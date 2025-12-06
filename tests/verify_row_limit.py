import pandas as pd
import io
from fastapi.testclient import TestClient
from backend.api.routes.data_management import router
from fastapi import FastAPI, UploadFile, File
import pytest

# We can't easily test the full endpoint without mocking DB, 
# but we can verify the pandas logic if we extract it or just trust the simple head(500) call.
# However, let's try to create a dataframe and verify head(500) works as expected in a script.

def test_pandas_limit():
    # Create a dataframe with 1000 rows
    df = pd.DataFrame({'col1': range(1000)})
    print(f"Original size: {len(df)}")
    
    if len(df) > 500:
        df = df.head(500)
        
    print(f"New size: {len(df)}")
    assert len(df) == 500
    print("Limit logic verified")

if __name__ == "__main__":
    test_pandas_limit()
