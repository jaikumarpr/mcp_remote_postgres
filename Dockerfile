# Builder stage
FROM python:3.13-alpine AS builder

RUN apk add --no-cache gcc musl-dev

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv pip install --system -e .


# Runtime stage
FROM python:3.13-alpine AS runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ ./src/

ENV PYTHONPATH=/app/src

EXPOSE 8006

ENTRYPOINT ["python", "-m", "main"]