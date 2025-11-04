import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL configuration from environment variables
PG_HOST = os.getenv('PG_HOST', 'localhost')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_DATABASE = os.getenv('PG_DATABASE', 'postgres')
PG_USERNAME = os.getenv('PG_USERNAME')
PG_PASSWORD = os.getenv('PG_PASSWORD')


def get_postgres_connection():
    """
    Create and return a PostgreSQL database connection.

    Returns:
        psycopg2.connection: PostgreSQL connection object
    """
    try:
        connection = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USERNAME,
            password=PG_PASSWORD
        )
        return connection
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        raise


def get_postgres_cursor(dict_cursor=True):
    """
    Create and return a PostgreSQL cursor.

    Args:
        dict_cursor (bool): If True, returns RealDictCursor for dictionary-like results

    Returns:
        tuple: (connection, cursor) - Both connection and cursor objects
    """
    try:
        connection = get_postgres_connection()
        if dict_cursor:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = connection.cursor()
            
        # print(f"Successfully created PostgreSQL connection")
        # print(f"Successfully created PostgreSQL cursor")
        return connection, cursor
    
    except Exception as e:
        print(f"❌ Error creating PostgreSQL cursor: {e}")
        raise

def execute_query(query, params=None, fetch_results=True):
    """
    Execute a PostgreSQL query and return results.

    Args:
        query (str): SQL query to execute
        params (tuple): Query parameters for parameterized queries
        fetch_results (bool): Whether to fetch and return results

    Returns:
        list: Query results (if fetch_results=True), None otherwise
    """
    connection = None
    cursor = None
    try:
        connection, cursor = get_postgres_cursor()
        cursor.execute(query, params)

        # Always commit for INSERT/UPDATE/DELETE queries
        # Check if query is a write operation (INSERT, UPDATE, DELETE, CREATE, ALTER, DROP)
        query_upper = query.strip().upper()
        is_write_operation = any(query_upper.startswith(cmd) for cmd in ['INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP'])

        if fetch_results:
            results = cursor.fetchall()
            # Commit if it's a write operation (like INSERT...RETURNING)
            if is_write_operation:
                connection.commit()
            return results
        else:
            connection.commit()
            return None

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"❌ Error executing query: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def test_connection():
    """
    Test the PostgreSQL connection.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        connection = get_postgres_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Successfully connected to PostgreSQL")
        print(f"Database version: {version[0]}")
        cursor.close()
        connection.close()
        return True
    
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()
