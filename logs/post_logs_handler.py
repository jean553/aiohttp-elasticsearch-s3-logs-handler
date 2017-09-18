'''
Handles POST /logs requests.
'''
from datetime import datetime
from elasticsearch import Elasticsearch, helpers

from aiohttp import web

from logs.config import ELASTICSEARCH_HOSTNAME


async def post_logs(request: web.Request):
    '''
    Save sent logs into ElasticSearch.
    '''
    data = await request.json()
    logs = data['logs']

    service_id = request.match_info.get('id')

    # TODO: #59 the index name is created using the first log
    # date and time; we should create many indices
    # if logs dates have different days but this should not happen
    date = datetime.utcfromtimestamp(float(logs[0]['date']))
    index = date.strftime('data-{}-%Y-%m-%d'.format(service_id))

    for log in logs:
        log.update(
            {
                '_type': 'logs',
                'service_id': service_id,
            }
        )
        log['_index'] = index
        log['date'] = datetime.utcfromtimestamp(float(log['date']))

    # TODO: #104 the elasticsearch client must be created only once
    es_client = Elasticsearch(hosts=[ELASTICSEARCH_HOSTNAME],)

    helpers.bulk(
        es_client,
        logs,
        index=index,
    )

    return web.Response()
