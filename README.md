# aiohttp-elasticsearch-s3-logs-handler

Asynchronous non-blocking logs handler using Elasticsearch for short-term storage
and Amazon S3 for long-term storage.

![Image 1](resources/architecture.png)

## Project overview and status

### Overview

This project shows a simple way to insert data into Elasticsearch through Aiohttp API.
The logs (data) are inserted into Elasticsearch and can be uploaded to an S3 bucket.

Four containers are included in the project:
* a Python development container with the Aiohttp service code (including tests),
* an Elasticsearch container,
* a Kibana container linked to the ES container (for test purposes),
* a fake S3 container for data upload from ES

## Create the service

