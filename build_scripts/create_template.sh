#!/bin/bash
curl -XPUT 'http://elasticsearch:9200/_template/data-template?pretty' -d '
{
  "template": "data-*",
  "settings": {
    "number_of_shards": 1
  },
  "mappings": {
    "data": {
      "properties": {
        "service_id": {
          "type": "string"
        },
        "message": {
          "type": "string"
        },
        "category": {
          "type": "string"
        },
        "level": {
          "type": "string"
        },
        "date": {
          "type": "date"
        }
      }
    }
  }
}
'
