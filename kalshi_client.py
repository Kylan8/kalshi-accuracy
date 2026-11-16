import pandas as pd
import requests
import time
from datetime import datetime, timezone

class KalshiClient:
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

    def __init__(self):
        self.session = requests.Session()

    
    def get_markets(self, series_ticker, page_size=100, status="settled", max_markets=500):
        params = {"limit": page_size, "status": status, "mve_filter": "exclude", "series_ticker": series_ticker}
        all_markets = []

        while True:
            time.sleep(0.2)
            resp = self.session.get(f"{self.BASE_URL}/markets", params=params)
            resp.raise_for_status()
            data = resp.json()

            all_markets.extend(data["markets"])

            curr_cursor = data["cursor"]

            if not curr_cursor:
                break

            if len(all_markets) >= max_markets:
                break

            params["cursor"] = curr_cursor

        return all_markets

    def get_candlesticks(self, series_ticker, ticker, start_ts, end_ts, period_interval=1):
        
        candlestick_url = f"/series/{series_ticker}/markets/{ticker}/candlesticks"
        candlestick_request_params = {"period_interval": period_interval, "start_ts": start_ts, "end_ts": end_ts}
    
        candlestick_response = self.session.get(f"{self.BASE_URL}{candlestick_url}", params=candlestick_request_params)

        candlestick_response.raise_for_status()
        candlestick_data = candlestick_response.json()

        return candlestick_data["candlesticks"]

