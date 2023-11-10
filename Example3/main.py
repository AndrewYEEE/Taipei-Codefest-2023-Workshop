
import geopandas as gpd
import geocoder
import json
import pandas as pd
from shapely.geometry import LineString, Point, Polygon
import func
from re import search
pd.set_option('display.max_rows', None) #print時會印全部

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
Practice_accessibility_job_C.drop(['_importdate','_id','seqno','contact'], axis=1, inplace=True) #contact有個資，應該排除

print("ETL2 : 去除新北市的機構 (兩筆) ")
Practice_accessibility_job_C = Practice_accessibility_job_C[
    ~Practice_accessibility_job_C.address.str.contains('新北市')]
print(Practice_accessibility_job_C.shape)


print("ETL3 : 將換行符號、空格換為','符號 (原本上面是說換為空格，但我偏向於換為有形的符號)")
pattern = '|'.join(['\r\n','\n',' ','\xa0','\x20','\u3000','\?'])
Address_P = Practice_accessibility_job_C['address'].str.replace('\n', ',',regex=True)  #取代rows內字串
Practice_accessibility_job_C['address']= Address_P # 塞回" 

Telephone_P = Practice_accessibility_job_C['telephone'].str.replace(pattern, ',',regex=True)  #取代rows內字串
Practice_accessibility_job_C['telephone']= Telephone_P # 塞回" 

Name_P = Practice_accessibility_job_C['name'].str.replace(pattern, ' ',regex=True)  #取代rows內字串，以空格替換
Practice_accessibility_job_C['name']= Name_P # 塞回" 

Business_P = Practice_accessibility_job_C['business item'].str.replace(pattern, '',regex=True)  #取代rows內字串，以空格替換
Practice_accessibility_job_C['business item']= Business_P # 塞回" 


print("ETL4 : 針對地址、電話內容檢視並只保留基金會資訊")

# ====================處理地址========================
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

Practice_accessibility_job_C['address'] = Address_List


# ====================處裡TelNum========================
# 先了解格式有哪些
# print(Practice_accessibility_job_C['telephone'].value_counts(dropna=False).to_dict())

# 從上面我們可以知道TelNum格式為: '暫不提供'、'2305-0025'、'(02)2391-1006'、'2309-3138,轉17'、'27652947'
# 這裡我先只節取 '暫不提供'、'2305-0025'、'27652947'
pattern = '|'.join(['\d{4}-\d{4}','暫不提供','\d{8}'])
Telephone_L = Practice_accessibility_job_C['telephone'].to_list() #獲取List
for i in range(len(Telephone_L)): 
    mat = search(pattern, Telephone_L[i])
    if mat is None: #如果真的找不到，預設插入 "暫不提供"
        mat = "暫不提供"
    else:
        mat = mat.group(0) #獲取第一筆合規值
    Telephone_L[i] = mat

#將List重新塞回panda
Practice_accessibility_job_C['telephone'] = Telephone_L



print("ETL5 : 民國年修改成西元年")
chinese_year = Practice_accessibility_job_C['year'] 
bc_year = chinese_year.astype(int) + 1911 #民國 轉 西元
Practice_accessibility_job_C['year']  = bc_year # 塞回 



print("ETL6 : 導入行政區")
Practice_accessibility_job_C['town'] = Practice_accessibility_job_C['address'].str.extract('臺北市([^\\d]{2}區)')
# 移除NaN資料 (應該只有1筆)
Practice_accessibility_job_C = Practice_accessibility_job_C.dropna()




print("OUTPUT1 : 統計business服務總數 (有些機構同時有多種服務，所以結果一定比機構數量多)")
# 只獲取需要的欄位
Business_Count = Practice_accessibility_job_C[['business item','town']]

# 先將business item轉換成List
Business_Count['business']=Business_Count['business item'].str.split("、")
# 依據List擴展出來
Business_Count = Business_Count.explode('business').reset_index()


#將 組合 物件依據區域分群
stat = Business_Count.groupby('business').size().to_dict()
specified_order = Business_Count['business'].unique()


results = {
    'data': [
        {
            'name':'臺北市身障就業機構服務類型總數',
            'data': [
                {
                    'x': x,
                    'y': stat[x]
                }
                for x in specified_order
            ]
        }
    ]
}


with open('accessibility_job_business_num.json', "w",encoding='utf8') as json_file:
    json.dump(results, json_file, ensure_ascii=False)


print("OUTPUT2 : 依據行政區統計機構數量")
stat = Practice_accessibility_job_C.groupby('town').size().to_dict()
specified_order = [
    '北投區', '士林區', '內湖區', '南港區',
    '松山區', '信義區', '中山區', '大同區',
    '中正區', '萬華區', '大安區', '文山區'
]


results = {
    'data': [
        {
            'name':'',
            'data': [
                {
                    'x': x,
                    'y': stat[x]
                }
                for x in specified_order
            ]
        }
    ]
}
print(results)

with open('accessibility_job_institution_num.json', "w",encoding='utf8') as json_file:
    json.dump(results, json_file, ensure_ascii=False)


print("ETL7 : 將地址加以解析經緯度座標 (這個要一點時間，它查一個座標蠻久的)")
# 顯以第一個地址嘗試獲取經緯度座標
# addr_0 = Practice_accessibility_job_C.loc[0, 'address'] #獲取地址欄位的第一筆資料
# addr_0_info = geocoder.arcgis(addr_0) #查詢座標資訊
# print(addr_0_info.json)
# addr_0_lng = addr_0_info.json['lng']
# addr_0_lat = addr_0_info.json['lat']
# point0 = Point(addr_0_lng, addr_0_lat) #製作座標點0
# print(point0.area) #製作座標點面積
# print(point0.bounds) # minx, miny, maxx, maxy #製作座標點面積範圍
# print(point0.geom_type) #座標類型 (Points、Lines、Polygons)


# Practice_accessibility_job_C['geometry'] = Practice_accessibility_job_C['address'].apply(
#     lambda x: Point(
#         geocoder.arcgis(x).json['lng'],
#         geocoder.arcgis(x).json['lat']
#     )
# )


# # from pd to gpd
# Practice_accessibility_job_GEO = gpd.GeoDataFrame(
#     Practice_accessibility_job_C,
#     crs='EPSG:4326'
# )
# print(Practice_accessibility_job_GEO)

# print("OUTPUT3 : 各機構標準訊息與座標點")
# Practice_accessibility_job_GEO.to_file(
#     'accessibility_job_institution_geo.geojson',
#     driver='GeoJSON'
# )






print("OUTPUT4 : 依據各行政區機構數量製作座標圖")
FILE_NAME = '.\Datasets\Raw\臺北市區界圖_20220915'
district_border = gpd.read_file(FILE_NAME, encoding='utf-8') 
district_border.crs = 'EPSG:3826' #轉台灣常用座標格式
district_border = district_border[['PTNAME', 'geometry']] #將臺北市區界圖 物件只保留['PTNAME', 'geometry']
district_border.rename(columns={'PTNAME': 'town'}, inplace=True)
district_border['town']=district_border['town'].str.replace("臺北市", "")
district_border = district_border.to_crs('EPSG:4326')
print("匯出district_border.geojson")
district_border.to_file(
    'district_border.geojson',
    driver='GeoJSON'
)


district_border['geometry'] = district_border['geometry'].centroid




#leftjoin 將統計資料合併過來
Practice_accessibility_job_T = Practice_accessibility_job_C.copy()
# Practice_accessibility_job_T['town'] = '臺北市'+Practice_accessibility_job_T['town'] 
stat = Practice_accessibility_job_T.groupby('town').size().to_dict()
print(stat)
district_border['nums'] =  district_border['town'].map(stat)
print(district_border)


print("匯出district_institution_geo.geojson")
district_border.to_file(
    'district_institution_geo.geojson',
    driver='GeoJSON'
)
