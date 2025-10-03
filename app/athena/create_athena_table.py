import boto3
from botocore.exceptions import ClientError

def create_quotation_csv_table():
    """Create external table in Athena for quotation CSV data."""
    # Athena client
    athena_client = boto3.client('athena')
    
    # SQL query to create table
    create_table_query = """
    CREATE EXTERNAL TABLE IF NOT EXISTS quotes_csv (
        txn_date date,
        quotation_no string,
        cust_name string,
        cust_address string,
        proj_name string,
        total_amount double,
        no int,
        content string,
        quantity double,
        unit string,
        unit_price double,
        subtotal double,
        currency string
    )
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
    WITH SERDEPROPERTIES (
        "separatorChar" = ",",
        "quoteChar" = "\\"",
        "escapeChar" = "\\\\"
    )
    LOCATION 's3://finance-agent-bucket/quotation/'
    TBLPROPERTIES ("skip.header.line.count"="1");
    """
    
    try:
        # Execute the query
        response = athena_client.start_query_execution(
            QueryString=create_table_query,
            QueryExecutionContext={
                'Database': 'default'  # Change to your database name if different
            },
            ResultConfiguration={
                'OutputLocation': 's3://finance-agent-bucket/athena-quotation-query-result/'  # S3 path for query results
            }
        )
        
        print(f"✅ Athena table creation started. Query execution ID: {response['QueryExecutionId']}")
        return response['QueryExecutionId']
        
    except ClientError as e:
        print(f"❌ Error creating Athena table: {e}")
        return None

def execute_athena_query(query_string, database='default'):
    """Execute a query against the Athena table and return execution ID."""
    athena_client = boto3.client('athena')
    
    try:
        # Start query execution
        response = athena_client.start_query_execution(
            QueryString=query_string,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': 's3://finance-agent-bucket/athena-results/'
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        print(f"🔄 Query started. Execution ID: {query_execution_id}")
        return query_execution_id
            
    except ClientError as e:
        print(f"❌ Error executing query: {e}")
        return None

def get_query_results(query_execution_id):
    """Retrieve results from completed Athena query."""
    athena_client = boto3.client('athena')
    
    try:
        results = []
        next_token = None
        
        while True:
            if next_token:
                response = athena_client.get_query_results(
                    QueryExecutionId=query_execution_id,
                    NextToken=next_token
                )
            else:
                response = athena_client.get_query_results(
                    QueryExecutionId=query_execution_id
                )
            
            # Extract column names from first row (header)
            if not results:
                columns = [col['VarCharValue'] for col in response['ResultSet']['Rows'][0]['Data']]
                results.append(columns)
            
            # Extract data rows (skip header row)
            for row in response['ResultSet']['Rows'][1:]:
                row_data = []
                for cell in row['Data']:
                    if 'VarCharValue' in cell:
                        row_data.append(cell['VarCharValue'])
                    else:
                        row_data.append(None)
                results.append(row_data)
            
            # Check if there are more results
            if 'NextToken' in response:
                next_token = response['NextToken']
            else:
                break
        
        return results
        
    except ClientError as e:
        print(f"❌ Error retrieving query results: {e}")
        return None

def check_query_status(query_execution_id):
    """Check the status of the Athena query execution."""
    athena_client = boto3.client('athena')
    
    try:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        
        if status == 'SUCCEEDED':
            print("✅ Query completed successfully!")
        elif status == 'FAILED':
            error_reason = response['QueryExecution']['Status']['StateChangeReason']
            print(f"❌ Query failed: {error_reason}")
        elif status in ['QUEUED', 'RUNNING']:
            print(f"🔄 Query is {status.lower()}...")
        
        return status
        
    except ClientError as e:
        print(f"❌ Error checking query status: {e}")
        return None

if __name__ == "__main__":
    import time
    
    # 1. Create table
    print("Step 1: Creating table...")
    execution_id = create_quotation_csv_table()
    
    if not execution_id:
        print("❌ Table creation failed. Please check your S3 bucket and permissions.")
        exit(1)
    
    # # 2. Check table creation status
    # print("\nStep 2: Checking table creation status...")
    # print("⏳ Waiting for table creation to complete...")
    # time.sleep(3)  # Wait a bit before checking
    # status = check_query_status(execution_id)
    
    # if status != 'SUCCEEDED':
    #     print("⚠️ Table creation not completed yet. Please run check_query_status() again later.")
    #     exit(0)
    
    # # 3. Run a query
    # print("\nStep 3: Running query...")
    # query_id = execute_athena_query('SELECT * FROM quotes_csv LIMIT 10;')
    
    # if not query_id:
    #     print("❌ Query execution failed.")
    #     exit(1)
    
    # # 4. Check query status
    # print("\nStep 4: Checking query status...")
    # print("⏳ Waiting for query to complete...")
    # time.sleep(3)  # Wait a bit before checking
    # query_status = check_query_status(query_id)
    
    # if query_status != 'SUCCEEDED':
    #     print("⚠️ Query not completed yet. Please run check_query_status() again later.")
    #     exit(0)
    
    # # # 5. Get results
    # # print("\nStep 5: Getting results...")
    # # results = get_query_results(query_id)
    
    # # if results:
    # #     print("\n📊 Query Results:")
    # #     print("-" * 80)
    # #     # Print header
    # #     if len(results) > 0:
    # #         print(" | ".join(results[0]))
    # #         print("-" * 80)
    # #     # Print data rows
    # #     for row in results[1:]:
    # #         print(" | ".join(str(cell) for cell in row))
    # #     print("-" * 80)
    # #     print(f"✅ Retrieved {len(results)-1} rows")
    # # else:
    # #     print("❌ Failed to retrieve results.")