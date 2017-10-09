#!/usr/bin/python
'''
Creates a snapshot of for one index.
'''
import os
import requests
from datetime import datetime, timedelta
import async_timeout
import asyncio
from typing import Any

import boto3
import aiohttp

from elasticsearch import Elasticsearch

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
assert AWS_ACCESS_KEY is not None

AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
assert AWS_SECRET_KEY is not None

S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
assert S3_BUCKET_NAME is not None

ELASTICSEARCH_HOSTNAME = os.getenv('ELASTICSEARCH_HOSTNAME')
assert ELASTICSEARCH_HOSTNAME is not None

ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT')
assert ELASTICSEARCH_PORT is not None

S3_ENDPOINT = os.getenv('S3_ENDPOINT')

ELASTICSEARCH_ENDPOINT = 'http://{}:9200'.format(ELASTICSEARCH_HOSTNAME)
SNAPSHOTS_DIRECTORY = '/tmp'
SNAPSHOT_DAYS_FROM_NOW = 10

ELASTICSEARCH_REQUESTS_TIMEOUT_SECONDS = 10
ELASTICSEARCH_MAXIMUM_RESULTS_PER_PAGE = 10
ELASTICSEARCH_SEARCH_CONTEXT_LIFETIME = '1m'  # 1 minute


def get_data_indices():
    '''
    Returns the list of data indices (data-* format).

    Returns:
        (list): list of indices names
    '''
    now = datetime.now()
    snapshot_datetime = now - timedelta(days=SNAPSHOT_DAYS_FROM_NOW)

    indices = requests.get(ELASTICSEARCH_ENDPOINT + '/_aliases')
    return [
        index
        for index
        in indices.json()
        if (
            index[:1] != '.' and
            # takes only the date part of the index name,
            # turn it into a datetime object, compare interval with now
            datetime.strptime(
                '-'.join(index.split('-')[2:]),
                '%Y-%m-%d',
            ) <= snapshot_datetime
        )
    ]


def generate_snapshot(index_name):
    '''
    Generate the dump for the given index
    and stores it into the snapshots directory.

    Args:
        index_name(str): name of the index
    '''
    os.system(
        '''
        elasticdump \
            --input=%(elasticsearch_endpoint)s/%(index_name)s \
            --output=%(snapshots_directory)s/%(index_name)s \
            --type=data
        ''' % ({
            'index_name': index_name,
            'snapshots_directory': SNAPSHOTS_DIRECTORY,
            'elasticsearch_endpoint': ELASTICSEARCH_ENDPOINT,
        })
    )


def upload_snapshot(
    s3_transfer,
    index_name,
):
    '''
    Uploads the dump for the given index into S3.

    Args:
        s3_transfer(boto3.s3.transfer.S3Transfer)
        index_name(str): name of the index
    '''
    s3_transfer.upload_file(
        SNAPSHOTS_DIRECTORY + '/' + index_name,
        S3_BUCKET_NAME,
        index_name,
    )


def remove_index(
    es_client,
    index_name,
):
    '''
    Removes the given index from elasticsearch.

    Args:
        es_client(elasticsearch.client.Elasticsearch)
        index_name(str): name of the index to remove
    '''
    es_client.delete_by_query(
        index=index_name,
        body={},
    )


def main():
    '''
    Script entry point.
    '''

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        # the custom endpoint is only required on dev environment
        endpoint_url='http://{}'.format(S3_ENDPOINT) if S3_ENDPOINT else None,
    )
    s3_transfer = boto3.s3.transfer.S3Transfer(s3_client)

    es_client = Elasticsearch([ELASTICSEARCH_HOSTNAME])

    indices = get_data_indices()

    for index in indices:
        generate_snapshot(index)
        upload_snapshot(
            s3_transfer,
            index,
        )
        remove_index(
            es_client,
            index,
        )


if __name__ == '__main__':
    main()
