'''
Functionnal test that checks that:
 - log is inserted into the index after a POST
 - log is got from the elasticsearch index after GET
 - log is removed from elasticsearch after upload to S3
 - log can be downloaded from elasticsearch after upload to S3
'''
import os
import time
from datetime import datetime

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

    log_message = 'a first log message'
    log_level = 'a low level'
    log_category = 'a first category'

    # August 9, 2017 06:56:12 pm
    log_timestamp = 1502304972
    log_datetime = datetime.utcfromtimestamp(log_timestamp)
    log_date = log_datetime.strftime('%Y-%m-%dT%H:%M:%S')

    json = {
        'logs': [
            {
                'message': log_message,
                'level': log_level,
                'category': log_category,
                'date': str(log_timestamp),
            }
        ]
    }

    response = requests.post(
        BASE_URL + '/logs',
        json=json,
    )
    assert response.status_code == 200
    time.sleep(WAIT_TIME)

    response = requests.get(
        BASE_URL + '/logs/2017-08-09-00-00-00/2017-08-10-00-00-00',
    )
    assert response.status_code == 200
    assert len(response.json()['logs']) == 1

    log = response.json()['logs'][0]
    assert log['message'] == log_message
    assert log['level'] == log_level
    assert log['category'] == log_category
    assert log['date'] == log_date

    # force upload script execution
    os.system('python /vagrant/build_scripts/scripts/create_snapshot.py')
