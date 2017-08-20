#!/bin/bash
curl -XPUT 'http://elasticsearch:9200/_snapshot/backups/snapshot?wait_for_completion=true'
