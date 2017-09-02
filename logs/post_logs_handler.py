"""
POST logs handler.
"""
from datetime import datetime
import json
from elasticsearch import helpers

from logs.abstract_handler import AbstractLogsHandler


# a class is supposed to contain at least more than one public method;
# we separated the post method from the get in order to keep small files
# pylint: disable=too-few-public-methods
#
# the arguments differ from the initial Tornado method signature
# (def post(self))
# pylint: disable=arguments-differ
class PostLogsHandler(AbstractLogsHandler):
    """
    Post logs handler.
    """

    # the arguments differ from the initial Tornado method signature
    # (def post(self))
    # pylint: disable=arguments-differ
    def post(
            self,
            service_id,
    ):
        """
        Post /logs action.
        """
        logs = json.loads(self.request.body.decode("utf-8"))["logs"]

        # TODO: #59 the index name is created using the first log
        # date and time; we should create many indices
        # if logs dates have different days but this should not happen
        date = datetime.utcfromtimestamp(float(logs[0]["date"]))
        index = date.strftime("data-{}-%Y-%m-%d".format(service_id))

        for log in logs:
            log.update(
                {
                    "_type": "logs",
                    "service_id": service_id,
                }
            )
            log["_index"] = index
            log["date"] = datetime.utcfromtimestamp(float(log["date"]))

        helpers.bulk(
            self.es_client,
            logs,
            index=index,
        )
