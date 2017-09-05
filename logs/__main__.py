"""Main module
"""
import tornado
import aiobotocore
from elasticsearch import Elasticsearch

from logs.config import ELASTICSEARCH_HOSTNAME
from logs.config import REGION_NAME
from logs.config import AWS_SECRET_KEY
from logs.config import AWS_ACCESS_KEY

from logs.post_logs_handler import PostLogsHandler
from logs.get_logs_handler import GetLogsHandler


def main():
    """
    Starts the tornado server
    """
    es_client = Elasticsearch(hosts=[ELASTICSEARCH_HOSTNAME],)

    session = aiobotocore.get_session()
    s3_client = session.create_client(
        service_name='s3',
        region_name=REGION_NAME,
        aws_secret_access_key=AWS_SECRET_KEY,
        aws_access_key_id=AWS_ACCESS_KEY,
    )

    context = {
        'es_client': es_client,
    }

    app = tornado.web.Application(
        [
            (r"/api/1/service/(.*)/logs", PostLogsHandler, context),
            (r"/api/1/service/(.*)/logs/(.*)/(.*)", GetLogsHandler, context)
        ]
    )
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
