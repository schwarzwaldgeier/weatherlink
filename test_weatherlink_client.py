import datetime
import math

import pytest

from weatherlink_client import WeatherlinkClient
from wind_record import WindRecord


class TestWeatherlinkClient:
    client: WeatherlinkClient

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = WeatherlinkClient(
            api_key="mvuzyka0gxwz6ij4mhxofwvrhvgopm7w",
            api_secret="jv4q3zthynysfu0d4dcwomwlza2ifcg2",
            station_id="2cd28dfa-e64f-4833-9a38-83b36c72b587"
        )

    def test_init(self):
        assert self.client.api_key == "mvuzyka0gxwz6ij4mhxofwvrhvgopm7w"

        assert self.client.station_id == "2cd28dfa-e64f-4833-9a38-83b36c72b587"
        assert self.client.base_url == "https://api.weatherlink.com/v2"
        assert self.client.headers == {
            "X-API-SECRET": self.client.api_secret
        }
        assert self.client.get_parameters == {"api-key": self.client.api_key}

    def test_get_current_conditions_not_mocked(self):
        response = self.client.get_current_conditions()
        assert response is not None
        assert 'timestamp' in response
        print(response)

    @pytest.mark.parametrize("deg, expected_direction", [
        (0, "N"),
        (9, "N"),
        (22, "NNO"),
        (45, "NO"),
        (67, "ONO"),
        (90, "O"),
        (112, "OSO"),
        (135, "SO"),
        (157, "SSO"),
        (180, "S"),
        (202, "SSW"),
        (225, "SW"),
        (247, "WSW"),
        (240, "WSW"),
        (270, "W"),
        (292, "WNW"),
        (315, "NW"),
        (337, "NNW"),
        (360, "N"),
    ])
    def test_convert_wind_dir(self, deg, expected_direction):
        assert self.client.convert_wind_dir(deg) == expected_direction

    def test_convert_wind_dir_invalid(self):
        with pytest.raises(ValueError):
            self.client.convert_wind_dir(-1)
        with pytest.raises(ValueError):
            self.client.convert_wind_dir(361)
        with pytest.raises(ValueError):
            self.client.convert_wind_dir(math.sqrt(-1))

    def test_get_current_conditions_mocked(self, requests_mock):
        sample_response = {
            "sensors": [
                {
                    "lsid": 795493,
                    "data": [
                        {
                            "ts": 1733742900,
                            "wind_dir": 240,
                            "wind_dir_of_gust_10_min": 360,
                            "wind_gust_10_min": 18,
                            "wind_speed": 12,
                            "wind_speed_2_min": 11.7,
                            "wind_speed_10_min": 10
                        }
                    ]
                }
            ],
            "generated_at": 1733813445
        }
        url = f"{self.client.base_url}/current/{self.client.station_id}?api-key={self.client.api_key}"
        requests_mock.get(url, json=sample_response)

        response = self.client.get_current_conditions()
        assert response['timestamp'] == 1733742900
        assert response['current_age'] == 70545
        assert response['wind_dir'] == 240
        assert response['wind_dir_of_gust_10_min'] == 360
        assert response['wind_gust_10_min'] == 18
        assert response['wind_speed'] == 12
        assert response['wind_speed_2_min'] == 11.7
        assert response['wind_speed_10_min'] == 10
        assert response['wind_dir_human'] == "WSW"

    def test_get_historic_data_not_mocked(self):
        now = int(datetime.datetime.now().timestamp())
        one_hour_ealier = now - 3600

        response = self.client.get_historic_data(one_hour_ealier, now)
        assert response is not None
        print(response)

    def test_get_sensor_catalog(self):
        response = self.client.get_sensor_catalog()
        assert response is not None
        print(response)

    def test_get_single_sensor_data(self):
        response = self.client.get_single_sensor_data(795493)
        assert response is not None

    def test_get_wind_speed(self):
        dataset = self.client.get_single_sensor_data(795493)
        wind_speed = self.client.get_wind_speed(dataset)
        assert wind_speed is not None
        print(wind_speed)

    def test_get_sensors_from_historic_data(self):
        now = int(datetime.datetime.now().timestamp())
        one_hour_ealier = now - 3600

        response = self.client.get_historic_data(one_hour_ealier, now)
        wind = self.client.get_wind_from_historic_data(response)
        assert wind is not None
        print(wind)

    def test_generate_wind_records_html(self):
        wind_records = [
            WindRecord(timestamp=1733742900, avg_speed=12, max_speed=18, avg_direction="N", max_direction="NNO"),
            WindRecord(timestamp=1733746500, avg_speed=10, max_speed=15, avg_direction="O", max_direction="ONO"),
            WindRecord(timestamp=1733750100, avg_speed=8, max_speed=12, avg_direction="S", max_direction="SSO")
        ]
        html_output = self.client.generate_wind_records_html(wind_records, 3)

        assert "<table border=\"1\">" in html_output
        assert "<th>Timestamp</th>" in html_output
        assert "<td>1733742900</td>" in html_output
        assert "<td>12</td>" in html_output
        assert "<td>18</td>" in html_output
        assert "<td>N ↑</td>" in html_output
        assert "<td>NNO ↑↗</td>" in html_output
        assert "<td>1733746500</td>" in html_output
        assert "<td>10</td>" in html_output
        assert "<td>15</td>" in html_output
        assert "<td>O →</td>" in html_output
        assert "<td>ONO ↗→</td>" in html_output
        assert "<td>1733750100</td>" in html_output
        assert "<td>8</td>" in html_output
        assert "<td>12</td>" in html_output
        assert "<td>S ↓</td>" in html_output
        assert "<td>SSO ↓↘</td>" in html_output

    def test_get_sensors_from_historic_data_html(self):
        now = int(datetime.datetime.now().timestamp())
        one_hour_ealier = now - 3600

        response = self.client.get_historic_data(one_hour_ealier, now)
        wind = self.client.get_wind_from_historic_data(response)
        assert wind is not None
        html = self.client.generate_wind_records_html(wind, len(wind))
        print(html)