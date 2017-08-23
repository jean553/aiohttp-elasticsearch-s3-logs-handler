# tornado-kibana-logs-handler

## Project overview and status

### Overview

This project shows a simple way to insert data into ElasticSearch through Tornado API.
The logs (data) are inserted into ElasticSearch and can be uploaded to a S3 bucket.

Four containers are included into the project:
* a Python development container with the Tornado service code (including tests),
* an ElasticSearch container,
* a Kibana container linked to the ES container (for tests purposes),
* a fake S3 container for data upload from ES

### Status

The project works with both local and remote S3.

#### Error when creating a repository with a local S3

The repository creation and the snapshots work, but the following error is returned:

```bash
curl -XPUT 'http://elasticsearch:9200/_snapshot/repository' -d '
{
    "type": "s3",
    "settings": {
        "bucket": "backups",
        "endpoint": "s3:5000",
        "protocol": "http",
        "access_key": "dummy",
        "secret_key":"dummy",
        "base_path": "backups"
    }
}
'

{"error":{"root_cause":[{"type":"repository_exception","reason":"[repository] failed to update snapshot in repository"}],"type":"repository_exception","reason":"[repository] failed to update snapsh
ot in repository","caused_by":{"type":"i_o_exception","reason":"com.amazonaws.services.s3.model.AmazonS3Exception: The specified key does not exist (Service: Amazon S3; Status Code: 404; Error Code
: NoSuchKey; Request ID: 1), S3 Extended Request ID: null","caused_by":{"type":"amazon_s3_exception","reason":"The specified key does not exist (Service: Amazon S3; Status Code: 404; Error Code: No
SuchKey; Request ID: 1)"}}},"status":500}%
```

It would be better to use `ES Curator` instead of basic HTTP requests.

## Start the container

```bash
vagrant up
```

## Connect to the service

```bash
vagrant ssh
```

## Starts the service

```bash
python -m "logs"
```

## Tests

```bash
py.test
```

## POST /logs

```bash
curl http://localhost:8000/api/1/service/1/logs \
    -X POST \
    -d '{"logs": [{"message": "log message", "level": "low", "category": "my category", "date": "1502304972"}]}' \
    -H 'Content-Type: application/json'
```

## GET /logs

```bash
curl http://localhost:8000/api/1/service/1/logs/2017-10-15-20-00-00/2017-10-16-15-00-00
```

## Connect to Kibana

In your browser:

```
http://kibana-container-ip-address:5601
```

This IP address can be found using `docker inspect tornado-kibana-logs-handler_kibana`.
The index pattern is `data-*`.

## Install S3 Plugin on Elasticsearch

TODO: #26 get rid of S3 plugin manual installation, this should be done automatically

```bash
docker exec -it tornado-kibana-logs-handler_elasticsearch /bin/bash
bin/elasticsearch-plugin install repository-s3
```

The ES container must be restarted.

## Create repository

```bash
./build_scripts/scripts/create_repository.sh
```

## Snapshot to S3

```bash
./build_scripts/scripts/make_snapshot.sh
```
