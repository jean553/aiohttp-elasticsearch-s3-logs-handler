#!/bin/bash
curl -XPUT 'http://elasticsearch:9200/_snapshot/s3-backup' -d '
{
  "type": "fs",
  "settings": {
    "location": "/tmp"
  }
}
'
