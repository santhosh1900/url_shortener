# Stage 1: Builder
FROM python:3.11-alpine AS builder

WORKDIR /usr/src/app

RUN apk add --no-cache build-base postgresql-dev gcc libffi-dev musl-dev

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# Stage 2: Final lightweight runtime image
FROM python:3.11-alpine

WORKDIR /usr/src/app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app ./app
COPY .env .
COPY README.md .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
