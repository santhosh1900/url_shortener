## Setup & Run Instructions

### Prerequisites
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed
- [Git](https://git-scm.com/) installed
- `.env` file with required environment variables (already included in the repository)

### Steps

1. **Clone the repository**

```
git clone https://github.com/santhosh1900/url_shortener.git
cd url_shortener
```

2. **Verify .env file**

```
# DB
POSTGRES_USER=postgres
POSTGRES_PASSWORD=0000
POSTGRES_DB=zocket
POSTGRES_HOST=db
POSTGRES_PORT=5432
SYSTEM_DB=postgres
#Redis
REDIS_HOST=redis
REDIS_PORT=6379
# Utilities
MAX_CODE_LENGTH=10
BASE_URL=http://localhost:8080
RATE_LIMITTER_SECONDS=60
RATE_LIMITTER_REQUESTS=100
PORT=8080
ADMIN=admin
ADMIN_PASSWORD=password@2000
JWT_SECRET=13adfadvgwef342$4124rvs412r12f!@1231223caca3344adfavad41332dsvdsbsdvadgefq
```

3. **Build and start the containers locally**

docker-compose up --build

This command will:
- Build the FastAPI backend service
- Start PostgreSQL and Redis containers
- Load environment variables from .env

4. **Access the application**

- FastAPI backend: http://localhost:8080
- PostgreSQL: dbt:5432 (credentials from .env)
- Redis: redis:6379 (credentials from .env)

5. **Stop the application**

```
docker-compose down
```

6. **Run using published Docker image (no local build required)**

docker run -p 8080:8080 docker.io/sandydev007/url-shortener:latest

Access the backend at http://localhost:8080

Make sure PostgreSQL and Redis containers are running or accessible (if using local .env settings).

6. **References**

GitHub Repository: https://github.com/santhosh1900/url_shortener

Docker Image: https://hub.docker.com/repository/docker/sandydev007/url-shortener/general

##



## API Reference
Base URL: http://localhost:8080
##

#### Create Short URL

```http
  POST /get-shorten-url
```

#### Body

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `url` | `string` | **Required**. |
| `customName` | `string` | **Optional**. |

#### Response (Without customName)
```
{
  "success": true,
  "url": "http://localhost:8080/1pv3WEq3My"
}
```

#### Response (With customName eg: sandy)
```
{
  "success": true,
  "url": "http://localhost:8080/sandy"
}
```

##

#### Get URL

```http
  GET /${short-code}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `short-code`      | `string` | **Required**. Id of item to fetch |

#### Response

307 Temporary Redirect

#### Response (Not Found)

404 URL not found

##


#### Admin Login

```http
  POST /admin-login
```
#### Body

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `username` | `string` | **admin** |
| `password` | `string` | **password@2000** |

#### Response
Save this access_token as a Bearer Token in the headers (Authorization)
```
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2MTQzMDU3NX0.SD-7Z91hwKrJopl5ARpPsSl02WC0wVZCVlgE1ZsrsAc",
    "token_type": "bearer"
}
```

##

#### Get All Urls (Protected Route)

```http
  GET /get-urls
```

#### Response
```
[
  {
      "original_url": "https://redis.io/",
      "click_count": 0,
      "id": 1,
      "created_at": "26/10/2025 : 02:51:05 AM",
      "last_accessed_at": "",
      "short_code": "http://localhost:8080/bIlXsGwkoX",
      "updated_at": "26/10/2025 : 02:51:05 AM",
      "analytics": "http://localhost:8080/get-analytics/bIlXsGwkoX"
    },
    {
      "original_url": "https://google.com/",
      "click_count": 10,
      "id": 1,
      "created_at": "26/10/2025 : 02:51:05 AM",
      "last_accessed_at": "",
      "short_code": "http://localhost:8080/sandy",
      "updated_at": "26/10/2025 : 02:51:05 AM",
      "analytics": "http://localhost:8080/get-analytics/sandy"
    }
]
```
##

#### Get Analytics of the single url
```http
  GET /get-analytics/${short-code}
```
This route gives you the date wise total_click of the particular short url

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `short-code` | `string` | **Required** |

#### Response
```
[
  {
    "date": "25/10/2025",
    "total_clicks": 3,
    "url": "https://redis.io/",
    "short_url": "http://localhost:8080/bIlXsGwkoX"
  }
]
```



## 🏛️ Architectural Overview

The URL Shortener Service is built on a microservice-oriented architecture using Python's FastAPI framework, leveraging PostgreSQL for persistence and Redis for high-speed caching and rate limiting.

#### 1. Client Interaction (The Request Flow)


| Component | Technology  | Primary Role(s)                      |
| :-------- | :------- | :-------------------------------- |
| API/Web Service      | FastAPI (Python) |Exposes high-speed RESTful endpoints, handles Rate Limiting (per IP), input validation, and JWT-based Token Authentication for admin routes. |
| Persistent Storage      | PostgreSQL |The Source of Truth for all URL mappings, metadata (including created_at, click_count, last_accessed_at), and detailed Analytics Data (date-wise clicks). |
| Caching/Auxiliary DB      | Redis |High-speed Caching for redirect lookups (GET /:short-code) to meet the $< 100 \text{ ms}$ latency constraint. Also utilized for efficient Rate Limiting tracking. |
| Deployment      | Docker & Docker Compose |Containerization for consistent, isolated, and scalable deployment across environments using a multi-stage build. |


##

#### 2. Core Request Flow

#### A. URL Creation (POST /get-shorten-url)

This flow ensures idempotency (same long URL $\rightarrow$ same short code) and supports Custom Aliases.

- Request Validation & Rate Limit Check: FastAPI validates the input URL. 

- The **RateLimiter** mechanism, backed by Redis, checks the client's IP and rejects requests exceeding **100 per minute**.

- Idempotency Check: The system checks if the original URL already exists in PostgreSQL.

- Short Code Generation: If new, a unique, up to 10-character short code is generated (or uses the provided customName). Collision handling is managed in the service layer.

- Persistence: The mapping and initial metadata are saved to PostgreSQL.

- Response: Returns the full shortened URL.

##

#### B. Redirection (GET /:short-code)

This flow is optimized for speed using a caching layer.

- Cache Lookup: The service first checks Redis for the original_url associated with the short-code.

- Cache Hit ($\approx 1 \text{ ms}$): If found, the application immediately returns a 307 Temporary Redirect response.

- Cache Miss: 
    - a. The original URL is fetched from PostgreSQL.
    - b. The click_count and last_accessed_at metadata are updated in PostgreSQL.
    - c. Analytics Data (date-wise click) is recorded.
    - d. The mapping is written back to Redis for subsequent requests.
    - e. Returns a 307 Temporary Redirect.

##

#### C. Admin & Analytics
- Admin routes (/get-urls, /get-analytics) are protected by Token-based Authentication (JWT).

- /get-urls: Fetches and returns paginated lists of all URLs and their metadata from PostgreSQL.

- /get-analytics: Queries PostgreSQL to retrieve and aggregate the detailed, date-wise click data for a specific short code.

## 

#### 3. Modular Code Structure

The application uses a clean Handler -> Service -> Repository layer separation for maintainability and testability:

- handler/router: HTTP Request handling, input/output validation, and rate limiter invocation.

- service: Core business logic (Short Code generation, caching logic, rate limiting coordination).

- repository: Data access layer (all interaction with PostgreSQL and Redis).


## 🖼️ Architectural Diagram

This diagram illustrates the main components and data flow within the URL Shortener Service.

```text
+---------------------+      +-------------------------------------+
|                     |      |            FastAPI Service          |
|      End User       |<-----| (http://localhost:8080)             |
|  (Browser/Client)   |      |                                     |
+---------------------+      | +---------------------------------+ |
           |                 | |     Rate Limiter (per IP)       | |
           |    HTTP Request | |     (Python RateLimiter lib)    | |
           |                 | +---------------------------------+ |
           |                 |                  |                  |
           |                 | +---------------------------------+ |
           |                 | |          Handlers / Routers     | |
           |                 | |  (e.g., /get-shorten-url, /:code)| |
           |                 | +---------------------------------+ |
           |                 |                  |                  |
           |                 | +---------------------------------+ |
           |                 | |          Service Layer          | |
           |                 | | (Business Logic, Code Gen, JWT) | |
           |                 | +---------------------------------+ |
           |                 |                  |                  |
           |                 | +---------------------------------+ |
           |                 | |         Repository Layer        | |
           |                 | | (DB Abstraction, Caching Logic) | |
           |                 | +---------------------------------+ |
           |                 +-------------------------------------+
           |                             |            |
           |        Cache Read/Write     |            | Persistent Data
           +---------------------------> |            |
                                         V            V
                          +---------------------+  +---------------------+
                          |        Redis        |  |     PostgreSQL      |
                          | (Cache, Rate Limits)|  | (Primary DB, Analytics)|
                          +---------------------+  +---------------------+
                                                       ^
                                                       |
                                                       | Long-term Storage
                                                       | URL metadata, click counts
                                                       | detailed analytics
```



## ⚖️ Design Decisions and Trade-Offs

The system architecture and technology stack were chosen to meet the core requirements of low latency redirects, data durability, idempotency, and scalability under a high read-to-write ratio.

#### 1. Client Interaction (The Request Flow)


| Decision |Rationale  | Trade-Off                      |
| :-------- | :------- | :-------------------------------- |
| Technology Stack: FastAPI, PostgreSQL, Redis      | High Performance & Development Speed: FastAPI with async I/O offers near-Go performance with Python's rapid development. PostgreSQL provides durability and analytics, and Redis ensures extreme speed. |Complexity: Using two databases (PostgreSQL and Redis) adds complexity to deployment and requires careful data consistency logic in the application layer. |
| Short Code Generation: Base62 Encoding of Sequential IDs (Deterministic)      | Guaranteed Uniqueness & Idempotency: Deriving the short code from a sequential, unique ID eliminates the need for expensive database collision checks, crucial for handling 10,000 new URLs/day. |Guessability/Predictability: Sequential codes, even encoded, are more predictable than random strings, potentially allowing malicious users to crawl the short URL space.|
| Data Storage: PostgreSQL (Primary DB)      | Strong Consistency & Durability: PostgreSQL is the source of truth for all mappings, metadata (created_at, last_accessed_at), and detailed analytics, ensuring data integrity over the required 5-year retention period. |Slower Redirect Latency: A direct database hit on every redirect would violate the $< 100 \text{ ms}$ latency requirement. This necessitates the use of a caching layer. |
| Caching Layer: Redis (In-Memory)      |Achieve Low Latency: Serves the high volume of read requests (redirects) directly from memory, meeting the 100 ms constraint and significantly offloading the primary database. |Data Freshness: Cached click counts may be slightly stale compared to the PostgreSQL counter, as the counter is only updated in the DB on a cache miss. This lag is an acceptable trade-off for speed. |
| Redirect Status Code: HTTP 307 Temporary Redirect      |Allows Click Analytics: Forces the client browser to hit our service on every access, enabling the service to accurately increment click_count and record granular analytics data. |Higher Server Load: The server must handle every single redirect request, increasing the overall load compared to using a permanent 301 redirect. |
| Rate Limiting Implementation: Per-IP using Python's RateLimiter      |Protection from Abuse: Simple and effective protection against DDoS/spamming the URL creation endpoint, fulfilling a core requirement without custom, complex Redis scripting. |Reliance on External Library: This ties the implementation to a specific Python package, making future language or architecture transitions slightly more complex.|

##

#### The choice to use both PostgreSQL and Redis is the central trade-off, prioritizing durability/analytics (PostgreSQL) and performance/latency (Redis) over architectural simplicity.



