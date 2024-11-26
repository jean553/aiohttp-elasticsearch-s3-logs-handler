'''
Handles GET /logs requests.
This module contains the handler for retrieving logs from ElasticSearch and S3.
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
ELASTICSEARCH_MAXIMUM_RESULTS_PER_PAGE = 10
ELASTICSEARCH_SEARCH_CONTEXT_LIFETIME = '1m'  # 1 minute


def _get_log_to_string(log_entry: Any) -> str:
    '''
    Returns a string representation of the given log.
    Convert single quotes to double quotes in order to match with JSON format
    (required for streaming)
    '''
    return str(log_entry['_source']).replace("'", '"')


async def _get_logs_from_elasticsearch(
    service_id: int,
    start_date: str,
    end_date: str,
) -> dict:
    '''
    Coroutine that returns the first page of logs from ES.
    '''
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(ELASTICSEARCH_REQUESTS_TIMEOUT_SECONDS):
            async with session.get(
                'http://{}:{}/data-{}-*/_search?scroll={}'.format(
                    ELASTICSEARCH_HOSTNAME,
                    ELASTICSEARCH_PORT,
                    service_id,
                    ELASTICSEARCH_SEARCH_CONTEXT_LIFETIME,
                ),
                json={
                    'size': ELASTICSEARCH_MAXIMUM_RESULTS_PER_PAGE,
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
                return await response.json()


async def _scroll_logs_from_elasticsearch(
    service_id: int,
    scroll_id: str,
) -> dict:
    '''
    Scroll the next page of found results from Elasticsearch.
    '''
    # TODO: #123 we use a new session for one request here;
    # if we try to use the same session as before,
    # then not all the logs are returned from ES;
    # we have to investigate how to organize the session(s) here
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(ELASTICSEARCH_REQUESTS_TIMEOUT_SECONDS):
            async with session.get(
                'http://{}:{}/_search/scroll'.format(
                    ELASTICSEARCH_HOSTNAME,
                    ELASTICSEARCH_PORT,
                    service_id,
                ),
                json={
                    'scroll': ELASTICSEARCH_SEARCH_CONTEXT_LIFETIME,
                    'scroll_id': scroll_id
                }
            ) as response:
                return await response.json()


def _stream_logs_chunk(
    stream: aiohttp.web_response.StreamResponse,
    logs: list,
):
    '''
    Streams each log one by one to the client.
    '''
    last_log_index = len(logs) - 1

    for log_index, log_entry in enumerate(logs):
        log_line = _get_log_to_string(log_entry)

        if log_index != last_log_index:
            log_line += ','

        stream.write(log_line.encode())


async def get_logs(
    request: web.Request,
    es_client: Elasticsearch,
):
    '''
    Handler for GET /logs/{id}/{start}/{end} endpoint.
    Retrieves logs for a specific service within a given date range.
    Fetches logs from ElasticSearch and, if necessary, from S3 for older data.
    '''

    '''
    Sends back logs according to the given dates range and service.
    '''
    service_id = request.match_info.get('id')
    start_date_str = request.match_info.get('start')
    end_date_str = request.match_info.get('end')

    start_datetime = datetime.strptime(
        start_date_str,
        API_DATE_FORMAT,
    )

    end_datetime = datetime.strptime(
        end_date_str,
        API_DATE_FORMAT,
    )

    elasticsearch_result = await _get_logs_from_elasticsearch(
        service_id,
        start_date_str,
        end_date_str,
    )

    response_stream = web.StreamResponse()
    response_stream.content_type = 'application/json'
    await response_stream.prepare(request)
    response_stream.write(b'{"logs": [')

    scroll_id = elasticsearch_result['_scroll_id']
    elasticsearch_logs = elasticsearch_result['hits']['hits']
    elasticsearch_logs_count = len(elasticsearch_logs)

    first_iteration = elasticsearch_logs_count == 0
    first_elasticsearch_scroll = True

    while elasticsearch_logs_count > 0:

        if not first_elasticsearch_scroll:
            response_stream.write(b',')

        _stream_logs_chunk(
            response_stream,
            elasticsearch_logs,
        )

        elasticsearch_result = await _scroll_logs_from_elasticsearch(
            service_id,
            scroll_id,
        )

        scroll_id = elasticsearch_result['_scroll_id']
        elasticsearch_logs = elasticsearch_result['hits']['hits']
        elasticsearch_logs_count = len(elasticsearch_logs)

        first_elasticsearch_scroll = False

    current_datetime = datetime.now()
    last_snapshot_date = current_datetime - timedelta(days=SNAPSHOT_DAYS_FROM_NOW)
    if start_datetime <= last_snapshot_date:

        s3_index_date = start_datetime

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

                s3_line_decoded = s3_line.decode('utf-8')
                s3_log_entry = json.loads(s3_line_decoded)
                log_datetime = datetime.strptime(
                    s3_log_entry['date'],
                    '%Y-%m-%dT%H:%M:%S',
                )

                if log_datetime < start_datetime or log_datetime > end_datetime:
                    s3_line = await s3_stream.readline()
                    continue

                log_line = str(s3_log_entry).replace("'", '"')

                if not first_iteration:
                    log_line = ',' + log_line
                first_iteration = False

                response_stream.write(log_line.encode())

                s3_line = await s3_stream.readline()

            s3_stream.close()
        s3_client.close()

    response_stream.write(b']}')

    return response_stream
