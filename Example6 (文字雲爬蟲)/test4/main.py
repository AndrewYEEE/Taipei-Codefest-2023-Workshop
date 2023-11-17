#Setup and Import Required Libraries
import pandas as pd
from pytrends.request import TrendReq

"""
https://pypi.org/project/pytrends

1. interest_over_time() : 取得關鍵字熱搜歷史資料

2. trending_searches() : 每日熱搜趨勢

3. top_charts() : 年度熱搜排行

4. suggestions() : 建議的關鍵字清單

5. interest_by_region() : 查詢關鍵字的熱搜區域

6. related_queries() : 查詢關鍵字的關聯查詢

7. related_topics()：查詢關鍵字的關聯主題

"""


pytrends = TrendReq(hl='zh-TW', tz=-480) 

kw_list = ["台北","臺北"] # list of keywords to get data 
pytrends.build_payload(kw_list, cat=0, timeframe='today 1-m', geo='TW') 
topics_data = pytrends.related_topics() #Returns dictionary of pandas.DataFrames
queries_data = pytrends.related_queries() #Returns dictionary of pandas.DataFrames
keywords = pytrends.suggestions(keyword=kw_list[0]) #Returns dictionary
trending_data =  pytrends.trending_searches(pn='taiwan')  #Returns pandas.DataFrame

print(topics_data)
topics_data_df = pd.DataFrame(topics_data)
# topics_data_df = topics_data_df.str.replace(" ","",regex=True)  #處理
topics_data_df.to_csv("topics_data.csv",encoding="utf-8")
# for key in topics_data:
#     topics_data[key]['rising'].to_csv("topics_data"+key+".csv",encoding="utf-8")
   


print(queries_data)
# queries_data_df = pd.DataFrame(queries_data)
# queries_data_df = queries_data_df.str.replace(" ","",regex=True)  #處理
for key in queries_data:
    queries_data[key]['top'].to_csv("queries_data"+key+"_top.csv",encoding="utf-8")
    queries_data[key]['rising'].to_csv("queries_data"+key+"_rising.csv",encoding="utf-8")



print(keywords)
keywords_df = pd.DataFrame(keywords)
# keywords_df = keywords_df.str.replace(" ","",regex=True)  #處理
keywords_df.to_csv("keywords_data.csv",encoding="utf-8")


print(trending_data)
# trending_data_df = pd.DataFrame(trending_data)
# trending_data_df = trending_data_df.str.replace(" ","",regex=True)  #處理
trending_data.to_csv("trending_data.csv",encoding="utf-8")





# historical_interest = pytrends.get_historical_interest(kw_list, 
#                                  year_start=2023, 
#                                  month_start=1, 
#                                  day_start=1, 
#                                  hour_start=0, 
#                                  year_end=2023, 
#                                  month_end=11, 
#                                  day_end=16, 
#                                  hour_end=0, 
#                                  cat=0, 
#                                  geo='TW', 
#                                  gprop='', 
#                                  sleep=1)

# print(historical_interest)