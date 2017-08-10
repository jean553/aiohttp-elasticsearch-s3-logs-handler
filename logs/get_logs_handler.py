"""GET logs handler
"""
from datetime import datetime
import json
import tornado.web
from elasticsearch import helpers

class GetLogsHandler(tornado.web.RequestHandler):
    """Get logs handler.
    """

    def initialize(
        self,
        es_client,
    ):
        """Initializes the received request handling process.
        """
        self.es_client = es_client

    def get(
        self,
        service_id,
        start_date,
        end_date,
    ):
        """Get /logs action.
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

        # TODO: we simply build one index using the start date information;
        # this will be modified according our decision regarding data sharding
        search_index = "data-%s-%d-%02d-%02d" % (
            service_id,
            start.year,
            start.month,
            start.day,
        )

        result = self.es_client.search(
            index=search_index,
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
        last_log_index = len(logs) - 1

        response = '{"logs": ['
        for counter, log in enumerate(logs):
            response += str(log["_source"])
            if counter != last_log_index:
                response += ","
        response += "]}"

        self.write(response)
