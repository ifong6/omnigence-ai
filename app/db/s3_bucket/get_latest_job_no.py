import boto3
import re


def get_latest_job_no_from_s3():
    """
    Scan S3 bucket to find the latest job number from existing quotation files.

    Returns:
        int: The latest job number found, or 0 if no files exist
    """
    s3_client = boto3.client('s3')
    bucket_name = 'finance-agent-bucket'
    prefix = 'quotation/'

    try:
        # List all objects in the quotation/ folder
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )

        max_job_no = 0

        if 'Contents' in response:
            for obj in response['Contents']:
                filename = obj['Key'].split('/')[-1]  # Get filename from path

                # Match pattern: quotation_Q-JCP-YY-NO-VER.csv
                match = re.search(r'Q-JCP-\d{2}-(\d+)-\d+\.csv', filename)
                if match:
                    job_no = int(match.group(1))
                    max_job_no = max(max_job_no, job_no)

        print(f"✅ Latest job number from S3: {max_job_no}")
        return max_job_no

    except Exception as e:
        print(f"❌ Error scanning S3: {e}")
        return 0


if __name__ == "__main__":
    latest = get_latest_job_no_from_s3()
    print(f"Next job number will be: {latest + 1:02d}")
