'''
config.py

This module loads the configuration from environment variables.
It prevents the service from starting if required variables are not set.
'''
import os

ELASTICSEARCH_HOSTNAME = os.getenv('ELASTICSEARCH_HOSTNAME')
assert ELASTICSEARCH_HOSTNAME is not None, "ELASTICSEARCH_HOSTNAME must be set"

ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT')
assert ELASTICSEARCH_PORT is not None, "ELASTICSEARCH_PORT must be set"

AIOHTTP_PORT = int(os.getenv('AIOHTTP_PORT'))
assert AIOHTTP_PORT is not None, "AIOHTTP_PORT must be set"

S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
