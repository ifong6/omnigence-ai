from app.s3_bucket.connection import setup_s3_bucket
import os
from dotenv import load_dotenv

load_dotenv()

def upload_file_to_s3(file_path:str, file_name:str):

    quotation_csv_bucket = setup_s3_bucket()

    if quotation_csv_bucket is None:
        raise Exception("Failed to setup S3 bucket")

    try:
        # Upload to S3
        s3_folder = os.getenv('S3_QUOTATION_CSV_FOLDER')
        s3_key = f"{s3_folder}/{file_name}"
        quotation_csv_bucket.upload_file(file_path, s3_key)

        s3_base_url = os.getenv('S3_BASE_URL')
        s3_url = f"{s3_base_url}/{s3_key}"
        print(f"✅ Uploaded CSV file to {s3_url}")

    except Exception as e:
        print(f"❌ Error uploading CSV file: {e}")
        raise