from sqlmodel import Session, text


# ========== Helper Function ==========
def print_table_schema(session: Session, table_name: str):
    """Print the table structure and all rows"""
    print("\n" + "="*60)
    print("TABLE STRUCTURE")
    print("="*60)
    
    # Get table structure
    result = session.execute(text(f"PRAGMA table_info({table_name})"))
    for row in result:
        print(f"Column: {row[1]:<20} Type: {row[2]:<15} NotNull: {row[3]} PK: {row[5]}")
    
    print("\n" + "="*60)
    print("TABLE DATA")
    print("="*60)
    
    # Get all companies
    companies = session.execute(text(f"SELECT * FROM {table_name}")).all()
    if not companies:
        print("(No data)")
    else:
        for company in companies:
            print(company)
    
    print("="*60 + "\n")