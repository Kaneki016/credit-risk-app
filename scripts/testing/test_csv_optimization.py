import time
import pandas as pd
import requests
import numpy as np
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

def generate_large_csv(filename="large_test_data.csv", rows=5000):
    print(f"Generating {rows} rows of test data...")
    
    data = {
        "person_age": [np.nan if i % 100 == 0 else x for i, x in enumerate(np.random.randint(20, 70, rows))],
        "person_income": [np.nan if i % 100 == 1 else x for i, x in enumerate(np.random.randint(20000, 150000, rows))],
        "person_emp_length": np.random.randint(0, 40, rows),
        "loan_amnt": np.random.randint(1000, 50000, rows),
        "loan_int_rate": np.round(np.random.uniform(5.0, 25.0, rows), 2),
        "loan_percent_income": np.round(np.random.uniform(0.05, 0.5, rows), 2),
        "cb_person_cred_hist_length": np.random.randint(2, 30, rows),
        "loan_status": np.random.choice([0, 1], rows),
        "home_ownership": np.random.choice(["RENT", "OWN", "MORTGAGE", "OTHER"], rows),
        "loan_intent": np.random.choice(["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"], rows),
        "loan_grade": np.random.choice(["A", "B", "C", "D", "E", "F", "G"], rows),
        "cb_person_default_on_file": np.random.choice(["Y", "N"], rows)
    }
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")
    return filename

def test_import_performance(filename):
    print(f"\nTesting import performance with {filename}...")
    
    start_time = time.time()
    
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/csv")}
            # Use replace_schema=true to start fresh and test schema creation too
            response = requests.post(f"{BASE_URL}/db/import_csv?replace_schema=true", files=files)
            
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Import Successful!")
            print(f"Time taken: {duration:.2f} seconds")
            print(f"Response: {result}")
            return True
        else:
            print(f"❌ Import Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    filename = "large_test_data.csv"
    try:
        generate_large_csv(filename, rows=5000)
        success = test_import_performance(filename)
        
        if success:
            print("\nPerformance Test Passed!")
        else:
            print("\nPerformance Test Failed!")
            
    finally:
        # Cleanup
        if Path(filename).exists():
            try:
                Path(filename).unlink()
                print(f"Cleaned up {filename}")
            except:
                pass
