'''
GET logs handler.
'''
import json
from datetime import datetime, timedelta
from typing import Any

import requests

from logs.abstract_handler import AbstractLogsHandler

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


# a class is supposed to contain at least more than one public method;
# we separated the post method from the get in order to keep small files
# pylint: disable=too-few-public-methods
#
# the arguments differ from the initial Tornado method signature
# (def get(self))
# pylint: disable=arguments-differ
class GetLogsHandler(AbstractLogsHandler):
    '''
    Get logs handler.
    '''

    def get(
        self,
        service_id: str,
        start_date: str,
        end_date: str,
    ):
        '''
        Get /logs action.
        '''
        start = datetime.strptime(
            start_date,
            DATE_FORMAT,
        )

        end = datetime.strptime(
            end_date,
            DATE_FORMAT,
        )

        result = self.es_client.search(
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

        self.write('{"logs": [')

        logs = result['hits']['hits']
        last_elasticsearch_log_index = len(logs) - 1
        first_iteration = True

        if len(logs) > 0:
            first_iteration = False

        for counter, log in enumerate(logs):
            line = get_log_to_string(log)

            if counter != last_elasticsearch_log_index:
                line += ','

            self.write(line)
            self.flush()

        now = datetime.now()
        last_snapshot_date = now - timedelta(days=SNAPSHOT_DAYS_FROM_NOW)
        if start <= last_snapshot_date:

            s3_index_date = start

            while s3_index_date <= last_snapshot_date:

                s3_index = 'data-%s-%04d-%02d-%02d' % (
                    service_id,
                    s3_index_date.year,
                    s3_index_date.month,
                    s3_index_date.day,
                )

                # TODO: #80 this feature must be non-blocking asynchronous
                response = requests.get(
                    'http://{}/{}/{}'.format(
                        S3_ENDPOINT,
                        S3_BUCKET_NAME,
                        s3_index,
                    )
                )

                if response.status_code == 200:

                    line = ''
                    if not first_iteration:
                        line += ','
                        first_iteration = False

                    line += get_log_to_string(json.loads(response.text))
                    self.write(line)
                    self.flush()

                s3_index_date += timedelta(days=1)

        # TODO: #84 logs are only filtered by day,
        # filters must applied on hours, minutes, seconds

        # TODO: #89 replace single quotes by double quotes in order to
        # return a valid JSON to the client even if the response content-type
        # is not JSON
        self.write(']}')
