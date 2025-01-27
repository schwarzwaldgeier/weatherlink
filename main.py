import os
from datetime import datetime

from fastapi import FastAPI
from dotenv import load_dotenv
from starlette.responses import HTMLResponse

# Initialize the WeatherlinkClient with your credentials

from weatherlink_client import WeatherlinkClient, WindRecord

app = FastAPI()

# Initialize the WeatherlinkClient with your credentials
# Load environment variables from .env file
load_dotenv()

# Initialize the WeatherlinkClient with your credentials
client = WeatherlinkClient(
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    station_id=os.getenv("STATION_ID")
)


@app.get("/html", response_class=HTMLResponse)
def get_wind_records_html(n: int = 10):
    now = int(datetime.now().timestamp())
    one_hour_earlier = now - 3600 * 24
    historic_data = client.get_historic_data(one_hour_earlier, now)
    wind_records = client.get_wind_from_historic_data(historic_data)
    html_output = client.generate_wind_records_html(wind_records, n)
    return html_output


@app.get("/json")
def get_wind_records_json(n: int = 10):
    now = int(datetime.now().timestamp())
    one_hour_earlier = now - 3600
    historic_data = client.get_historic_data(one_hour_earlier, now)
    wind_records = client.get_wind_from_historic_data(historic_data)
    return wind_records
