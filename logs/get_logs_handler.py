"""
GET logs handler.
"""
import json
from datetime import datetime, timedelta

import requests

from logs.abstract_handler import AbstractLogsHandler

from logs.config import S3_ENDPOINT
from logs.config import S3_BUCKET_NAME

DATE_FORMAT = "%Y-%m-%d-%H-%M-%S"
SNAPSHOT_DAYS_FROM_NOW = 10


# a class is supposed to contain at least more than one public method;
# we separated the post method from the get in order to keep small files
# pylint: disable=too-few-public-methods
#
# the arguments differ from the initial Tornado method signature
# (def get(self))
# pylint: disable=arguments-differ
class GetLogsHandler(AbstractLogsHandler):
    """
    Get logs handler.
    """

    def get(
            self,
            service_id,
            start_date,
            end_date,
    ):
        """
        Get /logs action.
        """
        start = datetime.strptime(
            start_date,
            DATE_FORMAT,
        )

        end = datetime.strptime(
            end_date,
            DATE_FORMAT,
        )

        result = self.es_client.search(
            index="data-{}-*".format(service_id),
            body={
                "query": {
                    "bool": {
                        "must": {
                            "match": {
                                "service_id": service_id
                            }
                        },
                        "filter": {
                            "range": {
                                "date": {
                                    "gte": start,
                                    "lte": end
                                }
                            }
                        }
                    }
                }
            }
        )

        logs = result["hits"]["hits"]
        logs_without_metadata = list()
        for log in logs:
            logs_without_metadata.append(log["_source"])

        now = datetime.now()
        last_snapshot_date = now - timedelta(days=SNAPSHOT_DAYS_FROM_NOW)
        if end > last_snapshot_date:

            # TODO: #80 this feature must be non-blocking asynchronous
            response = requests.get(
                'http://{}/{}/{}'.format(
                    S3_ENDPOINT,
                    S3_BUCKET_NAME,
                    # FIXME: #81 hard coded value only for tests purposes;
                    # every concerned indices must be requested
                    'data-1-2017-08-09',
                )
            )

            if response.status_code == 200:
                logs_without_metadata.append(
                    json.loads(response.text)["_source"]
                )

        self.write({"logs": logs_without_metadata})
