#!/usr/bin/python
'''
Creates a snapshot of for one index.
'''
import os
import requests

import boto3

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

ELASTICSEARCH_ENDPOINT = 'http://elasticsearch:9200'
SNAPSHOTS_DIRECTORY = '/tmp/snapshots'


def get_data_indices():
    '''
    Returns the list of data indices (data-* format).

    Returns:
        (list): list of indices names
    '''
    indices = requests.get(ELASTICSEARCH_ENDPOINT + '/_aliases')
    return [
        index
        for index
        in indices.json()
        if index[:1] != '.'
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


def remove_index(index_name):
    '''
    Removes the given index from elasticsearch.

    Args:
        index_name(str): name of the index to remove
    '''
    pass


def main():
    '''
    Script entry point.
    '''

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        endpoint_url='http://{}'.format(S3_ENDPOINT),
    )
    s3_transfer = boto3.s3.transfer.S3Transfer(s3_client)

    indices = get_data_indices()

    for index in indices:
        generate_snapshot(index)
        upload_snapshot(
            s3_transfer,
            index,
        )
        remove_index(index)


if __name__ == '__main__':
    main()
