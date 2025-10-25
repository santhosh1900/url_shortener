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

POSTGRES_USER=postgres
POSTGRES_PASSWORD=0000
POSTGRES_DB=zocket
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
PORT=8080
JWT_SECRET=<your-secret>

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


