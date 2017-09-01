'''
Functionnal test that checks that:
 - log is inserted into the index after a POST
 - log is got from the elasticsearch index after GET
 - log is removed from elasticsearch after upload to S3
 - log can be downloaded from elasticsearch after upload to S3
'''
import requests

BASE_URL = 'http://localhost:8000/api/1/service/1'


def test_post_and_upload():
    '''
    Posts a log and tries to get it from elasticsearch,
    executes the upload script and tries to get it from S3
    '''
    pass
