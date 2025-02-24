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
property_id = os.getenv("PROPERTY_ID")
print(property_id)

# Ensure environment variables are set
if not ga4_json_credentials:
    raise ValueError("GA4_CREDENTIALS_JSON environment variable is missing!")
if not property_id:
    raise ValueError("PROPERTY_ID environment variable is missing!")

# Load credentials from JSON
try:
    credentials_info = json.loads(ga4_json_credentials)
    #credentials = service_account.Credentials.from_service_account_file(credentials_path)
    print("✅ Successfully loaded JSON credentials!")
except json.JSONDecodeError as e:
    raise ValueError(f"❌ JSON decoding error: {e}")

# Authenticate using the credentials
credentials = service_account.Credentials.from_service_account_info(credentials_info)

# Function to fetch GA4 data
# https://cloud.google.com/php/docs/reference/analytics-data/0.20.1/V1beta.DateRange
'''def get_ga4_data():
    """Retrieve data from GA4 API"""
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="sessions")],
        date_ranges=[DateRange(start_date="2023-01-01", end_date="today")],
    )
    response = client.run_report(request)
    
    data = [
        {"city": row.dimension_values[0].value, "sessions": int(row.metric_values[0].value)}
        for row in response.rows
    ]
    return data'''
from google.analytics.data_v1beta import BetaAnalyticsDataClient, RunReportRequest, Dimension, Metric, DateRange

def get_ga4_data():
    """Retrieve data from GA4 API with additional metrics and dimensions"""
    client = BetaAnalyticsDataClient(credentials=credentials)
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[
            Dimension(name="city"),
            Dimension(name="country"),
            Dimension(name="deviceCategory"),
            Dimension(name="date")  # Adding time granularity
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="bounceRate")
        ],
        date_ranges=[DateRange(start_date="2023-01-01", end_date="today")],
    )
    
    response = client.run_report(request)
    
    data = [
        {
            "city": row.dimension_values[0].value,
            "country": row.dimension_values[1].value,
            "deviceCategory": row.dimension_values[2].value,
            "date": row.dimension_values[3].value,
            "sessions": int(row.metric_values[0].value),
            "activeUsers": int(row.metric_values[1].value),
            "bounceRate": float(row.metric_values[2].value)
        }
        for row in response.rows
    ]
    
    return data

@app.get("/")
def home():
    return {"message": "Welcome to the GA4 Data API"}

@app.get("/get_ga4_data")
def get_data():
    """Provides GA4 data via API."""
    try:
        data = get_ga4_data()
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
