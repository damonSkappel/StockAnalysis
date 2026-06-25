import pandas as pd
import yfinance as yf
import os
from sqlalchemy import create_engine, text


def download(bt_input):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DB_NAME = "stock.db"
    DB_FILE_PATH = os.path.join(BASE_DIR, DB_NAME)
    DB_PATH = f"sqlite:///{DB_FILE_PATH}"

    engine = create_engine(DB_PATH)
    with engine.connect() as connection:
        connection.execute(
            text(
                """CREATE TABLE IF NOT EXISTS ohlcv (
            Date TEXT NOT NULL,
            Ticker TEXT NOT NULL,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Volume REAL,
            PRIMARY KEY (Date, Ticker)
            )"""
            )
        )
        connection.commit()

    # This checks to see if the file is empty, if not is skips and nothign happens. Prevents errors
    if pd.read_sql("SELECT COUNT(*) FROM ohlcv", con=engine).iloc[0, 0] != 0:
        return

    df = yf.download(
        tickers=bt_input["ticker"],
        start=bt_input["start Date"],
        end=bt_input["end Date"],
        interval="1d",
        auto_adjust=True,
    )

    # convert wide to long format

    ohlcv = df.stack(level=1).reset_index()
    ohlcv["Date"] = ohlcv["Date"].astype(str)

    ohlcv.to_sql("ohlcv", con=engine, if_exists="append", index=False)
    return ohlcv
