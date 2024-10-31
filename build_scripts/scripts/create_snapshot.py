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
from boto3.s3.transfer import S3Transfer
import aiohttp

from elasticsearch import Elasticsearch

# Environment variables
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

# Optional: only required for development environment with fake S3 service
S3_ENDPOINT = os.getenv('S3_ENDPOINT')

# Constants
ELASTICSEARCH_ENDPOINT = 'http://{}:9200'.format(ELASTICSEARCH_HOSTNAME)
SNAPSHOTS_DIRECTORY = '/tmp'
SNAPSHOT_DAYS_FROM_NOW = 10
LOGS_FILES_OPEN_METHOD = 'w'
ELASTICSEARCH_REQUESTS_TIMEOUT_SECONDS = 10
ELASTICSEARCH_MAXIMUM_RESULTS_PER_PAGE = 10
ELASTICSEARCH_SEARCH_CONTEXT_LIFETIME = '1m'  # 1 minute


def _get_data_indices() -> list:
    '''
    Returns the list of data indices (data-* format) that are older than SNAPSHOT_DAYS_FROM_NOW.
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


def _get_log_to_string(log: Any) -> str:
    '''
    Returns a string representation of the given log.
    Convert single quotes to double quotes to match JSON format (required for streaming).
    '''
    return str(log['_source']).replace("'", '"') + '\n'


async def _get_logs_from_elasticsearch(index_name: str) -> dict:
    '''
    Retrieve the initial batch of logs for the given index from Elasticsearch.
    '''
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(ELASTICSEARCH_REQUESTS_TIMEOUT_SECONDS):
            async with session.get(
                'http://{}:{}/{}/_search?scroll={}'.format(
                    ELASTICSEARCH_HOSTNAME,
                    ELASTICSEARCH_PORT,
                    index_name,
                    ELASTICSEARCH_SEARCH_CONTEXT_LIFETIME,
                ),
                json={
                    'size': ELASTICSEARCH_MAXIMUM_RESULTS_PER_PAGE,
                }
            ) as response:
                return await response.json()


async def _scroll_logs_from_elasticsearch(scroll_id: str) -> dict:
    '''
    Scroll the next page of found results from Elasticsearch using the provided scroll_id.
    '''
    # TODO: #123 we use a new session for one request here;
    # if we try to use the same session as before,
    # then not all the logs are returned from ES;
    # we have to investigate how to organize the session(s) here
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(ELASTICSEARCH_REQUESTS_TIMEOUT_SECONDS):
            async with session.get(
                'http://{}:{}/_search/scroll'.format(
                    ELASTICSEARCH_HOSTNAME,
                    ELASTICSEARCH_PORT,
                ),
                json={
                    'scroll': ELASTICSEARCH_SEARCH_CONTEXT_LIFETIME,
                    'scroll_id': scroll_id
                }
            ) as response:
                return await response.json()


async def _generate_snapshot(index_name: str):
    '''
    Stream one index content from Elasticsearch and store it into a file for upload.
    '''
    result = await _get_logs_from_elasticsearch(index_name)

    scroll_id = result['_scroll_id']
    logs = result['hits']['hits']
    elasticsearch_logs_amount = len(logs)

    with open(
        '{}/{}'.format(
            SNAPSHOTS_DIRECTORY,
            index_name,
        ),
        LOGS_FILES_OPEN_METHOD,
    ) as logs_file:
        # Write initial batch of logs
        for log in logs:
            logs_file.write(_get_log_to_string(log))

        # Continue scrolling and writing logs until no more results
        while elasticsearch_logs_amount > 0:
            result = await _scroll_logs_from_elasticsearch(scroll_id)

            scroll_id = result['_scroll_id']
            logs = result['hits']['hits']

            for log in logs:
                logs_file.write(_get_log_to_string(log))

            elasticsearch_logs_amount = len(logs)


def _handle_snapshot(
    s3_transfer: S3Transfer,
    index_name: str,
):
    '''
    Uploads the dump for the given index into S3 and removes the local logs file.
    '''
    file_path = SNAPSHOTS_DIRECTORY + '/' + index_name

    # Upload file to S3
    s3_transfer.upload_file(
        file_path,
        S3_BUCKET_NAME,
        index_name,
    )

    # Remove local file after successful upload
    os.remove(file_path)


def _remove_index(
    es_client: Elasticsearch,
    index_name: str,
):
    '''
    Removes the given index from Elasticsearch.

    Args:
        es_client(elasticsearch.client.Elasticsearch)
        index_name(str): name of the index to remove
    '''
    es_client.delete_by_query(
        index=index_name,
        body={},
    )


async def _run():
    '''
    Main asynchronous function to orchestrate the snapshot creation process.
    '''
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        # the custom endpoint is only required on dev environment
        endpoint_url='http://{}'.format(S3_ENDPOINT) if S3_ENDPOINT else None,
    )
    s3_transfer = S3Transfer(s3_client)

    # Initialize Elasticsearch client
    es_client = Elasticsearch([ELASTICSEARCH_HOSTNAME])

    # Get list of indices to process
    indices = _get_data_indices()

    # Process each index
    for index in indices:
        # Generate snapshot file
        await _generate_snapshot(index)
        # Upload snapshot to S3
        _handle_snapshot(
            s3_transfer,
            index,
        )
        # Remove index from Elasticsearch
        _remove_index(
            es_client,
            index,
        )


def main():
    '''
    Script entry point. Sets up and runs the asynchronous event loop.
    '''
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run())
    loop.close()


if __name__ == '__main__':
    main()
