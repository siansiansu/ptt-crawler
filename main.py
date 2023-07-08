import logging
import os
import csv
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

# 改這裡
#####################################################################
# 開始的時間
start_date = "2023-01-01"

# 結束時間
end_date = "2023-07-07"

# 下載文章放的資料夾
downloadFolder = "關於疫情的文章"

# 搜尋什麼關鍵字
keywords = "疫情,校正回歸,高端,超前部署,新冠,確診"

# 從這個頁面往前搜尋
pageUrl = 'https://www.ptt.cc/bbs/Gossiping/index26353.html'

# 搜尋到這頁結束
endUrl = 'https://www.ptt.cc/bbs/Gossiping/index855.html'
#####################################################################
Path("./{}".format(downloadFolder)).mkdir(parents=True, exist_ok=True)

now = datetime.now()
current_time = now.strftime("%Y-%m-%d-%H-%M")

logging.basicConfig(filename='log-' + current_time + '.txt',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logging.getLogger().addHandler(logging.StreamHandler())
logging.info('文章下載目錄：{}/{}'.format(os.getcwd(), downloadFolder))

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
    if date == "99-99-99":
        return True
    return datetime.strptime(date, '%Y-%m-%d') >= datetime.strptime(start_date, '%Y-%m-%d') \
        and datetime.strptime(date, '%Y-%m-%d') <= datetime.strptime(end_date, '%Y-%m-%d')

def save_text(date, context, filename):
    month = get_month(date)
    Path(os.path.join(downloadFolder, month)).mkdir(parents=True, exist_ok=True)

    dest = os.path.join(downloadFolder, month, filename)
    with open(dest, 'w', encoding='utf-8-sig') as f:
        f.write(context)

def search_a_page(pageUrl):
    rootPage = get_page(pageUrl)
    arts = rootPage.find_all('div', class_='r-ent')

    if not os.path.isfile(r'{}/索引.csv'.format(downloadFolder)):
        indexCSV = pd.DataFrame(columns=['日期', '標題', '作者', '內容', '網址'], index=None)
        indexCSV.to_csv(r'{}/索引.csv'.format(downloadFolder), encoding='utf-8-sig', index=False)

    df = pd.read_csv(r'{}/索引.csv'.format(downloadFolder), encoding='utf-8-sig', index_col=False)

    for art in arts:
        try:
            title = art.find('div', class_='title').getText().strip()
        except:
            logging.info("[標題不存在] 標題：{}".format(title))
            title = None

        if '本文已被刪除' in title or '板規' in title:
            continue
        try:
            link = 'https://www.ptt.cc' + art.find('div', class_='title').a['href'].strip()
        except:
            logging.info("[連結不存在] 標題：{}".format(title))
            link = None
        if link and title:
            p = get_page(link)
            try:
                date = date_format(p.select('#main-content > div:nth-child(4) > span.article-meta-value', limit=1)[0].getText())
            except:
                date = "99-99-99"
            # title = p.select('#main-content > div:nth-child(3) > span.article-meta-value')[0].getText()

            if not check_date(date):
                logging.info("[不在輸入的日期範圍內，略過這篇內容] 日期：{}，標題：{}".format(date, title))
                return None

            article = p.find(id='main-content').getText().strip()
            try:
                author = p.find(class_='article-meta-value').getText().strip()
            except:
                author = ""
            if check_keyword(article):
                logging.info("[含有關鍵字，處理中] 日期：{}，標題：{}".format(date, title))
                filename = title.replace('/', '_').replace(' ', '_').replace('"', '_').replace('?', '_').replace('\\', '_')
                save_text(date, article, filename)
                df2 = pd.DataFrame([date, title, author, article, link]).T
                df2.columns = ['日期', '標題', '作者', '內容', '網址']
                df = pd.concat([df, df2], ignore_index=True, axis=0)
            else:
                logging.info("[不含有關鍵字，略過這篇內容] 日期：{} ，標題：{}".format(date, title))
    df.drop_duplicates(subset=['網址'], inplace=True)
    df.to_csv(r'{}/索引.csv'.format(downloadFolder), encoding='utf-8-sig', index=False)

    nextLink = 'https://www.ptt.cc' + rootPage.find("a", string="‹ 上頁")["href"]
    if nextLink == endUrl:
        logging.info("搜尋結束")
        sys.exit(0)
    logging.info("搜尋下一頁：{}".format(nextLink))
    return search_a_page(nextLink)

search_a_page(pageUrl)
logging.info("搜尋結束")
