import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# Create S3 resource
s3 = boto3.resource('s3')
bucket_name = os.getenv('S3_BUCKET_NAME')
bucket_region = os.getenv('S3_BUCKET_REGION')

def setup_s3_bucket():
    try:
        # Create bucket if it doesn't exist
        bucket = s3.Bucket(bucket_name)

        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' already exists")
        except:
            # Create bucket with region configuration
            bucket.create(CreateBucketConfiguration={'LocationConstraint': bucket_region})
            print(f"✅ Created bucket '{bucket_name}'")

        return bucket
    
    except Exception as e:
        print(f"❌ Error setting up bucket: {e}")
        return None

if __name__ == "__main__":
    setup_s3_bucket()




