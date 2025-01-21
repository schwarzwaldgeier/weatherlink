import os

from fastapi import FastAPI
from dotenv import load_dotenv

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


@app.get("/wind_records_html")
def get_wind_records_html(n: int):
    # Sample wind records for demonstration
    wind_records = [
        WindRecord(timestamp=1733742900, avg_speed=12, max_speed=18, avg_direction="N", max_direction="NNO"),
        WindRecord(timestamp=1733746500, avg_speed=10, max_speed=15, avg_direction="O", max_direction="ONO"),
        WindRecord(timestamp=1733750100, avg_speed=8, max_speed=12, avg_direction="S", max_direction="SSO")
    ]
    html_output = client.generate_wind_records_html(wind_records, n)
    return html_output
