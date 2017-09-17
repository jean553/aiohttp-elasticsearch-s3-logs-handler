'''
Handles POST /logs requests.
'''

from aiohttp import web


def post_logs(request: web.Request):
    '''
    Save sent logs into ElasticSearch.
    '''
    return web.Response(text='{}')
