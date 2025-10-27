import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get output_dir from environment variable, with a default value
output_dir: str = os.getenv('OUTPUT_DIR', "/Users/keven/Desktop/product")
