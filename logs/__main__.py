"""Main module
"""
import tornado
from elasticsearch import Elasticsearch

from logs.post_logs_handler import PostLogsHandler
from logs.get_logs_handler import GetLogsHandler

def main():
    """starts the tornado server
    """
    es_client = Elasticsearch(hosts=['elasticsearch'],)

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
