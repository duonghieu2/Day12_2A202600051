#  Delivery Checklist — Day 12 Lab Submission

> **Student Name:** _________________________  
> **Student ID:** _________________________  
> **Date:** _________________________

---

##  Submission Requirements

Submit a **GitHub repository** containing:

### 1. Mission Answers (40 points)

Create a file `MISSION_ANSWERS.md` with your answers to all exercises:

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcode thông tin nhạy cảm (Secrets) trực tiếp trong code: Các biến `OPENAI_API_KEY` và `DATABASE_URL` chứa mật khẩu được gán trực tiếp. Nếu vô tình push đoạn code này lên Git public, thông tin xác thực sẽ bị lộ ngay lập tức.
2. Thiếu quản lý cấu hình (No Configuration Management): Các thiết lập như `DEBUG = True` hay `MAX_TOKENS = 500` bị "đóng đinh" trong file. Trên production, chúng ta cần thay đổi các thông số này linh hoạt qua Environment Variables thay vì phải sửa code.
3. Sử dụng `print()` thay vì thư viện Logging chuẩn và làm lộ secret:
Code dùng lệnh `print()` để in log ra console, gây khó khăn cho việc thu thập và phân tích log hệ thống. Tệ hơn, dòng `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")` đã in thẳng API Key thật ra màn hình terminal, một lỗi bảo mật rất nặng.
4. Không có Health Check Endpoint (`/health`):
Hệ thống thiếu một API route chuyên dụng để báo cáo trạng thái. Nếu không có nó, các nền tảng cloud (như Docker, Kubernetes, Railway) sẽ không biết khi nào Agent bị treo để tự động khởi động lại container.
5. Cấu hình server (Host/Port) bị gắn chết và bật chế độ Reload:
Hàm `uvicorn.run` bị cấu hình cứng chạy ở `host="localhost"` (khiến các kết nối từ bên ngoài container không thể truy cập) và `port=8000` (bỏ qua biến môi trường `$PORT` mà cloud provider thường tự động cấp phát). Đồng thời, `reload=True` chỉ dành cho lúc dev, nếu để trên production sẽ làm giảm hiệu suất nghiêm trọng và gây rò rỉ bộ nhớ.

### Exercise 1.3: Comparison table

| Feature | Basic (`develop/app.py`) | Advanced (`production/app.py`) | Tại sao quan trọng khi lên Production? |
|---------|-------|----------|---------------------|
| Config & Secrets | Hardcode giá trị trực tiếp trong source code. | Đọc cấu hình từ Environment Variables (thông qua `os.getenv`). | Bảo mật & Linh hoạt: Đảm bảo không bị lộ API Key khi đưa code lên Git. Đồng thời giúp dễ dàng thay đổi cấu hình giữa các môi trường (dev, staging, prod) mà không cần sửa code. |
| Health check | Không có endpoint kiểm tra trạng thái (❌). | Có các endpoint như `/health` và `/ready` (✅). | Tự động phục hồi: Giúp các nền tảng Cloud (như Railway, Render, Kubernetes) biết container có đang bị treo hay không để tự động restart, và biết khi nào app thực sự sẵn sàng nhận traffic. |
| Logging | Dùng lệnh `print()` thuần túy. | Dùng Structured JSON Logging (`logging` module xuất ra định dạng JSON). | Phân tích & Theo dõi: Log dạng JSON giúp các công cụ gom log (như Datadog, ELK) dễ dàng parse, filter và query lỗi, thay vì phải đọc từng dòng text trơn. |
| Shutdown | Tắt đột ngột (Hard kill) ngay lập tức khi dừng ứng dụng. | Graceful Shutdown (quản lý qua `lifespan`). | Bảo toàn dữ liệu: Cho phép server có một khoảng thời gian ngắn để hoàn thành nốt các request đang xử lý dở dang và đóng kết nối database an toàn trước khi tắt hẳn, tránh báo lỗi cho end-user. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: Base image được sử dụng ở đây là `python:3.11` (được khai báo qua lệnh `FROM python:3.11`). Đây là bản phân phối Python đầy đủ, thường dùng làm điểm khởi đầu trước khi tối ưu hóa xuống các bản nhẹ hơn (như `slim` hoặc `alpine` trong bản production).
2. Working directory: Working directory là `/app` (được thiết lập qua lệnh `WORKDIR /app`). Đây là thư mục mặc định bên trong container, nơi chứa source code và là nơi các lệnh tiếp theo (như `COPY`, `RUN`, `CMD`) sẽ được thực thi.
3. Tại sao COPY requirements.txt trước?: Việc `COPY requirements.txt` và chạy `RUN pip install` TRƯỚC khi COPY toàn bộ source code là để tận dụng cơ chế Docker layer cache. Source code là thứ thay đổi liên tục, trong khi thư viện (requirements) thì ít đổi hơn. Nếu viết như thế này, ở những lần build sau, nếu `requirements.txt` không đổi, Docker sẽ dùng lại cache của bước cài thư viện thay vì tải lại từ đầu, giúp thời gian build nhanh hơn rất nhiều.
4. CMD vs ENTRYPOINT khác nhau thế nào?: `CMD`: Chỉ định lệnh mặc định để chạy khi container khởi động (ở đây là `CMD ["python", "app.py"]`). Lệnh này rất dễ bị ghi đè (override) từ bên ngoài khi người dùng truyền thêm tham số vào lệnh `docker run`.

`ENTRYPOINT`: Cấu hình container chạy như một executable file cố định. Nó khó bị ghi đè hơn `CMD` và mọi tham số truyền vào từ `docker run` thường sẽ được nối thêm vào sau `ENTRYPOINT`.

### Exercise 2.3: Image size comparison
- Develop: [1.66] GB
- Production: [424] MB
- Difference: [75]%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://my-production-agent-day12.railway.app
- Screenshot: [screenshots/railway_deploy.png](screenshots/railway_deploy.png)

## Part 4: API Security

### Exercise 4.1-4.3: Test results
- **4.1 API Key Auth:** Gọi API không có API Key trả về lỗi 401:
  `{"detail":"Invalid or missing API key. Include header: X-API-Key: <key>"}`
- **4.2 Valid Auth:** Cung cấp API Key hợp lệ trả về status 200 OK cùng token answer:
  `{"question":"Hello","answer":"Agent đang hoạt động bình thường...","model":"gpt-4o-mini","timestamp":"2026-04-17T...","history_length":1}`
- **4.3 Rate Limiting:** Sau khi gọi > 20 req/min, server chặn request và xuất code 429:
  `{"detail":"Rate limit exceeded: 20 req/min"}`

### Exercise 4.4: Cost guard implementation
- **Cách tiếp cận:** Sử dụng Redis để lưu state tổng lượng tiền (cost) đã dùng theo từng tháng (Sử dụng key dạng `budget:{user_id}:{YYYY-MM}`). Khi có một request mới vào, token đầu vào và token đầu ra được tính toán thành chi phí dựa trên bảng giá định sẵn. Giá trị này được record lại thông qua atomic function `incrbyfloat` với expiry là khoảng 1 tháng. Khi mỗi user gọi API, nếu giới hạn vượt quá budget $10/tháng (giá trị hiện tại > $10) thì FastApi sẽ giương HTTP Exception 402/503 để từ chối xử lý, đồng thời ngăn user bị deduct quá số tiền.

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **5.1 Health Check:** Đã thiết lập `/health` liveness probe để platform biết container còn hoạt động, và `/ready` để kiểm tra kết nối tới db/Redis cho readiness probe trước khi nhận traffic.
- **5.2 Graceful Shutdown:** Xử lý bằng `lifespan` FastAPI event loop và config `timeout_graceful_shutdown` của uvicorn để đảm bảo ứng dụng kết thúc/hoàn thành sạch sẽ các request đang chờ trước khi process tắt khi nhận lệnh `SIGTERM`.
- **5.3 Stateless Design:** Cấu trúc ứng dụng đã được thay đổi từ lưu local tuple trên RAM bằng Redis hash/list data types. Lịch sử chat được lưu trên memory in-cloud Redis thông qua lệnh `rpush` và `ltrim` để duy trì ngữ cảnh.
- **5.4 Load Balancing:** Kết hợp với Nginx, Docker compose có khả năng scale agents lên n-pods (ví dụ 3 instances) và round-robin định tuyến các luồng traffic 1 cách cân bằng.
```

---

### 2. Full Source Code - Lab 06 Complete (60 points)

Your final production-ready agent with all files:

```
your-repo/
├── app/
│   ├── main.py              # Main application
│   ├── config.py            # Configuration
│   ├── auth.py              # Authentication
│   ├── rate_limiter.py      # Rate limiting
│   └── cost_guard.py        # Cost protection
├── utils/
│   └── mock_llm.py          # Mock LLM (provided)
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Full stack
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .dockerignore            # Docker ignore
├── railway.toml             # Railway config (or render.yaml)
└── README.md                # Setup instructions
```

**Requirements:**
-  All code runs without errors
-  Multi-stage Dockerfile (image < 500 MB)
-  API key authentication
-  Rate limiting (10 req/min)
-  Cost guard ($10/month)
-  Health + readiness checks
-  Graceful shutdown
-  Stateless design (Redis)
-  No hardcoded secrets

---

### 3. Service Domain Link

Create a file `DEPLOYMENT.md` with your deployed service information:

```markdown
# Deployment Information

## Public URL
https://my-production-agent-day12.railway.app

## Platform
Railway / Render / Cloud Run

## Test Commands

### Health Check
```bash
curl https://my-production-agent-day12.railway.app/health
# Expected: {"status": "ok"}
```

### API Test (with authentication)
```bash
curl -X POST https://my-production-agent-day12.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "question": "Hello"}'
```

## Environment Variables Set
- PORT
- REDIS_URL
- AGENT_API_KEY
- LOG_LEVEL

## Screenshots
- [Deployment dashboard](screenshots/dashboard.png)
- [Service running](screenshots/running.png)
- [Test results](screenshots/test.png)
```

##  Pre-Submission Checklist

- [ ] Repository is public (or instructor has access)
- [ ] `MISSION_ANSWERS.md` completed with all exercises
- [ ] `DEPLOYMENT.md` has working public URL
- [ ] All source code in `app/` directory
- [ ] `README.md` has clear setup instructions
- [ ] No `.env` file committed (only `.env.example`)
- [ ] No hardcoded secrets in code
- [ ] Public URL is accessible and working
- [ ] Screenshots included in `screenshots/` folder
- [ ] Repository has clear commit history

---

##  Self-Test

Before submitting, verify your deployment:

```bash
# 1. Health check
curl https://my-production-agent-day12.railway.app/health

# 2. Authentication required
curl https://my-production-agent-day12.railway.app/ask
# Should return 401

# 3. With API key works
curl -H "X-API-Key: YOUR_KEY" https://my-production-agent-day12.railway.app/ask \
  -X POST -d '{"user_id":"test","question":"Hello"}'
# Should return 200

# 4. Rate limiting
for i in {1..15}; do 
  curl -H "X-API-Key: YOUR_KEY" https://my-production-agent-day12.railway.app/ask \
    -X POST -d '{"user_id":"test","question":"test"}'; 
done
# Should eventually return 429
```

---

##  Submission

**Submit your GitHub repository URL:**

```
https://github.com/your-username/day12-agent-deployment
```

**Deadline:** 17/4/2026

---

##  Quick Tips

1.  Test your public URL from a different device
2.  Make sure repository is public or instructor has access
3.  Include screenshots of working deployment
4.  Write clear commit messages
5.  Test all commands in DEPLOYMENT.md work
6.  No secrets in code or commit history

---

##  Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review [CODE_LAB.md](CODE_LAB.md)
- Ask in office hours
- Post in discussion forum

---

**Good luck! **
