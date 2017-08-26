"""
GET logs handler.
"""
from datetime import datetime

from logs.abstract_handler import AbstractLogsHandler

DATE_FORMAT = "%Y-%m-%d-%H-%M-%S"


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

        self.write({"logs": logs_without_metadata})
