'''
Loads the configuration from the environment variable,
prevents the service to start if the variable cannot be found
'''
import os

ELASTICSEARCH_HOSTNAME = os.getenv('ELASTICSEARCH_HOSTNAME')
assert ELASTICSEARCH_HOSTNAME is not None

REGION_NAME = os.getenv('REGION_NAME')
assert REGION_NAME is not None

AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
assert AWS_SECRET_KEY is not None

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
assert AWS_ACCESS_KEY is not None
