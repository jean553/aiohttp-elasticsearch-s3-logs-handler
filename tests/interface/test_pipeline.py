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
import boto3

from elasticsearch import Elasticsearch

from elasticsearch_client import remove_all_data_indices

WAIT_TIME = 1
SERVICE_ID = '1'
BASE_URL = 'http://localhost:8000/api/1/service/' + SERVICE_ID
SNAPSHOT_COMMAND = 'python /vagrant/build_scripts/scripts/create_snapshot.py'

ELASTICSEARCH_HOSTNAME = os.getenv('ELASTICSEARCH_HOSTNAME')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')


def _execute_snapshot_script():
    '''
    Executes the snapshot script
    '''
    os.system(SNAPSHOT_COMMAND)


def _empty_s3_bucket():
    '''
    Empty the bucket
    '''
    resource = boto3.resource(
        service_name='s3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        endpoint_url='http://%s' % S3_ENDPOINT,
    )
    bucket = resource.Bucket(S3_BUCKET_NAME)
    bucket.objects.all().delete()


def test_post_and_upload():
    '''
    Posts a log and tries to get it from elasticsearch,
    executes the upload script and tries to get it from S3
    '''
    _empty_s3_bucket()

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

    index = log_datetime.strftime('data-{}-%Y-%m-%d'.format(SERVICE_ID))

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

    _execute_snapshot_script()

    response = requests.get(
        'http://{}/{}/{}'.format(
            S3_ENDPOINT,
            S3_BUCKET_NAME,
            index,
        )
    )
    assert response.status_code == 200
    time.sleep(WAIT_TIME)

    result = es_client.search(
        index=index,
        body={
            'query': {
                'bool': {
                    'must': {
                        'match': {
                            'service_id': '1'
                        },
                        'match': {
                            'date': datetime.fromtimestamp(log_timestamp)
                        }
                    },
                }
            }
        }
    )

    # check the index has been deleted from elasticsearch
    logs_amount = result['hits']['total']
    assert logs_amount == 0, \
        'unexpected logs amount, got %s, expected 0' % logs_amount


def test_two_posts_at_different_times_should_only_update_one_to_s3():
    '''
    Verifies that when two logs are sent into two different indices,
    very different in time, only one log is sent to S3 at a time.
    '''
    _empty_s3_bucket()

    es_client = Elasticsearch([ELASTICSEARCH_HOSTNAME])
    remove_all_data_indices(es_client)
    time.sleep(WAIT_TIME)

    # send the first log on August 9, 2017 06:56:12 pm

    first_log_message = 'a first log message'
    first_log_level = 'a low level'
    first_log_category = 'a first category'

    first_log_timestamp = 1502304972
    first_log_datetime = datetime.utcfromtimestamp(first_log_timestamp)
    first_index = 'data-%s-%04d-%02d-%02d' % (
        SERVICE_ID,
        first_log_datetime.year,
        first_log_datetime.month,
        first_log_datetime.day,
    )

    first_json = {
        'logs': [
            {
                'message': first_log_message,
                'level': first_log_level,
                'category': first_log_category,
                'date': str(first_log_timestamp),
            }
        ]
    }

    response = requests.post(
        BASE_URL + '/logs',
        json=first_json,
    )
    assert response.status_code == 200
    time.sleep(WAIT_TIME)

    # send the second log at the current date
    # (in order to be ignored by the snapshot script)

    second_log_message = 'a second log message'
    second_log_level = 'a low level'
    second_log_category = 'a second category'

    second_log_datetime = datetime.now()
    second_log_timestamp = second_log_datetime.timestamp()
    second_index = 'data-%s-%04d-%02d-%02d' % (
        SERVICE_ID,
        second_log_datetime.year,
        second_log_datetime.month,
        second_log_datetime.day,
    )

    second_json = {
        'logs': [
            {
                'message': second_log_message,
                'level': second_log_level,
                'category': second_log_category,
                'date': str(second_log_timestamp),
            }
        ]
    }

    response = requests.post(
        BASE_URL + '/logs',
        json=second_json,
    )
    assert response.status_code == 200
    time.sleep(WAIT_TIME)

    # check there is two indices into ES

    result = es_client.search(
        index='data-1-2017-08-09',
        body={}
    )

    logs_amount = result['hits']['total']
    assert logs_amount == 1, \
        'unexpected logs amount, got %s, expected 1' % logs_amount

    result = es_client.search(
        index='data-1-%04d-%02d-%02d' % (
            second_log_datetime.year,
            second_log_datetime.month,
            second_log_datetime.day,
        ),
        body={}
    )

    logs_amount = result['hits']['total']
    assert logs_amount == 1, \
        'unexpected logs amount, got %s, expected 1' % logs_amount

    # verifies the two logs are into elasticsearch

    response = requests.get(
        '%s/logs/2017-08-09-00-00-00/%04d-%02d-%02d-%02d-%02d-%02d' % (
            BASE_URL,
            second_log_datetime.year,
            second_log_datetime.month,
            second_log_datetime.day,
            second_log_datetime.hour,
            second_log_datetime.minute,
            second_log_datetime.second,
        ),
    )
    assert response.status_code == 200
    assert len(response.json()['logs']) == 2

    # verifies that only one log remains into elasticsearch after snapshot

    _execute_snapshot_script()
    time.sleep(WAIT_TIME)

    # the first index is supposed to be in S3

    response = requests.get(
        'http://{}/{}/{}'.format(
            S3_ENDPOINT,
            S3_BUCKET_NAME,
            first_index,
        )
    )
    assert response.status_code == 200

    # the second index is not supposed to be in S3

    response = requests.get(
        'http://{}/{}/{}'.format(
            S3_ENDPOINT,
            S3_BUCKET_NAME,
            second_index,
        )
    )
    assert response.status_code == 404

    # check there is only one index remaining into ES

    result = es_client.search(
        index='data-1-2017-08-09',
        body={}
    )

    logs_amount = result['hits']['total']
    assert logs_amount == 0, \
        'unexpected logs amount, got %s, expected 0' % logs_amount

    result = es_client.search(
        index='data-1-%04d-%02d-%02d' % (
            second_log_datetime.year,
            second_log_datetime.month,
            second_log_datetime.day,
        ),
        body={}
    )

    logs_amount = result['hits']['total']
    assert logs_amount == 1, \
        'unexpected logs amount, got %s, expected 1' % logs_amount

    # verifies the GET API still returns two logs

    response = requests.get(
        '%s/logs/2017-08-09-00-00-00/%04d-%02d-%02d-%02d-%02d-%02d' % (
            BASE_URL,
            second_log_datetime.year,
            second_log_datetime.month,
            second_log_datetime.day,
            second_log_datetime.hour,
            second_log_datetime.minute,
            second_log_datetime.second,
        ),
    )
    assert response.status_code == 200
    assert len(response.json()['logs']) == 2


def test_get_different_minute_from_identical_index_from_es():
    '''
    Posts one log and tries to get it using a range including the log minute,
    tries again with a range excluding the log minute
    '''
    _empty_s3_bucket()

    es_client = Elasticsearch([ELASTICSEARCH_HOSTNAME])
    remove_all_data_indices(es_client)
    time.sleep(WAIT_TIME)

    # send the first log on August 9, 2017 06:56:12 pm

    first_log_message = 'a first log message'
    first_log_level = 'a low level'
    first_log_category = 'a first category'
    first_log_timestamp = 1502304972

    first_json = {
        'logs': [
            {
                'message': first_log_message,
                'level': first_log_level,
                'category': first_log_category,
                'date': str(first_log_timestamp),
            }
        ]
    }

    response = requests.post(
        BASE_URL + '/logs',
        json=first_json,
    )
    assert response.status_code == 200
    time.sleep(WAIT_TIME)

    # verifies the log is found if the GET range includes the log minute

    response = requests.get(
        '%s/logs/2017-08-09-18-56-10/2017-08-09-18-56-15' % BASE_URL,
    )
    assert response.status_code == 200
    assert len(response.json()['logs']) == 1

    # verifies the log is not found if the GET range excludes the log minute

    response = requests.get(
        '%s/logs/2017-08-09-18-56-20/2017-08-09-18-56-25' % BASE_URL,
    )
    assert response.status_code == 200
    assert len(response.json()['logs']) == 0

    response = requests.get(
        '%s/logs/2017-08-09-18-56-05/2017-08-09-18-56-10' % BASE_URL,
    )
    assert response.status_code == 200
    assert len(response.json()['logs']) == 0


def test_get_different_hour_from_identical_index_from_es():
    '''
    Posts one log and tries to get it using a range including the log hour,
    tries again with a range excluding the log hour
    '''
    _empty_s3_bucket()

    es_client = Elasticsearch([ELASTICSEARCH_HOSTNAME])
    remove_all_data_indices(es_client)
    time.sleep(WAIT_TIME)

    # send the first log on August 9, 2017 06:56:12 pm

    first_log_message = 'a first log message'
    first_log_level = 'a low level'
    first_log_category = 'a first category'
    first_log_timestamp = 1502304972

    first_json = {
        'logs': [
            {
                'message': first_log_message,
                'level': first_log_level,
                'category': first_log_category,
                'date': str(first_log_timestamp),
            }
        ]
    }

    response = requests.post(
        BASE_URL + '/logs',
        json=first_json,
    )
    assert response.status_code == 200
    time.sleep(WAIT_TIME)

    # verifies the log is found if the GET range includes the log hour

    response = requests.get(
        '%s/logs/2017-08-09-17-30-00/2017-08-09-19-30-00' % BASE_URL,
    )
    assert response.status_code == 200
    assert len(response.json()['logs']) == 1

    # verifies the log is not found if the GET range excludes the log hour

    response = requests.get(
        '%s/logs/2017-08-09-16-30-00/2017-08-09-17-30-00' % BASE_URL,
    )
    assert response.status_code == 200
    assert len(response.json()['logs']) == 0

    response = requests.get(
        '%s/logs/2017-08-09-19-30-00/2017-08-09-20-30-00' % BASE_URL,
    )
    assert response.status_code == 200
    assert len(response.json()['logs']) == 0
