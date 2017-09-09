'''
Abstract logs handler.
'''
import tornado.web


# the arguments differ from the initial Tornado method signature
# (def initialize(self))
# pylint: disable=arguments-differ
class AbstractLogsHandler(tornado.web.RequestHandler):
    '''
    Abstract logs handler.
    '''

    def initialize(
        self,
        es_client,
        s3_client,
    ):
        '''
        Initializes the received request handling process.
        '''
        self.es_client = es_client
        self.s3_client = s3_client

    def data_received(
        self,
        data,
    ):
        '''
        Used to handle streamed request data.
        Useless for us but must be implemented
        as required by the parent Tornado class.
        '''
        pass
