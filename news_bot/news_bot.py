
import requests
import json
from bs4 import BeautifulSoup
from bs4.element import Comment
from dotenv import load_dotenv
import os

load_dotenv()
# Set up the Telegram bot
bot_token = os.environ.get('BOT_TOKEN')
bot_chatID = os.environ.get('BOT_CHAT_ID')

# Set up the NewsData API
news_data_key = os.environ.get('NEWS_DATA_KEY')

# Set up the TextGear API
textgear_api_key = os.environ.get('TEXT_GEAR_KEY')

source_content_dict = {
    'sciencealert': {'div': 'post-content'},
    'phys': {'div': 'article-main'},
    'wired': {'div': 'body__inner-container'}
}

avoided_tags = ['style', 'script', 'head', 'title', 'meta', '[document]']


# Define the /news command handler
def news():

    # Fetch the latest news headlines from the News API
    url = f'https://newsdata.io/api/1/news?apikey={news_data_key}&category=science,technology&language=en&domain=phys,wired,sciencedaily,sciencealert'
    response = requests.get(url)
    data = json.loads(response.text)

    data = [data_with_content for data_with_content in data['results'] if
            data_with_content.get('link')]

    # Summarize the news articles using the TextGear API
    for article in data:
        source = article['source_id']
        url = article['link']
        content = extract_content(url, source)
        summary = summarize_text(content)
        message = f"{article['title']}\n\n{summary}\n\n{url}"
        send_message(message)


# Define the function to extract the content of an article
def extract_content(url, source):
    element_type, element_class = list(source_content_dict[source].items())[0]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58. Safari/537.3'
    }
    website = requests.get(url, headers=headers)
    soup = BeautifulSoup(website.text, 'html.parser')
    # find the div element with class "post-content"
    news_content = soup.find(element_type, class_=element_class)
    news_text = news_content.findAll(string=True)

    news_text = filter(tag_visible, news_text)
    content = u" ".join(t.strip() for t in news_text)

    return content


# Define the function to summarize text using the TextGear API
def summarize_text(text):
    url = f'https://api.textgears.com/summarize?key={textgear_api_key}&text={text}'
    response = requests.post(url)
    data = json.loads(response.text)
    return '\n'.join(data['response']['summary'])


# Define the function to send a message via the Telegram Bot API
def send_message(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": bot_chatID,
        "text": message
    }
    requests.post(url, json=payload)


# Define the function to filter out unwanted tags and comments
def tag_visible(element):
    if element.parent.name in avoided_tags or isinstance(element, Comment):
        return False
    return True


if __name__ == '__main__':
    news()
