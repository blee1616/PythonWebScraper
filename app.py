from flask import Flask, render_template, jsonify, request
import pandas as pd
import requests
from io import StringIO
import json
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download NLTK resources (only needed once)
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze/<ticker>')
def analyze(ticker):
    ticker = ticker.strip().upper()
    
    # Get current price
    current_price = fetch_stock_price(ticker)
    
    # Get articles and sentiment
    articles_list = fetch_articles(ticker)
    article_data = []
    
    if articles_list:
        sentiments = analyze_sentiment(articles_list)
        for article, sentiment in sentiments:
            article_data.append({
                'title': article,
                'sentiment': sentiment
            })
    
    # Get historical prices
    historical_data = get_historical_data(ticker)
    
    return jsonify({
        'current_price': current_price,
        'articles': article_data,
        'historical_prices': historical_data
    })

def fetch_stock_price(ticker):
    """Fetch current stock price from Yahoo Finance"""
    url = f"https://finance.yahoo.com/quote/{ticker}"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            # Extract price using regex
            price_pattern = r'"regularMarketPrice":{"raw":([0-9\.]+),'
            match = re.search(price_pattern, response.text)
            if match:
                return float(match.group(1))
    except Exception as e:
        print(f"Error fetching stock price: {e}")
    return "N/A"

def fetch_articles(ticker, limit=5):
    """Fetch news articles about the given ticker"""
    url = f"https://finance.yahoo.com/quote/{ticker}/news"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            # Extract headlines using regex
            headline_pattern = r'<h3 class="Mb\(5px\)">(.*?)</h3>'
            headlines = re.findall(headline_pattern, response.text, re.DOTALL)
            # Clean up headlines
            headlines = [re.sub(r'<.*?>', '', h).strip() for h in headlines]
            return headlines[:limit]
    except Exception as e:
        print(f"Error fetching articles: {e}")
    return []

def analyze_sentiment(articles):
    """Analyze sentiment of the given articles"""
    sid = SentimentIntensityAnalyzer()
    results = []
    
    for article in articles:
        sentiment_score = sid.polarity_scores(article)
        compound = sentiment_score['compound']
        
        if compound >= 0.05:
            sentiment = "Positive"
        elif compound <= -0.05:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
            
        results.append((article, sentiment))
    
    return results

def get_historical_data(ticker):
    """Fetch historical stock price data"""
    # Using Yahoo Finance API to get 1 year of data
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1=1640995200&period2=1672531200&interval=1d&events=history"
    
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Format dates for frontend
            dates = df['Date'].dt.strftime('%Y-%m-%d').tolist()
            prices = df['Close'].tolist()
            
            return {
                'dates': dates,
                'prices': prices
            }
    except Exception as e:
        print(f"Error fetching historical data: {e}")
    
    return {
        'dates': [],
        'prices': []
    }

if __name__ == '__main__':
    app.run(debug=True)