import os

import pandas as pd
import pandas_ta as ta
from sqlalchemy import create_engine


def compute_lstm():
    # These lines read in the path to the database and create the engine to query it
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_NAME = "stock.db"
    DB_FILE_PATH = os.path.join(BASE_DIR, DB_NAME)
    DB_PATH = f"sqlite:///{DB_FILE_PATH}"
    engine = create_engine(DB_PATH)

    query = "SELECT * FROM sentiment"
    df_sentiment = pd.read_sql(query, con=engine)

    # This takes the raw data from the sentiment df and for each day and ticker gives me the sentiment that showed up the most that day.
    top_sentiment = (
        df_sentiment.groupby(["date", "headline_ticker"])["sentiment_label"]
        .agg(lambda x: x.value_counts().idxmax())
        .reset_index(name="most_sentiment")
    )

    query2 = "SELECT * FROM ohlcv"
    df_ohlcv = pd.read_sql(query2, con=engine)

    # TODO: Add technical indicators (RSI, MACD, etc) with pandas-ta on top of the ohlcv data

    # This loop takes the ohlcv and groups it by ticker, then for each group it does the technical analysis on it. Then it appends it to the list. This gives me list of the tickers in order and with the technical indicators on them.
    group_list = []
    for ticker, group in df_ohlcv.groupby("Ticker"):
        group = group.assign(rsi=ta.rsi(close=group["Close"], length=14))
        group = pd.concat(
            [group, ta.macd(close=group["Close"], fast=12, slow=26, signal=9)],
            axis=1,
        )

        group = pd.concat(
            [group, ta.bbands(close=group["Close"], length=20, std=2)],
            axis=1,
        )

        group_list.append(group)

    df_ohlcv = pd.concat(group_list)

    # This is where I joined the two tables together on date and ticker, do after the adding technical indicators
    df_joined = pd.merge(
        df_ohlcv,
        top_sentiment,
        left_on=["Date", "Ticker"],
        right_on=["date", "headline_ticker"],
        how="left",
    )

    print(df_joined)


# TODO: fill in the NaN in top_sentiment with neutral. fillna('neutral') is not working

# TODO: Normalize the features

# TODO: Build sequences (Sliding windows of 30 days -> one label each)

# TODO: Split chronologically inot train/test

# TODO: Define, train, and evaluate the model.
