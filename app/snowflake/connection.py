import os
import snowflake.connector as sf
from dotenv import load_dotenv

load_dotenv()

connection = sf.connect(
    user=os.getenv('SF_USERNAME'),
    password=os.getenv('SF_PWD'),
    account=os.getenv('SF_ACCOUNT_IDENTIFIER')
)

def snowflake_health_check():
    try:
        print("Connecting to Snowflake...")
        
        # Test the connection with a simple query
        cursor = connection.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        result = cursor.fetchone()
        print("Connection successful")
        print(f"Snowflake version: {result[0]}")
        
    except Exception as e:
        print(f"Error connecting to Snowflake: {e}")
        
    finally:
        cursor.close()
        connection.close()
        print("Connection closed successfully")

