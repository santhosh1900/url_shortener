## Setup & Run Instructions

### Prerequisites
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed
- [Git](https://git-scm.com/) installed
- `.env` file with required environment variables (already included in the repository)

### Steps

1. **Clone the repository**

git clone https://github.com/santhosh1900/url_shortener.git
cd url_shortener

2. **Verify .env file**

```
POSTGRES_USER=postgres

POSTGRES_PASSWORD=0000

POSTGRES_DB=zocket

POSTGRES_HOST=db

POSTGRES_PORT=5432

REDIS_HOST=redis

REDIS_PORT=6379

PORT=8080

JWT_SECRET=<your-secret>
```

3. **Build and start the containers locally**

docker-compose up --build

This command will:

    - Build the FastAPI backend service

    - Start PostgreSQL and Redis containers
    
    - Load environment variables from .env

4. **Access the application**

FastAPI backend: http://localhost:8080

PostgreSQL: dbt:5432 (credentials from .env)

Redis: redis:6379 (credentials from .env)

5. **Stop the application**

docker-compose down

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



