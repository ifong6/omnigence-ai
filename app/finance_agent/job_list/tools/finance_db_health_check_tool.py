from app.postgres.db_connection import test_connection
from app.postgres.db_connection import get_postgres_connection

def finance_db_health_check_tool():
    """
    Check the health of the finance database.
    
    returns:
        str: 
    """
    print("Checking finance database health...")
    
    if not test_connection():
        return "Finance (Postgres) database is not healthy."
    
    return get_postgres_connection()
