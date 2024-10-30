'''
This file contains utility functions for interacting with Elasticsearch
during interface tests, such as removing all data indices.
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
