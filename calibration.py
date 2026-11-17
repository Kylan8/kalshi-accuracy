from datetime import datetime, timezone
import pandas as pd
from kalshi_client import KalshiClient
import numpy as np

class CalibrationAnalyzer:
    SPLIT = 0.5
    BID_ASK_THRESHOLD = 0.1
    
    def __init__(self):
        self.client = KalshiClient()

    def get_compare_candlestick(self, series_ticker, ticker, start_ts, end_ts, period_interval=1):
        candlestick_timestamp = start_ts + int(self.SPLIT * (end_ts - start_ts))
        compare_candlesticks = self.client.get_candlesticks(series_ticker, ticker, candlestick_timestamp - period_interval*60, candlestick_timestamp, period_interval)

        curr_candlestick = None
        for candlestick in compare_candlesticks:
            if candlestick["end_period_ts"] <= candlestick_timestamp:
                curr_candlestick = candlestick
            else:
                break

        return curr_candlestick

    def get_compare_probability(self, compare_candlestick):
        bid_raw = compare_candlestick.get('yes_bid', {}).get('close_dollars')
        ask_raw = compare_candlestick.get('yes_ask', {}).get('close_dollars')

        if not bid_raw or not ask_raw:
            return None
        
        bid_price = float(compare_candlestick['yes_bid']['close_dollars'])
        ask_price = float(compare_candlestick['yes_ask']['close_dollars'])

        if ask_price - bid_price >= self.BID_ASK_THRESHOLD:
            return None

        probability = (bid_price + ask_price) / 2
        return probability

    def convert_timestamp_to_unix(self, timestamp):
        return int(pd.to_datetime(timestamp).timestamp())

    def generate_probabilities_df(self, series_ticker, page_size=100, status="settled", max_markets=500, period_interval=1):
        markets = pd.DataFrame(self.client.get_markets(series_ticker, page_size, status, max_markets))

        markets_data = {
            "ticker": [],
            "probability_at_split": [],
            "outcome": []
        }

        for market in markets:
            ticker = market['ticker']
            start_ts = self.convert_timestamp_to_unix(market["open_time"])
            end_ts = self.convert_timestamp_to_unix(market["close_time"])
            curr_candlestick = self.get_compare_candlestick(series_ticker, ticker, start_ts, end_ts, period_interval)

            if not curr_candlestick:
                continue

            p = self.get_compare_probability(curr_candlestick)

            if not p:
                continue

            outcome = market['result']

            markets_data["ticker"].append(ticker)
            markets_data["probability_at_split"].append(p)
            if outcome == "yes":
                markets_data["outcome"].append(1)
            else:
                markets_data["outcome"].append(0)

        return pd.DataFrame(markets_data)

    def get_probs_buckets(self, markets_data):
        markets_data["bins"] = pd.cut(markets_data["probability_at_split"], np.linspace(0, 1, 10), include_lowest=True)
        markets_data = markets_data.groupby("bins", observed=False).agg(
            avg_probability=("probability_at_split", "mean"),
            observed_frequency=("outcome", "mean"),
            count=("probability_at_split", "count")
        )

    def get_brier_score(self, markets_data):
        
        




    
