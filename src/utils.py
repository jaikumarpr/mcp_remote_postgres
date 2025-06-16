from ipaddress import ip_address

def is_valid_host(host: str) -> bool:
    try:
        ip_address(host)
        return True
    except ValueError:
        return False
    
def is_valid_port(port: int) -> bool:
    return 1 <= port <= 65535

def is_valid_postgres_database_url(url: str) -> bool:
    return url.startswith(('postgresql://', 'postgres://'))