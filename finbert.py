import os

os.environ["TRANSFORMERS_OFFLINE"] = "1"
import pandas as pd
from sqlalchemy import create_engine, text
from transformers import pipeline


def sentiment_analysis():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DB_NAME = "stock.db"
    DB_FILE_PATH = os.path.join(BASE_DIR, DB_NAME)
    DB_PATH = f"sqlite:///{DB_FILE_PATH}"

    engine = create_engine(DB_PATH)

    query = "SELECT Ticker, Date, URL, Headline FROM headlines"
    df_headlines = pd.read_sql(query, con=engine)

    if df_headlines.empty:
        return

    with engine.connect() as connection:
        connection.execute(
            text(
                """CREATE TABLE IF NOT EXISTS sentiment (
            headline_ticker TEXT,
            date TEXT,
            URL TEXT,
            sentiment_label TEXT,
            sentiment_score REAL,
            PRIMARY KEY (URL, headline_ticker)
        )"""
            )
        )
        connection.commit()

    # This checks to see if the file is empty, if not is skips and nothign happens. Prevents errors
    if pd.read_sql("SELECT COUNT(*) FROM sentiment", con=engine).iloc[0, 0] != 0:
        return

    # TODO: add the filter of .isin to check if what I am trying to analyize is already in the table.
    # This would come into play if I added a ticker adn wanted teh sentiment on it as well,
    # then it wouldn't skip everything and it would add these to the end.

    nlp = pipeline(
        "sentiment-analysis", model="ProsusAI/finbert", tokenizer="ProsusAI/finbert"
    )

    headlines_list = df_headlines["Headline"].tolist()

    predictions = nlp(headlines_list, batch_size=32)

    df_sentiment = pd.DataFrame(
        {
            "headline_ticker": df_headlines["Ticker"],
            "date": df_headlines["Date"],
            "URL": df_headlines["URL"],
            "sentiment_label": [p["label"] for p in predictions],
            "sentiment_score": [p["score"] for p in predictions],
        }
    )

    df_sentiment.to_sql(name="sentiment", con=engine, if_exists="append", index=False)
