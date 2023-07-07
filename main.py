import os
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

start_date = '2023-07-01'
end_date = '2023-07-12'
rootUrl = 'https://www.ptt.cc/bbs/Gossiping/index.html'

Path("./articles").mkdir(parents=True, exist_ok=True)


print('[INFO] your current working dir is {}'.format(os.getcwd()))

def get_page(url):
    r = requests.get(url, headers={
        "cookie": "over18=1",
    })

    if r.status_code != 200:
        raise
    return BeautifulSoup(r.text, "html.parser")


def date_format(date):
    return datetime.strptime(date, '%a %b %d %H:%M:%S %Y').strftime('%Y-%m-%d')


def check_date(date):
    return datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(start_date, '%Y-%m-%d') \
        and datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(end_date, '%Y-%m-%d')

def save_text(context, filename):
    if os.path.isfile('./articles/{}.txt'.format(filename)):
        print("[INFO] {} already exists, skip.".format(filename))
        return
    with open('./articles/{}.txt'.format(filename), 'w', encoding='utf-8') as f:
        f.write(context)

def save_index(context):
    with open('./index.csv', 'w', encoding='utf-8') as f:
        f.write(context)

def get_context(url):
    p = get_page(url)
    date = date_format(p.select('#main-content > div:nth-child(4) > span.article-meta-value', limit=1)[0].getText())
    if not check_date(date):
        return None
    title = p.select('#main-content > div:nth-child(3) > span.article-meta-value')[0].getText()
    print("Processing {}, {}...".format(title, url))
    author = p.find(class_='article-meta-value').getText().strip()
    article = p.find(id='main-content').getText().strip()
    save_text(article, title.replace('/', '_'))

    return date, title, author, article, url

rootPage = get_page(rootUrl)
arts = rootPage.find_all('div', class_='r-ent')

contexts = []
for art in arts:
    title = art.find('div', class_='title').getText().strip()
    if '本文已被刪除' in title or '板規' in title:
        continue
    link = 'https://www.ptt.cc' + art.find('div', class_='title').a['href'].strip()
    if link:
        context = get_context(link)
        contexts.append(context)

with open('index.csv', 'w', encoding='UTF-8') as f:
    write = csv.writer(f)
    write.writerow(['date', 'title', 'author', 'article', 'url'])
    write.writerows(contexts)
