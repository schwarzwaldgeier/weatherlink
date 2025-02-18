from datetime import datetime, timedelta

from requests import get

from wind_record import WindRecord


class WeatherlinkClient:
    api_key: str
    api_secret: str
    station_id: str
    headers: dict
    base_url: str
    get_parameters: dict

    def __init__(self, api_key: str, api_secret: str, station_id: str, base_url="https://api.weatherlink.com/v2"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.station_id = station_id
        self.headers = {
            "X-API-SECRET": self.api_secret
        }
        self.base_url = base_url
        self.get_parameters = {"api-key": self.api_key}

    def get_current_conditions(self):
        params_str = "&".join([f"{key}={value}" for key, value in self.get_parameters.items()])
        url = f"{self.base_url}/current/{self.station_id}?{params_str}"
        response = get(url, headers=self.headers)
        data = response.json()

        sensor_data = data['sensors'][0]['data'][0]
        result = {
            'timestamp': sensor_data['ts'],
            'current_age': data['generated_at'] - sensor_data['ts'],
            'wind_dir': sensor_data.get('wind_dir'),
            'wind_dir_of_gust_10_min': sensor_data.get('wind_dir_of_gust_10_min'),
            'wind_gust_10_min': sensor_data.get('wind_gust_10_min'),
            'wind_speed': sensor_data.get('wind_speed'),
            'wind_speed_2_min': sensor_data.get('wind_speed_2_min'),
            'wind_speed_10_min': sensor_data.get('wind_speed_10_min')
        }

        if result['wind_dir'] is not None:
            result['wind_dir_human'] = self.convert_wind_dir(result['wind_dir'])

        return result

    def get_historic_data(self, start_ts: int, end_ts: int):
        params = {**self.get_parameters, "start-timestamp": start_ts, "end-timestamp": end_ts}
        params_str = "&".join([f"{key}={value}" for key, value in params.items()])
        print(params_str)
        url = (f"{self.base_url}/historic/"
               f"{self.station_id}?{params_str}&start-timestamp={start_ts}&end-timestamp={end_ts}")
        response = get(url, headers=self.headers)
        data = response.json()
        return data

    def get_wind_from_historic_data(self, historic_data):

        sensors = []
        wind_records = []
        for sensor in historic_data['sensors']:
            sensors.append(sensor)

            if sensor["sensor_type"] == 27:
                data = sensor['data']
                for dataset in data:
                    print(dataset)
                    timestamp = dataset.get('ts')
                    wind_speed_avg = dataset.get('wind_speed_avg')
                    wind_speed_hi = dataset.get('wind_speed_hi')
                    wind_dir_of_hi = dataset.get('wind_dir_of_hi')
                    wind_dir_of_prevail = dataset.get('wind_dir_of_prevail')
                    record = WindRecord(timestamp=timestamp,
                                        avg_speed=self.mph_to_kph(wind_speed_avg),
                                        max_speed=self.mph_to_kph(wind_speed_hi),
                                        avg_direction=wind_dir_of_prevail,
                                        max_direction=wind_dir_of_hi)
                    wind_records.append(record)

        wind_records.sort(key=lambda x: x.timestamp, reverse=True)
        return wind_records

    # @lru_cache
    def get_sensors_data(self, sensor_id_list):
        sensors_list_comma_separated = ",".join(map(str, sensor_id_list))
        params_str = "&".join([f"{key}={value}" for key, value in self.get_parameters.items()])
        url = f"{self.base_url}/sensors/{str(sensors_list_comma_separated)}?{params_str}"
        response = get(url, headers=self.headers)
        data = response.json()
        return data

    def get_single_sensor_data(self, sensor_id):
        params_str = "&".join([f"{key}={value}" for key, value in self.get_parameters.items()])
        url = f"{self.base_url}/sensors/{sensor_id}?{params_str}"
        response = get(url, headers=self.headers)
        data = response.json()
        return data

    def get_wind_speed(self, single_sensor_data_response):
        return single_sensor_data_response['sensors'][0]['wind_speed']

    def get_sensor_catalog(self):
        params_str = "&".join([f"{key}={value}" for key, value in self.get_parameters.items()])
        url = f"{self.base_url}/sensor-catalog?{params_str}"
        response = get(url, headers=self.headers)
        data = response.json()
        return data

    def convert_wind_dir(self, ordinal: int) -> str:
        if ordinal < 0 or ordinal > 15:
            raise ValueError("Must be a value between 0 and 15")
        directions = [
            "N", "NNO", "NO", "ONO", "O", "OSO", "SO", "SSO",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
        ]

        return directions[ordinal]

    def mph_to_kph(self, mph: float, precision=0) -> float:
        kph = mph * 1.60934
        return round(kph, precision)

    def inches_of_mercury_to_hpa(self, inches: float) -> float:
        return inches * 33.8639

    def generate_wind_records_html(self, wind_records, n):

        html = """<!doctype html>
<html>
        <head>
            <title>
            Wetter Merkur
            </title>
        </head>
        <body>
        <style>
    table {
        width: 90%;
        border-collapse: collapse;
    }
    th, td {
        padding: 8px 12px;
        border: 1px solid #ddd;
        text-align: center;
    }
    th {
        background-color: #f2f2f2;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    tr:nth-child(2) {
    font-size: 150%;
    }
    
    .speed {
        font-size: 150%;   
    }
    
    .direction {
        font-size: 150%;   
        
    }
</style>
        <table border="1" >
            <tr>
                <th>&nbsp;</th>
                <th>Wind Ø</th>
                <th>Wind max.</th>
            </tr>
        """

        arrow_svg_template = """
                    <svg 
                   
                    width="65"
                    viewBox="0 0 100 75" 
                    xmlns="http://www.w3.org/2000/svg">
                      <g transform="rotate({rotation}, 50, 50)">
                        <polygon points="50,15 60,50 50,40 40,50" fill="black" />
                      </g>
                    </svg>
                    """
        td_template = ("""
        <td 
            style="vertical-align: middle; font-size: 1.2em;">
            <span class="speed">
                {speed}
            </span>&nbsp;km/h&nbsp;

            <span class="direction">
                {direction} {svg}
            </span>
        </td>
        """)

        rotation = 22.5
        for record in wind_records[:n]:
            avg_direction_svg = arrow_svg_template.format(rotation=record.avg_direction * rotation + 180)
            max_direction_svg = arrow_svg_template.format(rotation=record.max_direction * rotation + 180)

            avg_td = td_template.format(speed=int(record.avg_speed),
                                        direction=self.convert_wind_dir(record.avg_direction), svg=avg_direction_svg)
            max_td = td_template.format(speed=int(record.max_speed),
                                        direction=self.convert_wind_dir(record.max_direction), svg=max_direction_svg)

            html += f"""
            <tr>
                <td><span>{(datetime.fromtimestamp(record.timestamp)
                      + timedelta(hours=1)).strftime('%H:%M')}</span></td>
                {avg_td}
                {max_td}
            </tr>
            """

        html += "</table></body></html>"
        return html
