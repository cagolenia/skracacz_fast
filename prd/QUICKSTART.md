# Quick Start Guide

## Step-by-Step Setup

### 1. Start Infrastructure (PostgreSQL, Redis, RabbitMQ)
```powershell
docker-compose up -d postgres redis rabbitmq
```

### 2. Initialize Database
```powershell
.\init_database.ps1
```

### 3. Start Services (in separate terminals)

**Terminal 1 - Link Management:**
```powershell
.\run_link_management.ps1
```

**Terminal 2 - Redirection:**
```powershell
.\run_redirection.ps1
```

**Terminal 3 - Analytics:**
```powershell
.\run_analytics.ps1
```

**Terminal 4 - Analytics Worker (optional, for queue processing):**
```powershell
.\run_worker.ps1
```

## Access Points

- **Link Management API**: http://localhost:8001/docs
- **Redirection Service**: http://localhost:8002/{short_code}
- **Analytics API**: http://localhost:8003/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## Test the System

### 1. Create a short link:
```powershell
curl.exe -X POST "http://localhost:8001/api/v1/links" `
  -H "Content-Type: application/json" `
  -d '{\"long_url\": \"https://www.google.com\"}'
```

### 2. Visit the short link:
```powershell
curl.exe -L "http://localhost:8002/YOUR_SHORT_CODE"
```

### 3. Check analytics:
```powershell
curl.exe "http://localhost:8003/stats/YOUR_SHORT_CODE"
```

## Troubleshooting

- **Module not found errors**: Make sure you're using the virtual environment `.venv`
- **Database connection errors**: Ensure Docker containers are running with `docker ps`
- **Port already in use**: Change the port in the respective run script
- **Import errors**: Check that PYTHONPATH is set correctly in each terminal

## Stop All Services

```powershell
docker-compose down
```
