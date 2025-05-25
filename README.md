Fetch real‑time market data, pull the latest Yahoo Finance headlines, score each story’s sentiment, and let an LLM rank the news by its likely impact on the stock.

> **Why another scraper?**  
> Yahoo’s HTML keeps changing, so the project now relies on the much more stable *yfinance* JSON endpoints for prices **and** news items.  
> Everything else—sentiment analysis, ranking, and charting—happens locally.

## Features
- **Real‑time quotes** – get the current price directly from Yahoo Finance.  
- **News retrieval** – pull in up‑to‑the‑minute articles for any ticker.  
- **Headline sentiment** – score each story with *TextBlob*.  
- **AI article ranking** – call OpenAI to order stories by potential impact.  
- **Historical charts** – visualize price history with Matplotlib. :contentReference[oaicite:0]{index=0}  

## Quick‑start (CLI or Flask)

```bash
# 1. Clone & create an isolated env
git clone https://github.com/blee1616/PythonWebScraper.git
cd PythonWebScraper
python -m venv .venv && source .venv/bin/activate        # Windows? .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your OpenAI key (bash)
export OPENAI_API_KEY="sk‑..."

# 4a. Run the Flask web app
python app.py              # then open http://127.0.0.1:5000

# 4b. —or— run the stand‑alone script
python old.py --ticker AAPL --days 90
