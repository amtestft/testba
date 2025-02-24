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
# ga4_json_credentials = os.getenv("GA4_CREDENTIALS_JSON")
property_id = os.getenv("PROPERTY_ID")
print(property_id)

# Ensure environment variables are set
'''if not ga4_json_credentials:
    raise ValueError("GA4_CREDENTIALS_JSON environment variable is missing!")
if not property_id:
    raise ValueError("PROPERTY_ID environment variable is missing!")
'''

credentials_path = "/etc/secrets/ga4_credentials.json"

# Load and read the JSON file
try:
    with open(credentials_path, "r") as file:
        credentials_data = json.load(file)  # Load as JSON object

    # Print first 100 lines (limiting output for readability)
    credentials_str = json.dumps(credentials_data, indent=2)
    lines = credentials_str.split("\n")  # Split by line
    for i, line in enumerate(lines[:100]):  # Limit to first 100 rows
        print(line)
except Exception as e:
    print(f"Error loading JSON: {e}")

if not os.path.exists(credentials_path):
    raise ValueError("GA4 credentials file is missing!")

# Load credentials from JSON
try:
    #credentials_info = json.loads(ga4_json_credentials)
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    print("✅ Successfully loaded JSON credentials!")
except json.JSONDecodeError as e:
    raise ValueError(f"❌ JSON decoding error: {e}")

# Authenticate using the credentials
#credentials = service_account.Credentials.from_service_account_info(credentials_info)

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
