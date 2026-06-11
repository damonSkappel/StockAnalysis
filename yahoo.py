import pandas as pd
import yfinance as yf
import sqlite3

#backtest input tests

bt_input = {'ticker': ["BA","UNH","MCD","HD"],
            'start Date' : '2019-01-01',
            'end Date' : '2019-06-01'}

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


def download (bt_input):
    df = yf.download(
        tickers = bt_input['ticker'],
        start = bt_input['start Date'],
        end = bt_input['end Date'],
        interval = '1d',
        auto_adjust = False)
    
    adj_close = df['Adj Close']
    high = df['High']
    low = df['Low']
    open_price = df['Open']
    volume = df['Volume']

    #convert wide to long format

    ohlcv = df.stack(level=1).reset_index()
    ohlcv.columns = ['Date', 'Ticker', 'Close', 'High', 'Low', 'Open', 'Volume', 'Primary Key']
    ohlcv['Date'] = ohlcv['Date'].astype(str)

    ohlcv.to_sql('ohlcv', con, if_exists='append', index=False)
    return ohlcv

test = download(bt_input)
con.close()
