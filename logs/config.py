'''
Loads the configuration from the environment variables,
with default values if the variables are not set
'''
import os

# Hostname of the Elasticsearch server
# Used to establish a connection to the Elasticsearch cluster
ELASTICSEARCH_HOSTNAME = os.getenv('ELASTICSEARCH_HOSTNAME', 'localhost')

# Port number for the Elasticsearch server
# Used in conjunction with the hostname to connect to Elasticsearch
ELASTICSEARCH_PORT = os.getenv('ELASTICSEARCH_PORT', '9200')

# Port number for the AIOHTTP server
# Defines on which port the AIOHTTP server will listen for incoming requests
AIOHTTP_PORT = int(os.getenv('AIOHTTP_PORT', '8000'))

# Endpoint URL for the S3-compatible object storage service
# Used to interact with the S3 bucket for storing or retrieving data
S3_ENDPOINT = os.getenv('S3_ENDPOINT', 'http://localhost:9000')

# Name of the S3 bucket to be used for storing data
# Specifies which bucket in the S3 storage will be accessed by the application
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'default-bucket')
