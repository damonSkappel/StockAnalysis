import newsAPI
import finbert
import yahoo

bt_input = {'ticker': ["BA","UNH","MCD","HD"],
            'start Date' : '2026-01-01',
            'end Date' : '2026-06-19'}

yahoo.download(bt_input)
newsAPI.fetch_headlines(bt_input['ticker'])
finbert.sentiment_analysis()
    

