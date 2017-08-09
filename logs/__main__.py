"""Main module
"""
import tornado
from elasticsearch import Elasticsearch

from logs.post_logs_handler import PostLogsHandler

def main():
    """starts the tornado server
    """
    es_client = Elasticsearch(hosts=['elasticsearch'],)

    context = {
        'es_client': es_client,
    }

    app = tornado.web.Application(
        [
            (r"/api/1/logs", PostLogsHandler, context)
        ]
    )
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
