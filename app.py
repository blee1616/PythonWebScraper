from flask import Flask, render_template, jsonify, request
import pandas as pd
import yfinance as yf
import json
from textblob import TextBlob
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze/<ticker>')
def analyze(ticker):
    ticker = ticker.strip().upper()
    
    stock = yf.Ticker(ticker)
    
    current_price = fetch_stock_price(stock)
    
    articles_list = fetch_articles(stock)
    article_data = []
    
    if articles_list:
        sentiments = analyze_sentiment(articles_list)
        for title, sentiment in sentiments:
            article_data.append({
                'title': title,
                'sentiment': sentiment
            })
    
    historical_data = get_historical_data(stock)
    
    return jsonify({
        'current_price': current_price,
        'articles': article_data,
        'historical_prices': historical_data
    })

def fetch_stock_price(stock):
    """Gets the latest stock price using yfinance"""
    try:
        info = stock.info
        return str(info.get('regularMarketPrice', 'Price not found'))
    except Exception as e:
        print(f"Error fetching stock price: {e}")
        return "Price not found"

def fetch_articles(stock):
    """Gets news articles using yfinance"""
    try:
        news = stock.news
        # Extract titles from news items (limit to 10 articles)
        titles = [item['content']['title'] for item in news[:10]] if news else []
        return titles
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []

def analyze_sentiment(articles):
    """Analyzes sentiment of article headlines using TextBlob."""
    sentiments = []
    for article in articles:
        analysis = TextBlob(article)
        sentiment_score = analysis.sentiment.polarity
        sentiment = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
        sentiments.append((article, sentiment))
    return sentiments

def get_historical_data(stock):
    """Fetch historical stock price data for the chart using yfinance"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        history = stock.history(start=start_date, end=end_date)
        dates = history.index.strftime('%Y-%m-%d').tolist()
        prices = history['Close'].tolist()
        
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