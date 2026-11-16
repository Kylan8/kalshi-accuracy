import pandas as pd
import requests
import time
from datetime import datetime, timezone

url = "https://api.elections.kalshi.com/trade-api/v2"
params = {"limit": 100, "status": "settled", "mve_filter": "exclude", "series_ticker": "KXGOLD15M"}

all_markets = []

while True:
    time.sleep(0.2)
    resp = requests.get(f"{url}/markets", params=params)
    data = resp.json()

    all_markets.extend(data["markets"])

    curr_cursor = data["cursor"]

    if not curr_cursor:
        break

    if len(all_markets) >= 500:
        break

    params["cursor"] = curr_cursor

df = pd.DataFrame(all_markets)
print(df.shape)
print(df["result"].value_counts())

ticker = df.iloc[0]["ticker"]
ticker_close_time = df.iloc[0]["close_time"]
series_ticker = df.iloc[0]["event_ticker"].split('-', 1)[0]

end_timestamp = int(pd.to_datetime(ticker_close_time).timestamp())
start_timestamp = end_timestamp - 900

halfway_timestamp = (end_timestamp + start_timestamp) // 2

candlestick_url = f"/series/{series_ticker}/markets/{ticker}/candlesticks"
candlestick_request_params = {"period_interval": 1, "start_ts": halfway_timestamp - 60, "end_ts": halfway_timestamp}

candlestick_response = requests.get(f"{url}{candlestick_url}", params=candlestick_request_params)
candlestick_data = candlestick_response.json()

end_unix_timestamp = candlestick_data["candlesticks"][0]["end_period_ts"]

print(candlestick_data["candlesticks"][0]["yes_ask"], candlestick_data["candlesticks"][0]["yes_bid"])

end_timestamp = datetime.fromtimestamp(end_unix_timestamp, tz=timezone.utc)

