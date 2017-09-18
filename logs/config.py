'''
Loads the configuration from the environment variable,
prevents the service to start if the variable cannot be found
'''
import os

ELASTICSEARCH_HOSTNAME = os.getenv('ELASTICSEARCH_HOSTNAME')
assert ELASTICSEARCH_HOSTNAME is not None

S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
