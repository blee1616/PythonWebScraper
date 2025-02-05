import requests
import re
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI(api_key="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",
                base_url="https://openrouter.ai/api/v1")

# Get stock ticker input
ticker = input("Enter the stock ticker symbol: ").upper()
url = f"https://www.finance.yahoo.com/quote/{ticker}/"

# Fetch the webpage
response = requests.get(url)

# Regex to clean HTML tags
CLEANR = re.compile('<.*?>')

def create_rankings(articles, ticker):
    """Sends one API request to rank multiple articles at once."""
    article_text = "\n".join([f"{i+1}. {a}" for i, a in enumerate(articles)])
    
    chat = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",
        messages=[
            {
                "role": "user",
                "content": f"Given these articles:\n{article_text}\nOnly return numbers 1-100 (1=worst, 100=best) in a numbered list (no explanation) for the future of {ticker} stock."
            }
        ]
    )
    
    return chat.choices[0].message.content

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    links = soup.find_all('a', class_='titles')

    # Extract and clean article titles
    articles = [re.sub(CLEANR, '', str(link)) for link in links]
    print(articles)
    if articles:
        rankings = create_rankings(articles, ticker)
        print(f"Stock Ranking for {ticker}:\n{rankings}")
    else:
        print("No articles found.")

else:
    print("Failed to retrieve the webpage:", response.status_code)

