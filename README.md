# aiohttp-elasticsearch-s3-logs-handler

This project implements an asynchronous, non-blocking logs handler using Elasticsearch for short-term storage and Amazon S3 for long-term storage.

## Project Overview

The main components of this project are:
- An Aiohttp API service for inserting and retrieving logs
- Elasticsearch for short-term log storage
- Amazon S3 for long-term log archival

## Getting Started

### Prerequisites

- Python 3.7+
- Docker and Docker Compose

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/aiohttp-elasticsearch-s3-logs-handler.git
   cd aiohttp-elasticsearch-s3-logs-handler
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start the services using Docker Compose:
   ```
   docker-compose up -d
   ```

4. Run the Aiohttp service:
   ```
   python -m logs
   ```

### Running Tests

To run the test suite:
