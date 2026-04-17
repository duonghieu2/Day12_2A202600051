# Deployment Information

## Public URL
https://my-production-agent-day12.railway.app

> **Note:** Hãy thay thế đường link trên bằng URL thực tế sau khi deploy lên Railway/Render!

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://my-production-agent-day12.railway.app/health
# Expected: {"status": "ok", ...}
```

### API Test (with authentication)
```bash
curl -X POST https://my-production-agent-day12.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- `PORT`
- `REDIS_URL`
- `AGENT_API_KEY`
- `LOG_LEVEL`

## Screenshots
> Hãy chủ động chụp ảnh và lưu vào thư mục `screenshots/` theo danh sách sau:
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
