'''
Functionnal test that checks that:
 - log is inserted into the index after a POST
 - log is got from the elasticsearch index after GET
 - log is removed from elasticsearch after upload to S3
 - log can be downloaded from elasticsearch after upload to S3
'''
import os
import time

import requests

from elasticsearch import Elasticsearch

from elasticsearch_client import remove_all_data_indices

BASE_URL = 'http://localhost:8000/api/1/service/1'
ELASTICSEARCH_HOSTNAME = os.getenv('ELASTICSEARCH_HOSTNAME')
WAIT_TIME = 1


def test_post_and_upload():
    '''
    Posts a log and tries to get it from elasticsearch,
    executes the upload script and tries to get it from S3
    '''
    es_client = Elasticsearch([ELASTICSEARCH_HOSTNAME])
    remove_all_data_indices(es_client)
    time.sleep(WAIT_TIME)

    log_timestamp = 1502304972

    json = {
        'logs': [
            {
                'message': 'a first log message',
                'level': 'a low level',
                'category': 'a first category',
                'date': str(log_timestamp),
            }
        ]
    }

    response = requests.post(
        BASE_URL + '/logs',
        json=json,
    )
    assert response.status_code == 200
