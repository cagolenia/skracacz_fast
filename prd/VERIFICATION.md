# 🧪 VERIFICATION GUIDE - Test Your Complete System

This guide helps you verify that everything works correctly.

## ✅ Step-by-Step Verification

### 1️⃣ Check Docker Infrastructure

```powershell
# Check if containers are running
docker ps

# You should see:
# - url_shortener_postgres
# - url_shortener_redis
# - url_shortener_rabbitmq
```

**Expected output**: 3 containers running

---

### 2️⃣ Verify Database

```powershell
# Check database connection and tables
docker exec url_shortener_postgres psql -U postgres -d url_shortener -c "\dt"

# Should show tables:
# - links
# - link_visits (after analytics starts)
```

**Expected output**: Tables listed

---

### 3️⃣ Test Link Management Service (Port 8001)

```powershell
# Health check
curl http://localhost:8001/health

# Create a link
curl -X POST "http://localhost:8001/api/v1/links" `
  -H "Content-Type: application/json" `
  -d '{\"long_url\": \"https://www.google.com\"}'

# List all links
curl http://localhost:8001/api/v1/links

# Open Swagger UI in browser
start http://localhost:8001/docs
```

**Expected**: 
- Health: `{"status": "healthy"}`
- Create returns short_code
- List shows created links

---

### 4️⃣ Test Redirection Service (Port 8002)

```powershell
# Replace YOUR_CODE with actual short_code from step 3
$code = "YOUR_CODE"

# Test redirect (should return 301)
curl -I "http://localhost:8002/$code"

# Or follow redirect
curl -L "http://localhost:8002/$code"

# Health check
curl http://localhost:8002/health
```

**Expected**:
- 301 redirect status
- Location header points to original URL

---

### 5️⃣ Test Analytics Service (Port 8003)

```powershell
# After visiting a link in step 4, check stats
# Wait 2-3 seconds for queue processing
Start-Sleep -Seconds 3

curl "http://localhost:8003/stats/$code"

# Get detailed visits
curl "http://localhost:8003/stats/$code/visits"

# Device statistics
curl "http://localhost:8003/stats/$code/devices"

# Global stats
curl "http://localhost:8003/stats"

# Open Swagger UI
start http://localhost:8003/docs
```

**Expected**:
- Stats show visit count
- Device type detected
- Timestamp recorded

---

### 6️⃣ Load Test Data

```powershell
cd C:\Users\Cezary\Documents\My\skracacz_fast
& ".\.venv\Scripts\python.exe" load_test_data.py
```

**Expected**:
- 15+ links created
- Results saved to test_data_links.json
- Examples displayed

---

### 7️⃣ Run Tests

```powershell
# Unit tests (Link Management)
cd C:\Users\Cezary\Documents\My\skracacz_fast\services\link_management
& "..\..\. venv\Scripts\pytest.exe" tests/ -v

# Integration tests (all services must be running)
cd C:\Users\Cezary\Documents\My\skracacz_fast\tests
& "..\. venv\Scripts\pytest.exe" test_integration.py -v -s
```

**Expected**:
- All unit tests pass (15+)
- Integration tests pass (if all services running)

---

### 8️⃣ Check RabbitMQ

```powershell
# Open RabbitMQ management interface
start http://localhost:15672

# Login: guest / guest

# Navigate to Queues tab
# Should see: link_visits queue
```

**Expected**:
- Queue exists
- Messages processed (Ready = 0 after processing)

---

### 9️⃣ Check Redis Cache

```powershell
# Connect to Redis
docker exec -it url_shortener_redis redis-cli

# In Redis CLI:
KEYS *
GET link:YOUR_CODE
EXIT
```

**Expected**:
- Keys show cached links
- GET returns long URL

---

### 🔟 Performance Test

```powershell
# Measure redirect time (first request - cache miss)
Measure-Command { curl -I "http://localhost:8002/$code" }

# Measure redirect time (second request - cache hit)
Measure-Command { curl -I "http://localhost:8002/$code" }
```

**Expected**:
- First request: ~50-100ms
- Second request: ~10-30ms (faster due to cache)

---

## 📋 VERIFICATION CHECKLIST

Use this checklist to verify all components:

```
Infrastructure:
[ ] PostgreSQL running (port 5432)
[ ] Redis running (port 6379)
[ ] RabbitMQ running (port 5672, 15672)
[ ] Docker network created

Services:
[ ] Link Management API responding (port 8001)
[ ] Redirection Service responding (port 8002)
[ ] Analytics API responding (port 8003)
[ ] Analytics Worker processing queue

Functionality:
[ ] Can create short links
[ ] Can retrieve link by code
[ ] Redirects work (301 status)
[ ] Cache improves performance
[ ] Analytics records visits
[ ] Device type detected
[ ] Duplicate URLs handled
[ ] Custom aliases work
[ ] Invalid URLs rejected
[ ] 404 for non-existent codes

Tests:
[ ] Unit tests pass
[ ] Integration tests pass (with services running)
[ ] Test data loads successfully

Documentation:
[ ] README.md exists and is clear
[ ] QUICKSTART.md provides simple steps
[ ] API docs accessible (/docs endpoints)
[ ] All scripts work
```

---

## 🐛 TROUBLESHOOTING

### Problem: "Connection refused"

**Solution:**
```powershell
# Check if service is running
netstat -an | findstr "8001"  # for Link Management
netstat -an | findstr "8002"  # for Redirection
netstat -an | findstr "8003"  # for Analytics

# Start the service if not running
```

### Problem: "Module not found"

**Solution:**
```powershell
# Ensure you're using the virtual environment
C:\Users\Cezary\Documents\My\skracacz_fast\.venv\Scripts\activate

# Or use absolute path to uvicorn
```

### Problem: "Database connection error"

**Solution:**
```powershell
# Check PostgreSQL is running
docker ps | findstr postgres

# Restart if needed
docker restart url_shortener_postgres

# Check connection
docker exec url_shortener_postgres pg_isready
```

### Problem: "No analytics data"

**Solution:**
```powershell
# Ensure Analytics Worker is running
cd services\analytics
python src\worker.py

# Check RabbitMQ queue
# Visit: http://localhost:15672
```

### Problem: "Cache not working"

**Solution:**
```powershell
# Check Redis is running
docker exec url_shortener_redis redis-cli PING
# Should return: PONG

# Restart Redis if needed
docker restart url_shortener_redis
```

---

## 🎯 QUICK SMOKE TEST

Run this comprehensive test to verify everything at once:

```powershell
# 1. Create link
$response = Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8001/api/v1/links" `
  -ContentType "application/json" `
  -Body '{"long_url": "https://www.example.com/test"}'

$code = $response.short_code
Write-Host "✓ Created link: $code"

# 2. Test redirect
$redirect = Invoke-WebRequest -Uri "http://localhost:8002/$code" -MaximumRedirection 0 -ErrorAction SilentlyContinue
Write-Host "✓ Redirect status: $($redirect.StatusCode)"

# 3. Wait and check analytics
Start-Sleep -Seconds 3
$stats = Invoke-RestMethod -Uri "http://localhost:8003/stats/$code"
Write-Host "✓ Analytics visits: $($stats.total_visits)"

Write-Host "`n🎉 All systems operational!"
```

---

## 📊 EXPECTED SYSTEM STATE

After full setup, your system should have:

**Processes:**
- 3 Docker containers
- 3 Python/uvicorn processes (services)
- 1 Python process (analytics worker) - optional

**Network:**
- Port 5432: PostgreSQL
- Port 6379: Redis
- Port 5672: RabbitMQ (AMQP)
- Port 15672: RabbitMQ Management UI
- Port 8001: Link Management API
- Port 8002: Redirection Service
- Port 8003: Analytics API

**Database:**
- `url_shortener` database
- `links` table with data
- `link_visits` table with analytics

**Files Created:**
- test_data_links.json (after loading test data)
- Various log files

---

## ✅ SUCCESS CRITERIA

Your system is fully operational when:

1. ✅ All health checks return "healthy"
2. ✅ You can create and retrieve links
3. ✅ Redirects work and are fast (<50ms with cache)
4. ✅ Analytics records visits
5. ✅ Tests pass
6. ✅ Test data loads successfully
7. ✅ No errors in service logs

---

## 🎓 WHAT TO TRY NEXT

Once verified, try these scenarios:

1. **Custom Aliases:**
   ```json
   {"long_url": "https://github.com", "custom_alias": "my-github"}
   ```

2. **Expiring Links:**
   ```json
   {
     "long_url": "https://example.com",
     "expires_at": "2026-12-31T23:59:59"
   }
   ```

3. **High Load:**
   - Create 100+ links
   - Visit them repeatedly
   - Check cache performance

4. **Analytics Deep Dive:**
   - Check device statistics
   - View time series data
   - Analyze top links

---

**📞 Need Help?**

Check the logs:
```powershell
# Docker logs
docker logs url_shortener_postgres
docker logs url_shortener_redis
docker logs url_shortener_rabbitmq

# Service logs (in their terminals)
# Look for errors or warnings
```

---

*Last Updated: April 21, 2026*
*Status: Ready for verification ✅*
