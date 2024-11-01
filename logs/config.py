'''
This module manages the configuration for the logs service.
It loads environment variables for Elasticsearch, aiohttp, and S3 settings.
The module also includes assertions to ensure all required variables are set,
preventing the service from starting with incomplete configuration.
Loads the configuration from the environment variable,
prevents the service to start if the variable cannot be found
'''
import os

ELASTICSEARCH_HOSTNAME = os.getenv('ELASTICSEARCH_HOSTNAME')
assert ELASTICSEARCH_HOSTNAME is not None

ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT')
assert ELASTICSEARCH_PORT is not None

AIOHTTP_PORT = int(os.getenv('AIOHTTP_PORT'))
assert AIOHTTP_PORT is not None

S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
