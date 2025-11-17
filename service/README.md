# SQLLineage FastAPI Service

A RESTful API service for SQL lineage analysis, built on top of [SQLLineage](https://github.com/reata/sqllineage) and FastAPI.

## Features

- **Column-Level Lineage**: Extract column-to-column lineage relationships in JSON format
- **Table-Level Lineage**: Identify source and target tables from SQL queries
- **Multiple SQL Dialects**: Support for ANSI, Hive, SparkSQL, PostgreSQL, T-SQL, BigQuery, and more
- **OpenMetadata Integration**: Optional metadata resolution from OpenMetadata API
- **Rate Limiting**: Built-in rate limiting (100 requests/minute per IP)
- **Request Size Limits**: Handles SQL queries up to 50MB
- **Dockerized**: Ready-to-deploy Docker container with docker-compose
- **Swagger UI**: Interactive API documentation at `/docs`
- **Comprehensive Tests**: Unit and integration tests included

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) OpenMetadata instance for metadata resolution

### Deployment with Docker Compose

1. **Clone the repository**:
   ```bash
   cd sqllineage/service
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start the service**:
   ```bash
   docker-compose up -d
   ```

4. **Verify the service is running**:
   ```bash
   curl http://localhost:8000/health
   ```

5. **Access Swagger UI**:
   Open your browser to `http://localhost:8000/docs`

## Configuration

### Environment Variables

Configure the service using environment variables in `.env` file:

```bash
# Service Configuration
SERVICE_PORT=8000              # Port to run the service on
LOG_LEVEL=INFO                 # Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_FORMAT=json                # Log format (json or text)

# OpenMetadata Integration
OPENMETADATA_URL=https://your-openmetadata-api/api/v1
OPENMETADATA_API_KEY=your-api-key-here
OPENMETADATA_TIMEOUT=10        # API timeout in seconds
OPENMETADATA_CACHE_TTL=300     # Cache TTL in seconds

# Request Limits
MAX_REQUEST_SIZE_MB=50         # Maximum SQL size per request
RATE_LIMIT_RPM=100            # Requests per minute per IP
REQUEST_TIMEOUT_SEC=30         # Request timeout

# SQL Configuration
DEFAULT_DIALECT=ansi           # Default SQL dialect
```

### Resource Limits

Adjust resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

## API Endpoints

### Health Check

```bash
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "openmetadata_configured": true
}
```

### Column Pairs Lineage

Extract column-level lineage as source-target pairs.

```bash
POST /api/v1/lineage/column-pairs
Content-Type: application/json

{
  "sql": "INSERT INTO target_table SELECT col1, col2 FROM source_table",
  "dialect": "ansi",
  "silent_mode": false,
  "openmetadata_enabled": true
}
```

**Response**:
```json
{
  "column_pairs": [
    {
      "target": "target_table.col1",
      "sources": ["source_table.col1"]
    },
    {
      "target": "target_table.col2",
      "sources": ["source_table.col2"]
    }
  ],
  "warnings": [],
  "metadata": {
    "processing_time_ms": 125.5,
    "dialect_used": "ansi",
    "statement_count": 1,
    "successful_statements": 1,
    "failed_statements": 0
  }
}
```

### Table Lineage

Extract table-level lineage.

```bash
POST /api/v1/lineage/table
Content-Type: application/json

{
  "sql": "INSERT INTO db1.target SELECT * FROM db2.source1 JOIN db3.source2",
  "dialect": "hive"
}
```

**Response**:
```json
{
  "source_tables": [
    {"schema": "db2", "table": "source1"},
    {"schema": "db3", "table": "source2"}
  ],
  "target_tables": [
    {"schema": "db1", "table": "target"}
  ],
  "warnings": [],
  "metadata": {
    "processing_time_ms": 98.2,
    "dialect_used": "hive",
    "statement_count": 1,
    "successful_statements": 1,
    "failed_statements": 0
  }
}
```

### Verbose Column Lineage

Get full column lineage paths showing transformation chains.

```bash
POST /api/v1/lineage/column
```

### Supported Dialects

Get list of supported SQL dialects.

```bash
GET /api/v1/dialects
```

**Response**:
```json
{
  "dialects": [
    "ansi", "athena", "bigquery", "databricks", "db2", "exasol",
    "hive", "mysql", "oracle", "postgres", "redshift", "snowflake",
    "sparksql", "sqlite", "teradata", "tsql", "vertica"
  ]
}
```

## Usage Examples

### Python

```python
import requests

url = "http://localhost:8000/api/v1/lineage/column-pairs"
payload = {
    "sql": """
        WITH user_orders AS (
            SELECT u.user_id, u.name, o.order_id, o.total
            FROM users u
            JOIN orders o ON u.user_id = o.user_id
        )
        INSERT INTO analytics.user_metrics
        SELECT user_id, name, COUNT(order_id), SUM(total)
        FROM user_orders
        GROUP BY user_id, name
    """,
    "dialect": "hive",
    "silent_mode": False,
    "openmetadata_enabled": True
}

response = requests.post(url, json=payload)
result = response.json()

for pair in result["column_pairs"]:
    print(f"{pair['target']} <- {', '.join(pair['sources'])}")
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/lineage/column-pairs" \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT col1, col2 FROM table1",
    "dialect": "ansi"
  }'
```

### Multiple Statements

The API supports multiple SQL statements separated by semicolons:

```python
payload = {
    "sql": """
        CREATE TABLE temp AS SELECT * FROM source;
        INSERT INTO target SELECT * FROM temp;
        DROP TABLE temp;
    """,
    "dialect": "ansi",
    "silent_mode": True
}
```

## OpenMetadata Integration

The service can fetch table metadata from OpenMetadata to improve lineage accuracy.

### Configuration

1. Set OpenMetadata environment variables:
   ```bash
   OPENMETADATA_URL=https://openmetadata.example.com/api/v1
   OPENMETADATA_API_KEY=your-jwt-token
   ```

2. Enable in requests:
   ```json
   {
     "sql": "...",
     "openmetadata_enabled": true
   }
   ```

### How It Works

- The service queries OpenMetadata API for table column information
- Results are cached for 5 minutes (configurable via `OPENMETADATA_CACHE_TTL`)
- Falls back to basic analysis if OpenMetadata is unavailable
- Supports custom FQN (Fully Qualified Name) patterns

## Rate Limiting

All API endpoints (except `/health`) are rate-limited to prevent abuse.

**Default Limit**: 100 requests per minute per IP address

**Response Headers**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when window resets

**429 Response** when limit exceeded:
```json
{
  "error": "Rate limit exceeded",
  "limit": 100,
  "window": "1 minute"
}
```

## Development

### Local Development Setup

1. **Install dependencies**:
   ```bash
   cd service
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   ```

3. **Run the service**:
   ```bash
   cd app
   python -m uvicorn main:app --reload --port 8000
   ```

4. **Access Swagger UI**:
   http://localhost:8000/docs

### Running Tests

```bash
# Unit tests
pytest tests/test_api.py -v

# Integration tests
pytest tests/test_integration.py -v

# All tests with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking
mypy app/
```

## Deployment

### Production Checklist

- [ ] Set strong `OPENMETADATA_API_KEY` if using OpenMetadata
- [ ] Configure appropriate `LOG_LEVEL` (INFO or WARNING for production)
- [ ] Set `LOG_FORMAT=json` for structured logging
- [ ] Adjust `RATE_LIMIT_RPM` based on expected traffic
- [ ] Configure resource limits in docker-compose.yml
- [ ] Set up log rotation for `/app/logs`
- [ ] Configure reverse proxy (nginx/Apache) if needed
- [ ] Set up monitoring and alerting
- [ ] Enable HTTPS with valid certificates

### Scaling

For high-traffic scenarios:

1. **Horizontal Scaling**: Run multiple containers behind a load balancer
2. **Resource Tuning**: Increase CPU/memory limits
3. **Rate Limiting**: Adjust `RATE_LIMIT_RPM` per instance
4. **Caching**: Increase `OPENMETADATA_CACHE_TTL` to reduce API calls

### Monitoring

Monitor these metrics:

- Request rate and response times (`X-Process-Time` header)
- Rate limit hit rate (429 responses)
- Error rates (4xx, 5xx responses)
- OpenMetadata API call success rate
- Memory usage and CPU utilization

Logs are written to:
- Console (stdout)
- File: `/app/logs/sqllineage-api.log` (with rotation)

## Troubleshooting

### Service won't start

1. Check logs:
   ```bash
   docker-compose logs sqllineage-api
   ```

2. Verify port availability:
   ```bash
   netstat -tuln | grep 8000
   ```

3. Check environment variables:
   ```bash
   docker-compose config
   ```

### OpenMetadata connection issues

1. Verify OpenMetadata URL is accessible:
   ```bash
   curl ${OPENMETADATA_URL}/system/status
   ```

2. Check API key validity
3. Review logs for OpenMetadata warnings
4. Disable OpenMetadata: set `OPENMETADATA_URL=` (empty)

### Rate limiting too strict

Adjust `RATE_LIMIT_RPM` in `.env`:
```bash
RATE_LIMIT_RPM=200
docker-compose restart
```

### Memory issues with large SQL

Increase memory limits in `docker-compose.yml`:
```yaml
memory: 4G  # Increase from 2G
```

## API Reference

Complete API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

This service is part of the SQLLineage project. See the main project LICENSE file.

## Support

For issues and questions:
- GitHub Issues: https://github.com/reata/sqllineage/issues
- Documentation: https://sqllineage.readthedocs.io/

## Changelog

### Version 1.0.0
- Initial release
- Column-pairs, table, and verbose column lineage endpoints
- OpenMetadata integration
- Rate limiting and request size validation
- Docker and docker-compose support
- Comprehensive test suite
