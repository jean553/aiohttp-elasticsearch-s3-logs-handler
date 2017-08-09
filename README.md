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
curl -X POST http://localhost:8000/api/1/logs
```
