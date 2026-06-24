import os

import pandas as pd
from sqlalchemy import create_engine


#This is going to be where I write all of the code to get the LSTM Model working

#TODO: Read from ohlcv and sentiment, join them on Date + Ticker
    #what to do with days with no headlines
    #Get each date down to 1 row in sentiment. Positive, neutral, negative. Majority wins. 
    #actually figure out how to join the tables 
    #probably don't need to make this its own table, just a pandas dataframe. 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = "stock.db"
DB_FILE_PATH = os.path.join(BASE_DIR,DB_NAME)
DB_PATH = f"sqlite:///{DB_FILE_PATH}"

engine = create_engine(DB_PATH)

query = "SELECT * FROM sentiment"
df_sentiment = pd.read_sql(query, con=engine)

top_sentiment = df_sentiment.groupby(['date', 'headline_ticker'])['sentiment_label'].agg(lambda x: x.value_counts().idxmax()).reset_index(name='most_sentiment')

query2 = "SELECT * FROM ohlcv"
df_ohlcv = pd.read_sql(query2, con=engine)

df_joined = pd.merge(df_ohlcv, top_sentiment, left_on=  ['Date' , 'Ticker'], right_on=['date', 'headline_ticker'], how= 'left')

print(df_joined)



#TODO: Add technical indicators (RSI, MACD, etc) with pandas-ta on top of the ohlcv data

#TODO: Normalize the features

#TODO: Build sequences (Sliding windows of 30 days -> one label each)

#TODO: Split chronologically inot train/test

#TODO: Define, train, and evaluate the model. 