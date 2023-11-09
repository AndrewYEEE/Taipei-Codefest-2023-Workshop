
import geopandas as gpd
import geocoder
import json
import pandas as pd
from shapely.geometry import LineString, Point, Polygon
import func



## **實作 - 整理儀表板可用的資料**
"""
原始資料集 身障就業資源地圖_1120918

URL:https://data.taipei/dataset/detail?id=c5aafda8-ef14-4f66-a6b7-d5da995a14b5

備註:原始資料集之地址欄位填寫狀況較多，如同一欄位有多筆地址或門牌號碼有多筆的狀況，建議可依照自身考慮條件進行清理與優化。



最終產出成果

共有二個檔案，分為基本圖資(chart_data)與地圖圖資(map_data)
地址清理上採取以下動作:
(1)去除新北市的機構(2筆)
(2)同一欄位有多筆地址換行取代為空格
(3)若有基金會與辦公室地址，以基金會為主
(4)若存在多筆地址，暫取第一筆地址作為代表呈現(可依個人判斷優化操作)
(5)若geocoder無回傳經緯度欄位，暫先去除該筆資料(可依個人判斷優化操作)(1筆)

"""
print("Input 1. 身障就業資源地圖")
rid = 'f26a4c04-771f-42f3-a028-1a7e89303509'
Practice_accessibility_job = func.get_datataipei_api(rid)
Practice_accessibility_job_C = Practice_accessibility_job.copy()
print(Practice_accessibility_job_C.shape)

print("ETL1 : 移除不用的Col ")
Practice_accessibility_job_C.drop(['_importdate','_id','seqno'], axis=1, inplace=True)

print("ETL2 : 去除新北市的機構 (兩筆) ")
Practice_accessibility_job_C = Practice_accessibility_job_C[
    ~Practice_accessibility_job_C.address.str.contains('新北市')]
print(Practice_accessibility_job_C.shape)


print("ETL3 : 將換行符號、空格換為','符號 (原本上面是說換為空格，但我偏向於換為有形的符號)")
pattern = '|'.join(['\n',' '])
Address_P = Practice_accessibility_job_C['address'].str.replace('\n', ',',regex=True)  #取代rows內字串
Practice_accessibility_job_C['address']= Address_P # 塞回" 

Contact_P = Practice_accessibility_job_C['contact'].str.replace(pattern, ',',regex=True)  #取代rows內字串
Practice_accessibility_job_C['contact']= Contact_P # 塞回" 

Telephone_P = Practice_accessibility_job_C['telephone'].str.replace(pattern, ',',regex=True)  #取代rows內字串
Practice_accessibility_job_C['telephone']= Telephone_P # 塞回" 



print("ETL4 : 針對地址、電話內容檢視並只保留基金會資訊")
Address_PD = Practice_accessibility_job_C['address'].copy()
Address_List = Address_PD.str.split(',').to_list()
for i in range(len(Address_List)):
    if len(Address_List[i]) < 2 : #如果只有一個，直接放回去
        Address_List[i] = Address_List[i][0]
        continue

    #保留具有"基金會"字眼內容
    Found = False
    for item in Address_List[i]: #如果不只一個，檢查內容
        if "基金會" in item:
            Address_List[i] = item 
            Found = True
            break
    
    #如果以上條件都沒有符合，以第一筆有"臺北市"的資料為主
    if Found == False :
        for item in Address_List[i]:
            if "臺北市" in item:
                Address_List[i] = item 
                Found = True
                break

    #如果以上條件都沒有符合，直接放置第一個元素
    if Found == False : 
        Address_List[i] = Address_List[i][0] 
print(Address_List)
print(len(Address_List))
Practice_accessibility_job_C['address'] = Address_List

print(Practice_accessibility_job_C)
print(Practice_accessibility_job_C.shape)



