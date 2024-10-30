#!/usr/bin/python
'''
This script creates a bucket in the S3 service (or a fake S3 service for development).
It's used to set up the storage environment for the logs service.
Creates a dummy bucket inside the S3 fake service.
'''

import os
import boto3


def generate_bucket():
    '''
    Generate the bucket according
    to the environment variables
    '''
    resource = boto3.resource(
        service_name='s3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        endpoint_url='http://%s' % os.getenv('S3_ENDPOINT'),
    )
    resource.create_bucket(Bucket=os.getenv('S3_BUCKET_NAME'))


def main():
    '''
    Script entry point
    '''
    generate_bucket()


if __name__ == '__main__':
    main()
