import streamlit as st
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# Initialize OpenAI and News API
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
news_api_key = os.getenv('NEWS_API_KEY')

# Set up OpenAI client
client = OpenAI(api_key=openai_api_key)

# Function for fetching News Articles
def fetch_news(api_key, query, language='en', page_size=5):
    url = ('https://newsapi.org/v2/everything?'
           f'q={query}&'
           f'language={language}&'
           'sortBy=publishedAt&'
           f'pageSize={page_size}&'
           f'apiKey={api_key}')
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['articles']
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        st.error(f'An error occurred: {err}')
    return []

# Summarize News Articles Using OpenAI GPT
def summarize_article(article_content):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following article in 2 short sentences."},
                {"role": "user", "content": article_content}
            ],
            max_tokens=60,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error summarizing article: {e}")
        return ''

# Perform Sentiment Analysis on Summaries
def sentiment_analysis(summary):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Determine the sentiment as Positive, Negative, or Neutral."},
                {"role": "user", "content": summary}
            ],
            max_tokens=5,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f'Error analyzing the sentiment: {e}')
        return 'Neutral'

# Suggest trading actions based on sentiment
def suggest_trading_action(sentiment):
    if sentiment.lower() == 'positive':
        return 'Buy'
    elif sentiment.lower() == 'negative':
        return 'Sell'
    else:
        return 'Hold'

# Build the Streamlit Interface
st.title('📰 AI-Powered Stock Market News Analyzer')

query = st.text_input('Enter a stock symbol or company name:', 'AAPL')

if st.button('Analyze'):
    articles = fetch_news(news_api_key, query, page_size=3)  # Limit to 3 articles to reduce API calls
    if articles:
        st.success(f'Analyzed {len(articles)} recent articles about "{query}".')
        for article in articles:
            st.subheader(article['title'])
            st.write(f"Source: {article['source']['name']}")
            st.write(f"Published At: {article['publishedAt']}")
            
            summary = summarize_article(article.get('description', ''))
            st.write('**Summary:**', summary)
            
            sentiment = sentiment_analysis(summary)
            st.write('**Sentiment:**', sentiment)
            
            action = suggest_trading_action(sentiment)
            st.write('**Suggested Action:**', action)
            st.markdown('---')
    else:
        st.warning('No articles found. Please try a different query.')