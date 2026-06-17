# StockAnalysis Project Context

## What This Is

A personal learning project combining LSTM-based stock price prediction with FinBERT
sentiment analysis from financial news headlines. Built to learn full-stack ML, not
to actually beat the market.

## Notes for LLMs

you will not give me any code, or change any code, this is a learning project and so you will just help me figure out how to do different steps and give me resources on the web to learn.

## Tech Stack Decisions

- **Price data:** yfinance (free, no API key, sufficient for training)
- **News data:** NewsAPI only (Reddit was ruled out — their terms prohibit using
  data to train ML models)
- **Storage:** SQLite for development, will migrate to PostgreSQL at deploy
- **Model weights:** HuggingFace Hub (account: DamonSkap)
- **Sentiment model:** FinBERT out of the box (ProsusAI/finbert) — no fine-tuning yet
- **Prediction target:** Direction only (up/down), not price percentage — simpler
  and more honest framing
- **ML architecture:** Single LSTM to start, may upgrade to stacked LSTM or
  Transformer later
- **Fusion strategy:** Early fusion — sentiment score added as a feature column
  alongside price/technical indicators, not a separate model
- **Backend:** FastAPI (not built yet)
- **Frontend:** React + Plotly for candlestick charts (not built yet)
- **Hosting:** HuggingFace Spaces (backend) + Vercel (frontend), free tier, no
  real users expected
- **Automation:** GitHub Actions for scheduled daily data pulls (not implemented yet)

## Current State (Phase 1 — Complete)

Three working scripts:

- `yahoo.py` — fetches OHLCV data via yfinance, writes to `ohlcv` table, uses
  INSERT OR IGNORE pattern to handle duplicate Date+Ticker rows
- `newsAPI.py` — fetches headlines via NewsAPI using company names resolved
  dynamically from `yf.Ticker(ticker).info['shortName']`, writes to `headlines`
  table (primary key: URL + Ticker)
- `finbert.py` — reads headlines table, runs FinBERT sentiment-analysis pipeline
  in batches, writes labels/scores to `sentiment` table (includes Ticker, Date,
  URL, sentiment_label, sentiment_score)

## Database Schema

- `ohlcv`: Date, Ticker, Open, High, Low, Close, Volume — PK (Date, Ticker)
- `headlines`: Ticker, Headline, Source, Date, URL — PK (URL, Ticker)
- `sentiment`: headline_ticker, date, URL, sentiment_label, sentiment_score

## Known Gaps / Not Yet Handled

- No duplicate protection on `sentiment` table inserts (will crash on second run)
- No filtering to skip already-scored headlines (re-scores everything every run)
- No null/empty headline filtering before FinBERT
- Connection management between files works (passed in as parameter) but each
  script is run manually, not yet automated

## Next Phase — LSTM (Phase 2, in progress)

Building a PyTorch LSTM to predict next-day price direction (binary classification).
Key plan:

- Sequence length ~30 days lookback
- Features: OHLCV + technical indicators (RSI, MACD, Bollinger Bands, moving
  averages via pandas-ta) + FinBERT sentiment score, early-fused as input columns
- Chronological train/test split (no random split — avoids look-ahead bias)
- Normalize features with MinMaxScaler/StandardScaler before training
- Loss: BCELoss (binary classification)
- Device handling: cuda → mps → cpu fallback chain (dev on MacBook M5 MPS,
  training on workstation with RTX 4000 Ada GPUs available)
- SHAP explainability planned for later to surface feature importance in UI

## Environment Notes

- Using `.venv` virtual environment
- `TRANSFORMERS_OFFLINE=1` set in finbert.py to avoid network hangs once model
  is cached locally
- Had recurring SSL/KeyboardInterrupt issues tied to miniforge/conda Python
  conflicting with venv SSL cert loading — worth checking `certifi` install
  in venv if this resurfaces
- API keys stored in `.env`, loaded via python-dotenv
