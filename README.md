# tornado-kibana-logs-handler

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
