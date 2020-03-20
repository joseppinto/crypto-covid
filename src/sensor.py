import requests
from datetime import datetime
from twitter import Twitter, OAuth
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import opinion_lexicon
from nltk.tokenize import treebank
import sys
import os.path
from os import path


if len(sys.argv) < 2:
    exit(-1)

# Get path for dataset we'll write on
DATASET_FILE = sys.argv[1]


# CRYPTO API SETTINGS
CRYPTO_API_KEY = os.environ.get("CRYPTO_API_KEY")
COIN_HEADERS = {'X-CoinAPI-Key': CRYPTO_API_KEY}
COINS = ['BTC', 'ETH', 'XRP', 'LTC']

# COVID API SETTINGS
URL_COVID = "https://coronavirus-monitor.p.rapidapi.com/coronavirus/cases_by_particular_country.php"
MONITORED_COUNTRIES = ['China', 'Italy', 'Iran', 'Spain',
                       'Germany', 'USA', 'France', 'S. Korea',
                       'Switzerland', 'UK', 'Portugal'
                       ]
COVID_API_KEY = os.environ.get("COVID_API_KEY")
HEADERS_COVID = {
    'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com",
    'x-rapidapi-key': COVID_API_KEY
    }

# TWITTER SEARCH SETTINGS
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')

HASHTAGS = {}
HASHTAGS['BTC'] = ['bitcoin', 'btc', 'bitcoinmining']
HASHTAGS['ETH'] = ['ethereum', 'eth']
HASHTAGS['XRP'] = ['ripple', 'xrp']
HASHTAGS['LTC'] = ['litecoin', 'ltc']
SINCE_ID = {}
SINCE_ID['BTC'] = 0

# NLP settings
STOP_WORDS=set(stopwords.words("english"))
SELECTED_POS_TAGS = ['JJ', 'JJR', 'JJS', 'MD',
                     'RB', 'RBR', 'RBS', 'UH', 'VB',
                     'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']


# NLP function to determine if tweet has positive, neutral or negative sentiment
def simple_sentiment(text):
    tokenizer = treebank.TreebankWordTokenizer()
    pos_words = 0
    neg_words = 0

    tokenized_sent = [word.lower() for word in tokenizer.tokenize(text)]

    for word in tokenized_sent:
        if word in opinion_lexicon.positive():
            pos_words += 1
        elif word in opinion_lexicon.negative():
            neg_words += 1

    if pos_words > neg_words:
        return 'Positive'
    elif pos_words < neg_words:
        return 'Neutral'
    elif pos_words == neg_words:
        return 'Negative'

# Start of script flow
# Initialize our data row as a dict with a timestamp (minute precision)
dict = {}

time = str(datetime.now())[0:16]
dict["time"] = time


# Get data on our selected cryptocurrencies
print("Getting data from coin api...", end="")
for coin in COINS:
    url = f'https://rest.coinapi.io/v1/exchangerate/{coin}/USD'
    res = requests.get(url, headers=COIN_HEADERS)
    print(CRYPTO_API_KEY)
    dict[f"{coin}_PRICE_USD"] = float((res.json())["rate"])
print("Done")

# Get COVID data on monitored countries
print("Getting data from COVID19 api...", end="")
for mc in MONITORED_COUNTRIES:
    querystring = {"country": mc}
    response = requests.request("GET", URL_COVID, headers=HEADERS_COVID, params=querystring)
    data = response.json()["stat_by_country"][-1]
    dict[f"{mc}_total_cases"] = data["total_cases"]
    dict[f"{mc}_new_cases"] = data["new_cases"]
    dict[f"{mc}_total_deaths"] = data["total_deaths"]
print("Done")

# Fetch tweets and determine if they have useful data
print("Starting to fetch twitter data...")
oauth = OAuth(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
t = Twitter(auth=oauth)

for coin in COINS:
    print(f"Processing {coin} tweets...", end="")
    balance = {}
    for h in HASHTAGS[coin]:

        query = t.search.tweets(q= f'%23{h}', lang='en')
        ps = PorterStemmer()
        lem = WordNetLemmatizer()
        for s in query['statuses']:
            sentiment = simple_sentiment(s['text'])
            balance[sentiment] = balance.get(sentiment, 0) + 1

    if balance['Positive'] > balance['Negative']:
        dict[f"{coin}_twitter"] = 1
    elif balance['Positive'] < balance['Negative']:
        dict[f"{coin}_twitter"] = 0
    else:
        dict[f"{coin}_twitter"] = 0.5
    print("Done")


# Print new row to dataset
print(f"Writing to dataset file({DATASET_FILE})...", end="")
if path.exists(DATASET_FILE):
    file = open(DATASET_FILE, 'a')
else:
    file = open(DATASET_FILE, 'w+')
    line = ""
    for c in dict.keys():
        line += str(c) + ", "
    file.write(line[:-2] + "\n")

line = ""
for c in dict.values():
    line += str(c) + ", "
file.write(line[:-2] + "\n")

file.close()
print("Done")
