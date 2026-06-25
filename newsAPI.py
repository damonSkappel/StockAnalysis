import os
import pandas as pd
from dotenv import load_dotenv
from newsapi import NewsApiClient
import yfinance as yf
from sqlalchemy import create_engine, text

load_dotenv()
newsapi = NewsApiClient(api_key=os.getenv("newsapiAPIKEY"))


def fetch_headlines(tickers):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DB_NAME = "stock.db"
    DB_FILE_PATH = os.path.join(BASE_DIR, DB_NAME)
    DB_PATH = f"sqlite:///{DB_FILE_PATH}"

    engine = create_engine(DB_PATH)

    with engine.connect() as connection:
        connection.execute(
            text(
                """CREATE TABLE IF NOT EXISTS headlines (
            Ticker TEXT,
            Headline TEXT,
            Source TEXT,
            Date TEXT,
            URL TEXT,
            PRIMARY KEY (URL, Ticker)
        )"""
            )
        )
        connection.commit()

    # This checks to see if the file is empty, if not is skips and nothign happens. Prevents errors
    if pd.read_sql("SELECT COUNT(*) FROM headlines", con=engine).iloc[0, 0] != 0:
        return

    for ticker in tickers:
        company = yf.Ticker(ticker).info["shortName"]
        response = newsapi.get_everything(
            q=company, language="en", sort_by="publishedAt", page_size=100
        )

        articles = response["articles"]
        rows = []
        if response["status"] == "ok":
            for article in articles:
                rows.append(
                    {
                        "Ticker": ticker,
                        "Headline": article["title"],
                        "Source": article["source"]["name"],
                        "Date": article["publishedAt"][
                            0:10
                        ],  # only takes the first 10 characters so that the date looks the same as the one returned by yfinance.
                        "URL": article["url"],
                    }
                )
        else:
            print(response["code"])

        df = pd.DataFrame(rows)
        headlines_cleaned = df.dropna(subset=["Headline"])
        if not headlines_cleaned.empty:
            headlines_cleaned.to_sql(
                "headlines", con=engine, if_exists="append", index=False
            )


# TODO research newsapi to see if it holds dates from the past, so when I am testing on the past, I can use historical data. Also hook in the dates from main.py to use the same range of news.
