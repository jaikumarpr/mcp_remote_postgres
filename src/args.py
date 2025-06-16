import argparse
import logging
from utils import is_valid_host, is_valid_port, is_valid_postgres_database_url

logger = logging.getLogger(__name__)

_DEFAULT_HOST: str = "0.0.0.0"
_DEFAULT_PORT: int = 8006

def parse_args():

    parser = argparse.ArgumentParser(description="Remote Postgres MCP Server")
    parser.add_argument(
        "database_url",
        help="PostgreSQL database URL (e.g., postgresql://user:password@host:port/database)"
    )
    parser.add_argument(
        "--host",
        default=_DEFAULT_HOST,
        help=f"Host to bind to (default: {_DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=_DEFAULT_PORT,
        help=f"Port to bind to (default: {_DEFAULT_PORT})"
    )

    return parser.parse_args()


def get_args() -> tuple[str, str, int]:

    args = parse_args()
    
    db_url:str = args.database_url
    
    host = args.host
    port = args.port

    validate_args(db_url, host, port)

    return db_url, host, port


def validate_args(db_url: str, host: str, port: int):
    
    try:
        if not is_valid_host(host):
            raise ValueError("Invalid host specified")
        if not is_valid_port(port):
            raise ValueError(f"Invalid port specified: {port}. Must be between 1 and 65535")
        if not is_valid_postgres_database_url(db_url):
                raise ValueError("Invalid database URL format. Must start with postgresql:// or postgres://")
    except Exception as e:
        raise ValueError(f"Error validating arguments: {e}")