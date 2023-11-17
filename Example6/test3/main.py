import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime



# 如果連接掛掉可以自己把ed中的參數改成今天的日期~
# url = 'https://trends.google.com.tw/trends/api/dailytrends?hl=zh-TW&tz=-480&ed=20231116&geo=TW&ns=15'
# resp = requests.get(url)
# # print(resp.text)


# pd.DataFrame(json.loads(re.sub(r'\)\]\}\',\n', '', resp.text))['default']['trendingSearchesDays'][0]['trendingSearches'])
enddt = datetime.datetime.today()
startdt = enddt - datetime.timedelta(days=7)
df = []
for i in pd.date_range(start=datetime.datetime.strftime(startdt,'%Y%m%d'), end=datetime.datetime.strftime(enddt,'%Y%m%d'), freq='1D'):
      url = 'https://trends.google.com.tw/trends/api/dailytrends?hl=zh-TW&tz=-480&ed={}&geo=TW&ns=15'.format(datetime.datetime.strftime(i, '%Y%m%d'))
      print(url)
      resp = requests.get(url)
      ndf=[]
      ndf = pd.DataFrame(json.loads(re.sub(r'\)\]\}\',\n', '', resp.text))['default']['trendingSearchesDays'][0]['trendingSearches'])
      ndf['date'] = datetime.datetime.strftime(i, '%Y-%m-%d')
      df.append(ndf)
df = pd.concat(df, ignore_index=True)
df['title'] = df['title'].apply(lambda x: x['query'])
print(df)
out = df[['title','formattedTraffic','relatedQueries','date']]

out.to_csv("trends_news.csv",encoding="utf-8")