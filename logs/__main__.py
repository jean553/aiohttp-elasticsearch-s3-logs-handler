"""Main module
"""
import tornado

from logs.post_logs_handler import PostLogsHandler

def main():
    """starts the tornado server
    """
    app = tornado.web.Application(
        [
            (r"/api/1/logs", PostLogsHandler)
        ]
    )
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
