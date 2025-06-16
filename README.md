# Remote Postgres MCP Server

A Model Control Protocol (MCP) server that provides secure, read-only access to PostgreSQL databases via streamable HTTP transport. Built with FastMCP and asyncpg for high-performance database operations.

## Features

- **Read-only Database Access**: Secure access to PostgreSQL databases with read-only operations
- **Streamable HTTP Transport**: Built-in HTTP server for MCP communication
- **Connection Pooling**: Efficient database connection management with asyncpg
- **Docker Support**: Containerized deployment with Docker and docker-compose

## Available Tools

- **execute_query**: Execute SELECT statements and retrieve data
- **get_table_schema**: Inspect table structures and column information  
- **list_tables**: List all tables in the database

## Installation

### Prerequisites

- Python 3.13 or higher
- PostgreSQL database access

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd remote-postgres-mcp

# Install dependencies with uv
uv sync
```

### Using pip

```bash
# Clone the repository
git clone <repository-url>
cd remote-postgres-mcp

# Install dependencies
pip install -r requirements.txt
# or install from pyproject.toml
pip install -e .
```

### Command Line Arguments

The server accepts the following arguments:

- `database_url` (required): PostgreSQL connection URL
- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 8006)

## Usage

### Basic Usage

```bash
# Run with command line arguments
python main.py "postgresql://user:password@database_host:5432/mydb"

# Run with custom host and port
python main.py "postgresql://user:password@database_host:5432/mydb" --host 127.0.0.1 --port 8080
```

### Using uv

```bash
# Run with uv
uv run python main.py "postgresql://user:password@database_host:5432/mydb"
```

## Docker Deployment

### Using Docker Compose

1. Update the `docker-compose.yml` with your database configuration:

```yaml
services:
  remote-postgres-mcp:
    build: .
    ports:
      - "8006:8006"
    command: >
      postgresql://username:password@database_host:5432/database
      --host 0.0.0.0
      --port 8006
```

2. Run the service:

```bash
docker-compose up -d
```

### Using Docker

```bash
# Build the image
docker build -t remote-postgres-mcp .

# Run the container
docker run -p 8006:8006 \
  remote-postgres-mcp \
  "<database_url>"
```