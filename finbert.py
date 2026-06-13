import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
from transformers import pipeline



def sentiment_analysis():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DB_NAME = "stock.db"
    DB_FILE_PATH = os.path.join(BASE_DIR,DB_NAME)
    DB_PATH = f"sqlite:///{DB_FILE_PATH}"

    engine = create_engine(DB_PATH)

    query = "SELECT Ticker, Date, URL, Headline FROM headlines"
    df_headlines = pd.read_sql(query, con=engine)

    if df_headlines.empty:
        exit()

    nlp = pipeline(
        "sentiment-analysis",
        model="ProsusAI/finbert",
        tokenizer="ProsusAI/finbert"
    )

    headlines_list = df_headlines["Headline"].tolist()

    predictions = nlp(headlines_list, batch_size=32)

    df_sentiment= pd.DataFrame(
        {
            "headline_ticker": df_headlines["Ticker"],
            "date": df_headlines["Date"],
            "URL": df_headlines["URL"],
            "sentiment_label": [p["label"] for p in predictions],
            "sentiment_score": [p["score"] for p in predictions],
        }
    )

    df_sentiment.to_sql(name="sentiment", con=engine, if_exists="append", index=False)

