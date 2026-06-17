import pandas as pd
import yfinance as yf
import sqlite3
import newsAPI
import finbert

#backtest input tests

bt_input = {'ticker': ["BA","UNH","MCD","HD"],
            'start Date' : '2026-01-01',
            'end Date' : '2026-06-13'}

#Create an SQL connection 

con = sqlite3.connect('stock.db')
c = con.cursor()

#Create price table
query1 = '''CREATE TABLE IF NOT EXISTS ohlcv (
    Date TEXT NOT NULL,
    Ticker TEXT NOT NULL,
    Open REAL,
    High REAL,
    Low REAL,
    Close REAL,
    Volume REAL,
    PRIMARY KEY (Date, Ticker)
    )'''

query2 = '''CREATE TABLE IF NOT EXISTS headlines (
    Ticker TEXT,
    Headline TEXT,
    Source TEXT,
    Date TEXT,
    URL TEXT,
    PRIMARY KEY (URL, Ticker)
)'''




c.execute(query1)
c.execute(query2)
con.commit()




# print(dbCheck)

def download (bt_input):
    c.execute("SELECT COUNT(*) FROM ohlcv")
    row_count = c.fetchone()[0]
    if(row_count != 0):
        exit
    else:
        df = yf.download(
            tickers = bt_input['ticker'],
            start = bt_input['start Date'],
            end = bt_input['end Date'],
            interval = '1d',
            auto_adjust = True)


        #convert wide to long format

        ohlcv = df.stack(level=1).reset_index()
        ohlcv['Date'] = ohlcv['Date'].astype(str)

        ohlcv.to_sql('ohlcv', con, if_exists='append', index=False)
        return ohlcv

test = download(bt_input)

c.execute("SELECT COUNT(*) FROM headlines")
row_count = c.fetchone()[0]
if (row_count != 0):
    exit
else:
    newsAPI.fetch_headlines(bt_input['ticker'], con)
    finbert.sentiment_analysis()
con.close()

