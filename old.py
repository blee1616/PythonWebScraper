import requests
import re
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup
from openai import OpenAI
from textblob import TextBlob

client = OpenAI(api_key="API key", base_url="https://openrouter.ai/api/v1") #API key

CLEANR = re.compile('<.*?>') #Cleans requests for articles, leaving only article names


def fetch_stock_price(ticker): #Gets the latest stock price from Yahoo Finance
    
    url = f"https://finance.yahoo.com/quote/{ticker}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
        if price_tag:
            return price_tag.text
    return "Price not found"


def fetch_articles(ticker): #Gets news articles from yahoo finance website
    
    url = f"https://finance.yahoo.com/quote/{ticker}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all('a', class_='titles') #all articles have the word "titles" in class
        return [re.sub(CLEANR, '', str(link)) for link in links]
    return []


def analyze_sentiment(articles):
    """Analyzes sentiment of article headlines."""
    sentiments = []
    for article in articles:
        analysis = TextBlob(article)
        sentiment_score = analysis.sentiment.polarity
        sentiment = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"
        sentiments.append((article, sentiment))
    return sentiments


# def create_rankings(articles, ticker):
#     """Uses AI to rank articles."""
#     article_text = "\n".join([f"{i+1}. {a}" for i, a in enumerate(articles)])
#     chat = client.chat.completions.create(
#         model="deepseek/deepseek-r1:free",
#         messages=[
#             {"role": "user", "content": f"Given these articles:\n{article_text}\nOnly return numbers 1-100 (1=worst, 100=best) in a numbered list (no explanation) for the future of {ticker} stock."}
#         ]
#     )
#     return chat.choices[0].message.content


def fetch_historical_prices(ticker):
    """Fetches and plots historical stock prices."""
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1=1640995200&period2=1672531200&interval=1d&events=history"
    response = requests.get(url)
    
    if response.status_code == 200:
        df = pd.read_csv(pd.compat.StringIO(response.text))
        df['Date'] = pd.to_datetime(df['Date'])
        plt.figure(figsize=(10, 5))
        plt.plot(df['Date'], df['Close'], label=f'{ticker} Stock Price', color='blue')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.title(f'Historical Stock Prices for {ticker}')
        plt.legend()
        plt.grid()
        plt.show()
    else:
        print("Failed to fetch historical data.")


if __name__ == "__main__": #main function
    tickers = input("Enter stock ticker symbols (comma-separated): ").upper().split(',')
    for ticker in tickers:
        ticker = ticker.strip()
        print(f"\nFetching data for {ticker}...")
        
        price = fetch_stock_price(ticker)
        print(f"Current Price: {price}")
        
        articles = fetch_articles(ticker)
        if articles:
            sentiments = analyze_sentiment(articles)
            for article, sentiment in sentiments:
                print(f"{article} - Sentiment: {sentiment}")
            
            # rankings = create_rankings(articles, ticker)
            # print(f"Stock Ranking for {ticker}:\n{rankings}")
        else:
            print("No articles found.")
        
        fetch_historical_prices(ticker)
