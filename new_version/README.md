# High-Performance National Exam API

This project is a high-concurrency API built in **Go** to serve national exam results. It is optimized to handle tens of thousands of requests per second (RPS) through aggressive caching, connection pooling, and request coalescing.

---

##  Key Features

* **Request Coalescing:** Uses `singleflight` to prevent "Thundering Herd" issues, ensuring only one database query is executed for the same ID simultaneously.
* **Asynchronous Caching:** Implements a background worker pool and buffered channels to write results to Redis without blocking the main request path.
* **High-Speed JSON:** Utilizes the `sonic` library for ultra-fast JSON encoding and decoding.
* **Load Balanced:** Configured with Nginx (`least_conn`) and 10 application replicas for maximum throughput.
* **Optimized Networking:** Nginx and Redis are tuned with high `nofile` limits and persistent `keepalive` connections.

---

##  Tech Stack

* **Backend:** Go (using `fasthttp`)
* **Database:** MySQL 8.0 (with GORM)
* **Cache:** Redis 7 (Alpine)
* **Proxy/LB:** Nginx
* **Infrastructure:** Docker & Docker Compose

---

##  Getting Started

Follow these steps to get the environment running from scratch:

### 1. Clone the Repository
```bash
git clone https://github.com/Nguyenn0312/National_Exam_SearchEngine.git
cd National_Exam_SearchEngine
```

### 2. Synchronize Go Dependencies
Before building, ensure all required packages (like `singleflight` and `sonic`) are downloaded:
```bash
go mod tidy
```

### 3. Configuration
The project uses environment variables for database security. Create a `.env` file in the root directory:
```bash
echo "DB_PASSWORD=your_secure_password" > .env
```

### 4. Deploy with Docker
Build and start the entire stack (Database, Redis, 10 App Replicas, and Nginx):
```bash
docker-compose up -d --build
```
This will start the database, Redis, 10 API instances, and the Nginx load balancer.

---
##  API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/search/{sbd}` | GET | Search for a specific student by ID (SBD). Results are cached in Redis. |
| `/api/search/?{subject}={score}` | GET | Filter students by subject scores (e.g., `math=9`). |

---

##  Benchmarking

To test the performance of the system, ensure you have the stack running and use `wrk`:

**Run test through docker with wrk:**
```bash
docker run --net=host --rm williamyeh/wrk -t14 -c4000 -d60s --latency http://localhost/api/search/24008611
```

---

##  Architecture

[Image of a high-performance web architecture including Nginx load balancer, Go application replicas, Redis cache, and MySQL database]

The architecture is designed to minimize latency at every hop:
1.  **Nginx** balances traffic across 10 app containers using the `least_conn` strategy.
2.  **Go Apps** check Redis first. If a cache miss occurs, `singleflight` ensures only one instance hits the DB for that specific ID.
3.  **Redis Workers** update the cache asynchronously via buffered channels to keep response times low for the user.
