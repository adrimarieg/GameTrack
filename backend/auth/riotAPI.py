import requests
import time

class RiotAPIClient:
    def __init__(self, api_key, base_url="https://<region>.api.riotgames.com"):
        self.api_key = api_key #Change to OAuth token if I add sign on flow
        self.base_url = base_url
    
    def call_api(self, endpoint, params=None, headers=None, method="GET"):
        url = f"{self.base_url}{endpoint}"
        default_headers = {"X-Riot-Token": self.api_key}
        if headers:
            default_headers.update(headers)
        # print("Request URL:", url)
        # print("Headers:", default_headers)
        for attempt in range(3):
            response = requests.request(method, url, params=params, headers=default_headers)
            print("Status code:", response.status_code)
            # print("Response:", response.text)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))
                time.sleep(retry_after)
                continue
            elif response.status_code == 200:
                return response.json()
            else:
                break
        return None

