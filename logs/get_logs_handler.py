'''
GET logs handler.
'''
import json
from datetime import datetime, timedelta

import requests

from logs.abstract_handler import AbstractLogsHandler

from logs.config import S3_ENDPOINT
from logs.config import S3_BUCKET_NAME

DATE_FORMAT = '%Y-%m-%d-%H-%M-%S'
SNAPSHOT_DAYS_FROM_NOW = 10


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
        logs_without_metadata = list()

        for counter, log in enumerate(logs):
            line = str(log['_source']).replace("'", '"')

            if counter != last_elasticsearch_log_index:
                line += ','

            self.write(line)

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

                    print('----')
                    print(response.text)
                    print(json.loads(response.text)['_source'])

                    logs_without_metadata.append(
                        json.loads(response.text)['_source']
                    )

                s3_index_date += timedelta(days=1)

        # TODO: #83 result must be streamed to the client
        # TODO: #84 logs are only filtered by day,
        # filters must applied on hours, minutes, seconds

        # TODO: #89 replace single quotes by double quotes in order to
        # return a valid JSON to the client even if the response content-type
        # is not JSON
        #self.write(str(logs_without_metadata).replace("'", '"'))
        self.write(']}')
