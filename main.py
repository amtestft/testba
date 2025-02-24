'''from typing import Optional

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
    '''
from fastapi import FastAPI, HTTPException
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account
import os
import json

app = FastAPI()

# Retrieve JSON credentials from environment variable
ga4_json_credentials = os.getenv("GA4_CREDENTIALS_JSON")
# property_id = os.getenv("PROPERTY_ID")
property_id = "477023147"

# Ensure environment variables are set
if not ga4_json_credentials:
    raise ValueError("GA4_CREDENTIALS_JSON environment variable is missing!")
if not property_id:
    raise ValueError("PROPERTY_ID environment variable is missing!")

# Load credentials from JSON
try:
    credentials_info = json.loads(ga4_json_credentials)
    print("✅ Successfully loaded JSON credentials!")
except json.JSONDecodeError as e:
    raise ValueError(f"❌ JSON decoding error: {e}")

# Authenticate using the credentials
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Function to fetch GA4 data
def get_ga4_data():
    """Retrieve data from GA4 API"""
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
    )
    response = client.run_report(request)
    
    data = [
        {"city": row.dimension_values[0].value, "sessions": int(row.metric_values[0].value)}
        for row in response.rows
    ]
    return data

@app.get("/get_ga4_data")
def get_data():
    """Provides GA4 data via API."""
    try:
        data = get_ga4_data()
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
