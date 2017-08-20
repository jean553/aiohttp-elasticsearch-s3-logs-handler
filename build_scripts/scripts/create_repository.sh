#!/bin/bash
curl -XPUT 'http://elasticsearch:9200/_snapshot/backups' -d '
{
  "type": "s3",
  "settings": {
    "bucket": "'$S3_BUCKET_NAME'",
    "access_key": "'$AWS_ACCESS_KEY'",
    "secret_key": "'$AWS_SECRET_KEY'"
  }
}
'
