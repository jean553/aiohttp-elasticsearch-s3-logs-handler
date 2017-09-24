'''
Handles GET /logs requests.
'''
import json
import async_timeout
from datetime import datetime, timedelta
from typing import Any

import botocore
import aiobotocore

import aiohttp
from aiohttp import web
from elasticsearch import Elasticsearch

from logs.config import S3_ENDPOINT
from logs.config import S3_BUCKET_NAME
from logs.config import ELASTICSEARCH_HOSTNAME
from logs.config import ELASTICSEARCH_PORT

API_DATE_FORMAT = '%Y-%m-%d-%H-%M-%S'
ELASTICSEARCH_DATE_FORMAT = 'yyyy-MM-dd-HH-mm-ss'
SNAPSHOT_DAYS_FROM_NOW = 10
ELASTICSEARCH_REQUESTS_TIMEOUT_SECONDS = 10


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
        API_DATE_FORMAT,
    )

    end = datetime.strptime(
        end_date,
        API_DATE_FORMAT,
    )

    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(ELASTICSEARCH_REQUESTS_TIMEOUT_SECONDS):
            async with session.get(
                'http://{}:{}/data-{}-*/_search?scroll=2m'.format(
                    ELASTICSEARCH_HOSTNAME,
                    ELASTICSEARCH_PORT,
                    service_id,
                ),
                json={
                    'size': 10,
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
                                        'gte': start_date,
                                        'lte': end_date,
                                        'format': ELASTICSEARCH_DATE_FORMAT
                                    }
                                }
                            }
                        }
                    }
                }
            ) as response:
                result = await response.json()

    stream = web.StreamResponse()
    stream.content_type = 'application/json'
    await stream.prepare(request)
    stream.write(b'{"logs": [')

    scroll_id = result['_scroll_id']
    logs = result['hits']['hits']
    elasticsearch_logs_amount = len(logs)

    first_iteration = False if elasticsearch_logs_amount > 0 else True

    line = ''
    while elasticsearch_logs_amount > 0:

        for counter, log in enumerate(logs):
            line += get_log_to_string(log)

            if counter != elasticsearch_logs_amount - 1:
                line += ','

            stream.write(line.encode())

            line = ''

        # TODO: #119 Elasticsearch streaming should be non-blocking IO
        result = es_client.scroll(
            scroll_id=scroll_id,
            scroll='2m',
        )
        scroll_id = result['_scroll_id']
        logs = result['hits']['hits']
        elasticsearch_logs_amount = len(logs)

        if elasticsearch_logs_amount > 0:
            line = ','

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
                line_items = json.loads(temp_line)
                log_date = datetime.strptime(
                    line_items['_source']['date'],
                    '%Y-%m-%dT%H:%M:%S',
                )

                if log_date < start or log_date > end:
                    s3_line = await s3_stream.readline()
                    continue

                line = get_log_to_string(line_items)

                if not first_iteration:
                    line = ',' + line
                first_iteration = False

                stream.write(line.encode())

                s3_line = await s3_stream.readline()

            s3_stream.close()

    # TODO: #89 replace single quotes by double quotes in order to
    # return a valid JSON to the client even if the response content-type
    # is not JSON
    stream.write(b']}')

    s3_client.close()

    return stream
