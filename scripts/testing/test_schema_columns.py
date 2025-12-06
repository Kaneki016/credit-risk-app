import pandas as pd
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def test_minimal_schema_import(filename="minimal_test.csv"):
    print(f"Generating minimal test data...")
    
    # Create a CSV with ONLY 'income' and 'loan_status'
    # This should result in a table with only these columns + metadata columns
    # It should NOT have 'person_age', 'loan_amnt', etc.
    data = {
        "person_income": [50000, 60000, 70000],
        "loan_status": [0, 1, 0]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")
    
    try:
        print(f"\nImporting {filename} with replace_schema=true...")
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/csv")}
            response = requests.post(f"{BASE_URL}/db/import_csv?replace_schema=true", files=files)
            
        if response.status_code == 200:
            print("✅ Import Successful!")
            
            # Verify Schema
            print("\nVerifying Schema...")
            schema_res = requests.get(f"{BASE_URL}/db/schema/loan_applications")
            if schema_res.status_code == 200:
                columns = schema_res.json()["columns"]
                print(f"Columns in DB: {columns}")
                
                # Check for absence of standard columns
                forbidden = ["person_age", "loan_amnt", "loan_grade"]
                present = [c for c in forbidden if c in columns]
                
                if not present:
                    print("✅ Verified: Standard columns are ABSENT.")
                    return True
                else:
                    print(f"❌ Failed: Found forbidden columns: {present}")
                    return False
            else:
                print(f"❌ Failed to get schema: {schema_res.status_code}")
                return False
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
    if test_minimal_schema_import():
        print("\nTest Passed!")
    else:
        print("\nTest Failed!")
