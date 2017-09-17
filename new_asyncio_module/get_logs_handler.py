'''
Handles GET /logs requests.
'''

from aiohttp import web


def get_logs(request: web.Request):
    '''
    Sends back logs according to the given dates range and service.
    '''
    return web.Response(text='{}')
