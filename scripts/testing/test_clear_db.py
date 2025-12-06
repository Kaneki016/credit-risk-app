import pandas as pd
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def test_clear_db_with_dynamic_schema(filename="clear_test.csv"):
    print(f"Generating minimal test data...")
    
    # Create a CSV with minimal columns
    data = {
        "person_income": [50000],
        "loan_status": [0]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    
    try:
        # 1. Import to set up dynamic schema
        print(f"\n1. Importing to set up dynamic schema...")
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/csv")}
            response = requests.post(f"{BASE_URL}/db/import_csv?replace_schema=true", files=files)
            
        if response.status_code != 200:
            print(f"❌ Import Failed: {response.status_code}")
            return False
            
        print("✅ Import Successful. Schema is now dynamic.")

        # 2. Try to clear database
        print(f"\n2. Clearing database...")
        response = requests.delete(f"{BASE_URL}/db/clear?confirm=true")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Clear Database Successful!")
            print(f"Deleted: {result['deleted']}")
            return True
        else:
            print(f"❌ Clear Database Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if Path(filename).exists():
            Path(filename).unlink()

if __name__ == "__main__":
    if test_clear_db_with_dynamic_schema():
        print("\nTest Passed!")
    else:
        print("\nTest Failed!")
