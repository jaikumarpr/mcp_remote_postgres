import sys
import logging
from fastmcp import FastMCP
from mcp_server import setup,run
from args import get_args

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    
    try:
        db_url, host, port = get_args()
        
        mcp: FastMCP = setup(db_url)
        run(mcp,transport="streamable-http", host=host, port=port)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
