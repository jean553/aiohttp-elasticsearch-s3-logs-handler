"""
GET logs handler
"""
from datetime import datetime
import json
import tornado.web
from elasticsearch import helpers

class GetLogsHandler(tornado.web.RequestHandler):
    """
    Get logs handler.
    """

    def initialize(
        self,
        es_client,
    ):
        """
        Initializes the received request handling process.
        """
        self.es_client = es_client

    def get(
        self,
        service_id,
        start_date,
        end_date,
    ):
        """
        Get /logs action.
        """
        DATE_FORMAT = "%Y-%m-%d-%H-%M-%S"

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
