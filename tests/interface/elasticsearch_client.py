'''
This file contains utility functions for interacting with Elasticsearch
in the context of testing the logs service.
Elasticsearch client routines for tests
'''

from elasticsearch.client import Elasticsearch


def remove_all_data_indices(es_client: Elasticsearch):
    '''
    Removes all the data-* indices.
    '''
    es_client.delete_by_query(
        index='data-*',
        body={},
    )
    es_client.indices.delete(index='data-*')
