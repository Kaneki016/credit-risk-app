import pandas as pd
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def test_schema_refactor(filename="refactor_test.csv"):
    print(f"Generating test data...")
    
    data = {
        "person_income": [50000],
        "loan_status": [0]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    
    try:
        # 1. Clear Database (should drop tables)
        print(f"\n1. Clearing database (drop_tables=true)...")
        response = requests.delete(f"{BASE_URL}/db/clear?confirm=true&drop_tables=true")
        
        if response.status_code == 200:
            print("✅ Database Cleared & Tables Dropped.")
        else:
            print(f"❌ Clear Database Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False

        # 2. Import CSV (should create table)
        print(f"\n2. Importing CSV (should create table)...")
        # Note: replace_schema param is now ignored or removed, but we can still pass it without error usually
        # The logic inside checks if table exists.
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/csv")}
            response = requests.post(f"{BASE_URL}/db/import_csv", files=files)
            
        if response.status_code == 200:
            print("✅ Import Successful (Table Created).")
        else:
            print(f"❌ Import Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
        # 3. Import CSV again (should append)
        print(f"\n3. Importing CSV again (should append)...")
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/csv")}
            response = requests.post(f"{BASE_URL}/db/import_csv", files=files)
            
        if response.status_code == 200:
            print("✅ Import Successful (Appended).")
            return True
        else:
            print(f"❌ Import Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if Path(filename).exists():
            Path(filename).unlink()

if __name__ == "__main__":
    if test_schema_refactor():
        print("\nTest Passed!")
    else:
        print("\nTest Failed!")
