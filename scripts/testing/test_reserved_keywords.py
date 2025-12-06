import pandas as pd
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def test_reserved_keyword_import(filename="keyword_test.csv"):
    print(f"Generating test data with reserved keywords...")
    
    # 'default' is a reserved keyword in SQL
    # 'order' is also reserved
    data = {
        "person_income": [50000, 60000],
        "default": [0, 1],
        "order": [1, 2]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")
    
    try:
        # 1. Test with replace_schema=true (recreate table)
        print(f"\n1. Importing with replace_schema=true...")
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/csv")}
            response = requests.post(f"{BASE_URL}/db/import_csv?replace_schema=true", files=files)
            
        if response.status_code == 200:
            print("✅ Recreate Table Successful!")
        else:
            print(f"❌ Recreate Table Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False

        # 2. Test with replace_schema=false (append/add column)
        # We'll add a NEW reserved keyword column
        print(f"\n2. Adding new reserved keyword column...")
        
        data_2 = {
            "person_income": [70000],
            "group": ["A"] # 'group' is reserved
        }
        df2 = pd.DataFrame(data_2)
        filename2 = "keyword_test_2.csv"
        df2.to_csv(filename2, index=False)
        
        with open(filename2, "rb") as f:
            files = {"file": (filename2, f, "text/csv")}
            response = requests.post(f"{BASE_URL}/db/import_csv?replace_schema=false", files=files)
            
        if response.status_code == 200:
            print("✅ Add Column Successful!")
            return True
        else:
            print(f"❌ Add Column Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if Path(filename).exists():
            Path(filename).unlink()
        if Path("keyword_test_2.csv").exists():
            Path("keyword_test_2.csv").unlink()

if __name__ == "__main__":
    if test_reserved_keyword_import():
        print("\nTest Passed!")
    else:
        print("\nTest Failed!")
