import os
import pandas as pd
from dotenv import load_dotenv
from newsapi import NewsApiClient
import sqlite3
import yfinance as yf

load_dotenv()
newsapi = NewsApiClient(api_key=os.getenv('newsapiAPIKEY'))


def fetch_headlines(tickers, con: sqlite3.Connection):
    c = con.cursor()
    for ticker in tickers:
        company = yf.Ticker(ticker).info['shortName']
        response = newsapi.get_everything(
            q=company,
            language='en',
            sort_by='publishedAt',
            page_size=100
        )

        articles = response['articles']
        rows = []
        if response['status'] == 'ok':
            for article in articles:
                rows.append({
                    'Ticker': ticker,
                    'Headline': article['title'],
                    'Source': article['source']['name'],
                    'Date': article['publishedAt'],
                    'URL': article['url']
                })
        else: 
            print(response['code'])        

        df = pd.DataFrame(rows)
        if not df.empty:
            df.to_sql('headlines' , con, if_exists='append', index=False)

