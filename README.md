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

## Create the service

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

## Loading tests

```bash
locust --host=http://localhost:8000
```

Connect to the web interface on port 8089.

This is better to run the Locust client on a separated machine.

## Pylint

```bash
pylint logs/
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

## Snapshot to JSON file using Elasticdump

```bash
elasticdump \
    --input=http://elasticsearch:9200/data-1-20-17-08-01 \
    --output=result.json \
    --type=data
```

## Performance tests

This test performs a lot of POST requests for many logs from many TSV files.

```bash
python tests/performance/performance_test.py
```

## Launch service into AWS Cloud

You must have an IAM user with the following permissions:
 * `AmazonEC2FullAccess`,
 * `AmazonS3FullAccess`

Furthermore, you have to create a key pair file, and using the name as `key_name` below.

The following commands have to be executed into the build scripts folder:

```bash
cd build_scripts
```

### Create the required AMI with Packer

Packer must be installed on your machine
(https://www.packer.io/downloads.html).

```bash
packer build \
    -var 'access_key=ACCESS_KEY' \
    -var 'secret_key=SECRET_KEY' \
    -var 'region=REGION' \
    packer.json
```

### Create the infrastructure with Terraform

```bash
terraform init

terraform plan \
    -var 'access_key=ACCESS_KEY' \
    -var 'secret_key=SECRET_KEY' \
    -var 'region=REGION' \
    -var 'service_ami_id=SERVICE_AMI_ID' \
    -var 'key_name=SSH_KEY_NAME'

terraform apply \
    -var 'access_key=ACCESS_KEY' \
    -var 'secret_key=SECRET_KEY' \
    -var 'region=REGION' \
    -var 'service_ami_id=SERVICE_AMI_ID' \
    -var 'key_name=SSH_KEY_NAME'
```
