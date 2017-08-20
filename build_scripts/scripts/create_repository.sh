#!/bin/bash
curl -XPUT 'http://elasticsearch:9200/_snapshot/backups' -d '
{
  "type": "s3",
  "settings": {
    "bucket": "backups",
    "protocol": "http",
    "endpoint": "s3:5000",
    "access_key": "dummy",
    "secret_key": "dummy"
  }
}
'
