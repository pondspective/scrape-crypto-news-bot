import requests
import json
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
import time

BASE_URL = 'https://www.coindesk.com'
NEWS_URL_ENDPOINT = 'https://www.coindesk.com/pf/api/v3/content/fetch/websked-collections'
LIMIT_ROWS_PER_CATEGORY = 30
categories = ['markets','business','policy','tech','web3content']

def make_fetch_news_payload(content_alias, size, from_=0):
    return { 'query' : json.dumps({"content_alias":content_alias
                        ,"format":"main-navigation-article"
                        ,"from":str(from_)
                        ,"size":str(size)})
            }

def transform_data(data):
    selected_data = []
    for article in data:
        tag_text = []
        for tag in article['tags']:
            if tag_text != None:
                tag_text.append(tag['text'])
        trunc_url = article['canonical_url']
        # print(trunc_url)
        url_split = trunc_url.split('/')
        news_date = datetime(int(url_split[2]), int(url_split[3]), int(url_split[4])) if len(url_split) >= 5 else None
        item = {
            'url' : BASE_URL + trunc_url,
            'type':url_split[1],
            'date': news_date,
            'subtype':article['subtype'],
            'tags':tag_text,
            'headline':article['headlines']['basic']
        }
        # print(item)
        selected_data.append(item)
    return selected_data

def fetch_news_url_by_category(category):
    print(f"Get data from category {category}")
    payload = make_fetch_news_payload(content_alias=category, size=LIMIT_ROWS_PER_CATEGORY)
    resp = requests.get(url=NEWS_URL_ENDPOINT, params=payload)
    if resp.status_code == 200:
        data = json.loads(resp.text)
    else:
        print(f"Get data category {category} failed error status {resp.status_code}")
        print(resp.text)
    time.sleep(1)
    return data

def fetch_news_url(categories, transform=True):
    res = []
    for c in categories:
        data = fetch_news_url_by_category(c)
        if transform:
            res.extend(transform_data(data))
        else:
            res.extend(data)
    return res

def get_historical_news(data,days_ago):
    df = pd.json_normalize(data)
    filter_date = (datetime.now() - timedelta(days=days_ago)).date()
    df['date'] = df['date'].apply(lambda x: x.date())
    print(filter_date)
    return df[df['date'] >= filter_date]

def get_latest_news(data, category='all'):
    df = pd.json_normalize(data)
    df['date'] = df['date'].apply(lambda x: x.date())
    df.to_csv('debug.csv')
    print(df.head(5))
    print(df.dtypes)

    # Get latest date
    filter_date = df.dropna(subset=['date'])['date'].max()
    
    if category == 'all':
        return df[df['date'] == filter_date]
    else:
        return df[df['date'] == filter_date][df['type'] == category]

news = fetch_news_url(categories)
print(get_latest_news(news).head(5))




