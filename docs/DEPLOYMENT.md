# Deployment Guide

## Docker Deployment

```bash
docker-compose up -d
```

This starts:
- MCP Server (port 8000)
- Backend API (port 8001)
- Frontend (port 3000)
- PostgreSQL (port 5432)
- Redis (port 6379)
- Prometheus (port 9090)
- Grafana (port 3001)

## Production Deployment

1. Set environment variables
2. Build frontend: `cd frontend && npm run build`
3. Run with production server: `uvicorn backend.main:app --host 0.0.0.0 --port 8001`

## Monitoring

- Prometheus for metrics collection
- Grafana dashboards for visualization
- Structured logging with Loguru
