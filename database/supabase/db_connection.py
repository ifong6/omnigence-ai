import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
SB_USER = os.getenv("SB_USER")
SB_PASSWORD = os.getenv("SB_PASSWORD")
SB_HOST = os.getenv("SB_HOST")
SB_PORT = os.getenv("SB_PORT")
SB_DBNAME = os.getenv("SB_DBNAME")

def execute_query(query, params=None, fetch=False):
    try:
        connection = psycopg2.connect(
            user=SB_USER,
            password=SB_PASSWORD,
            host=SB_HOST,
            port=SB_PORT,
            dbname=SB_DBNAME
        )
        print("Connection successful!")

        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(query, params or [])

        data = cursor.fetchall() if fetch else None
        connection.commit()

        cursor.close()
        connection.close()   # ✅ Always close to avoid open connections in Supabase free tier

        # Convert RealDictRow to plain dict for consistent return type
        if data:
            return [dict(row) for row in data]
        return data

    except Exception as e:
        print(f"Failed to run query: {e}")
        raise  # Re-raise the exception instead of silently returning None
    