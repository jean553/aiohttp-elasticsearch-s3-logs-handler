'''
Handles GET /logs requests.
'''
import json
from datetime import datetime, timedelta
from typing import Any

import requests
import botocore
import aiobotocore

from aiohttp import web
from elasticsearch import Elasticsearch

from logs.config import S3_ENDPOINT
from logs.config import S3_BUCKET_NAME

DATE_FORMAT = '%Y-%m-%d-%H-%M-%S'
SNAPSHOT_DAYS_FROM_NOW = 10


def get_log_to_string(log: Any) -> str:
    '''
    Returns a string representation of the given log.
    Convert single quotes to double quotes in order to match with JSON format
    (required for streaming)
    '''
    return str(log['_source']).replace("'", '"')


async def get_logs(
    request: web.Request,
    es_client: Elasticsearch,
):
    '''
    Sends back logs according to the given dates range and service.
    '''
    service_id = request.match_info.get('id')
    start_date = request.match_info.get('start')
    end_date = request.match_info.get('end')

    start = datetime.strptime(
        start_date,
        DATE_FORMAT,
    )

    end = datetime.strptime(
        end_date,
        DATE_FORMAT,
    )

    result = es_client.search(
        index='data-{}-*'.format(service_id),
        body={
            'query': {
                'bool': {
                    'must': {
                        'match': {
                            'service_id': service_id
                        }
                    },
                    'filter': {
                        'range': {
                            'date': {
                                'gte': start,
                                'lte': end
                            }
                        }
                    }
                }
            }
        }
    )

    stream = web.StreamResponse()
    stream.content_type = 'application/json'

    await stream.prepare(request)

    stream.write(b'{"logs": [')

    logs = result['hits']['hits']
    elasticsearch_logs_amount = len(logs)
    last_elasticsearch_log_index = elasticsearch_logs_amount - 1
    first_iteration = True

    if elasticsearch_logs_amount > 0:
        first_iteration = False

    for counter, log in enumerate(logs):
        line = get_log_to_string(log)

        if counter != last_elasticsearch_log_index:
            line += ','

        stream.write(line.encode())

    now = datetime.now()
    last_snapshot_date = now - timedelta(days=SNAPSHOT_DAYS_FROM_NOW)
    if start <= last_snapshot_date:

        s3_index_date = start

        s3_session = aiobotocore.get_session()
        s3_client = s3_session.create_client(
            service_name='s3',
            region_name='',
            aws_secret_access_key='',
            aws_access_key_id='',
            endpoint_url='http://' + S3_ENDPOINT,
        )

        while s3_index_date <= last_snapshot_date:

            s3_index = 'data-%s-%04d-%02d-%02d' % (
                service_id,
                s3_index_date.year,
                s3_index_date.month,
                s3_index_date.day,
            )

            s3_index_date += timedelta(days=1)

            s3_response = None

            try:
                s3_response = await s3_client.get_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=s3_index,
                )
            except botocore.exceptions.ClientError:
                continue

            s3_stream = s3_response['Body']
            s3_line = await s3_stream.readline()

            while(len(s3_line) > 0):

                temp_line = s3_line.decode('utf-8')
                line = get_log_to_string(json.loads(temp_line))

                if not first_iteration:
                    line = ',' + line
                first_iteration = False

                stream.write(line.encode())

                s3_line = await s3_stream.readline()

            s3_stream.close()

    # TODO: #84 logs are only filtered by day,
    # filters must applied on hours, minutes, seconds

    # TODO: #89 replace single quotes by double quotes in order to
    # return a valid JSON to the client even if the response content-type
    # is not JSON
    stream.write(b']}')

    s3_client.close()

    return stream
