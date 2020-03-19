import requests
from datetime import datetime
from twitter import Twitter, OAuth

# CRYPTO API SETTINGS
API_KEY = "7B1926D0-7FB2-4354-A8F0-3FB2B8D1F00D"
COIN_HEADERS = {'X-CoinAPI-Key': API_KEY}
COINS = ['BTC', 'ETH', 'XRP', 'LTC']

# COVID API SETTINGS
URL_COVID = "https://coronavirus-monitor.p.rapidapi.com/coronavirus/cases_by_particular_country.php"
MONITORED_COUNTRIES = ['China', 'Italy', 'Iran', 'Spain',
                       'Germany', 'USA', 'France', 'S. Korea',
                       'Switzerland', 'UK', 'Portugal'
                       ]
HEADERS_COVID = {
    'x-rapidapi-host': "coronavirus-monitor.p.rapidapi.com",
    'x-rapidapi-key': "0e6a8d459emsha4b8121ebc28670p185339jsn88f62da8994f"
    }

# TWITTER SEARCH SETTINGS
HASHTAGS = {}
HASHTAGS['BTC'] = ['bitcoin', 'btc', 'bitcoinmining']
HASHTAGS['ETH'] = ['ethereum', 'eth']
HASHTAGS['XRP'] = ['ripple', 'xrp']
HASHTAGS['LTC'] = ['litecoin', 'ltc']


# Start of script flow

# Initialize our data row as a dict with a timestamp (minute precision)
dict = {}
time = str(datetime.now())[0:16]
dict["time"] = time


# Get data on our selected cryptocurrencies
for coin in COINS:
    url = f'https://rest.coinapi.io/v1/exchangerate/{coin}/USD'
    res = requests.get(url, headers=COIN_HEADERS)

    dict[f"{coin}_PRICE_USD"] = float((res.json())["rate"])


# Get COVID data on monitored countries
for mc in MONITORED_COUNTRIES:
    querystring = {"country": mc}
    response = requests.request("GET", URL_COVID, headers=HEADERS_COVID, params=querystring)
    data = response.json()["stat_by_country"][-1]
    dict[f"{mc}_total_cases"] = data["total_cases"]
    dict[f"{mc}_new_cases"] = data["new_cases"]
    dict[f"{mc}_total_deaths"] = data["total_deaths"]


''' TODO: TWITTER
# Fetch tweets and determine if they have useful data


ACCESS_TOKEN = 'access_token'
ACCESS_SECRET = 'access_secret'
CONSUMER_KEY = 'consumer_key'
CONSUMER_SECRET = 'consumer_secret'

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
t = Twitter(auth=oauth)

query = t.search.tweets(q='%23hillarysoqualified')

for s in query['statuses']:
    print(s['created_at'], s['text'], '\n')
    
'''