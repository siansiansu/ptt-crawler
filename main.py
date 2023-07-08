import os
import csv
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

start_date = str(sys.argv[1])
end_date = str(sys.argv[2])
downloadFolder = sys.argv[3]
keywords = sys.argv[4]

pageUrl = 'https://www.ptt.cc/bbs/Gossiping/index.html'

Path("./{}".format(downloadFolder)).mkdir(parents=True, exist_ok=True)


print('文章下載目錄：{}/{}'.format(os.getcwd(), downloadFolder))

def get_page(url):
    r = requests.get(url, headers={
        "cookie": "over18=1",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
    })

    if r.status_code != 200:
        raise Exception('[文章擷取失敗] ' + url)
    return BeautifulSoup(r.text, "html.parser")


def date_format(date):
    return datetime.strptime(date, '%a %b %d %H:%M:%S %Y').strftime('%Y-%m-%d')

def get_month(date):
    return '-'.join(date.split('-')[:2])

def check_keyword(article):
    for keyword in keywords.split(','):
        if keyword in article:
            return True
    return False

def check_date(date):
    return datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(start_date, '%Y-%m-%d') \
        and datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(end_date, '%Y-%m-%d')


def save_text(date, context, filename):
    month = get_month(date)
    Path("./{}/{}".format(downloadFolder, month)).mkdir(parents=True, exist_ok=True)

    with open('./{}/{}/{}.txt'.format(downloadFolder, month, filename), 'w', encoding='utf-8-sig') as f:
        f.write(context)

def search_a_page(pageUrl):
    rootPage = get_page(pageUrl)
    arts = rootPage.find_all('div', class_='r-ent')

    if not os.path.isfile('{}/索引.csv'.format(downloadFolder)):
        indexCSV = pd.DataFrame(columns=['日期', '標題', '作者', '內容', '網址'], index=None)
        indexCSV.to_csv('{}/索引.csv'.format(downloadFolder), encoding='utf-8-sig', index=False)

    df = pd.read_csv('{}/索引.csv'.format(downloadFolder), encoding='utf-8-sig', index_col=False)

    for art in arts:
        title = art.find('div', class_='title').getText().strip()
        if '本文已被刪除' in title or '板規' in title:
            continue
        try:
            link = 'https://www.ptt.cc' + art.find('div', class_='title').a['href'].strip()
        except:
            print("[連結不存在] 標題：{}".format(title))
            link = None
        if link:
            p = get_page(link)
            try:
                date = date_format(p.select('#main-content > div:nth-child(4) > span.article-meta-value', limit=1)[0].getText())
            except:
                date = "99-99-99"
            title = p.select('#main-content > div:nth-child(3) > span.article-meta-value')[0].getText()

            if not check_date(date):
                print("[不在輸入的日期範圍內，略過這篇內容] 日期：{}，標題：{}".format(date, title))
                return None

            article = p.find(id='main-content').getText().strip()
            author = p.find(class_='article-meta-value').getText().strip()
            if check_keyword(article):
                print("[含有關鍵字，處理中] 日期：{}，標題：{}".format(date, title))
                save_text(date, article, title.replace('/', '_'))
                df2 = pd.DataFrame([date, title, author, article, link]).T
                df2.columns = ['日期', '標題', '作者', '內容', '網址']
                df = pd.concat([df, df2], ignore_index=True, axis=0)
            else:
                print("[不含有關鍵字，略過這篇內容] 日期：{} ，標題：{}".format(date, title))
    df.drop_duplicates(subset=['網址'], inplace=True)
    df.to_csv('{}/索引.csv'.format(downloadFolder), encoding='utf-8-sig', index=False)

    nextLink = 'https://www.ptt.cc' + rootPage.find("a", string="‹ 上頁")["href"]
    print("搜尋下一頁：{}".format(nextLink))
    return search_a_page(nextLink)

search_a_page(pageUrl)
