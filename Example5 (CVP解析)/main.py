
import geopandas as gpd
import geocoder
import json
import pandas as pd
from shapely.geometry import LineString, Point, Polygon
import func
from re import search
import wget 
import os
pd.set_option('display.max_rows', None) #print時會印全部

"""
pip3 install wget

"""

# 處理 URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate chain too long
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context




# 時間,lon,lat,無意義,往東北,往東南,往西南,往西北,停止
print("Input 1. 基地台CVP資訊匯入")
FILE_NAME = '.\Datasets\Processed\CVP_data.csv'
CVP_Info = pd.read_csv(FILE_NAME)

# 處理時間格式
CVP_Info[['Date', 'Time']] = CVP_Info['時間'].str.split('_', expand=True)
CVP_Info[['Hour', 'Min','Sec']] = CVP_Info['Time'].str.split('-', expand=True)
CVP_Info.drop(['時間','Sec','無意義','Time'], axis=1, inplace=True)


CVP_Info['Date'] = CVP_Info['Date'].str.replace('-', '',regex=True)  #處理時間
CVP_Info['Date'] = "2023"+CVP_Info['Date'] #處理時間
CVP_Info['DateTime'] = CVP_Info['Date']+CVP_Info['Hour'] #處理時間

# 修改col名稱
CVP_Info.rename(columns={'往東北': 'EN','往東南': 'ES','往西南': 'WS','往西北': 'WN','停止': 'Stop'}, inplace=True)

# 改資料類型
CVP_Info["EN"] = CVP_Info["EN"].astype(int)
CVP_Info["ES"] = CVP_Info["ES"].astype(int)
CVP_Info["WN"] = CVP_Info["WN"].astype(int)
CVP_Info["WS"] = CVP_Info["WS"].astype(int)
CVP_Info["Stop"] = CVP_Info["Stop"].astype(int)
CVP_Info["lon"] = CVP_Info["lon"].astype(str) 
CVP_Info["lat"] = CVP_Info["lat"].astype(str) 

# 統整總人數 
column_names = ['EN', 'ES', 'WN', 'WS', 'Stop']
CVP_Info['Total']= CVP_Info[column_names].sum(axis=1)

#組合座標點
CVP_Info['GEO']= CVP_Info['lon']+","+CVP_Info['lat']


# # 轉換Geo pandas、查詢座標、儲存檔案
# Travel_Loc_Pars['geometry'] = CVP_Info[['lon','lat']]].apply(
#     lambda x: Point(
#         geocoder.arcgis(x).json['lng'],
#         geocoder.arcgis(x).json['lat']
#     )
# )


#重新排序Col
CVP_Info_Sort = CVP_Info[['DateTime','Date', 'Hour', 'Min', 'lon', 'lat' , 'GEO', 'EN', 'ES', 'WN', 'WS' , 'Stop', 'Total']] 
print(CVP_Info_Sort.head())



# Creating an empty dictionary
CVP_Info_By_Hour = {}
CVP_Info_By_Hour['DateTime'] = []
CVP_Info_By_Hour['GEO'] = []
CVP_Info_By_Hour['EN'] = []
CVP_Info_By_Hour['ES'] = []
CVP_Info_By_Hour['WN'] = []
CVP_Info_By_Hour['WS'] = []
CVP_Info_By_Hour['Stop'] = []
CVP_Info_By_Hour['Total'] = []



#獲取5000個座標點
LL = CVP_Info_Sort["GEO"].unique().tolist()
LL_df = pd.DataFrame(LL, columns =['GEO'])
# print(LL_df)

## 將這5000個座標點，與臺北市邊界圖做交集，只保留有交集的
LL_df[['lng', 'lat']] = LL_df['GEO'].str.split(',', expand=True)
LL_df['geometry'] = LL_df.apply(
    lambda x: Point(
        x.lng,
        x.lat)
, axis=1)
LL_GEO = gpd.GeoDataFrame(
    LL_df,
    crs='EPSG:4326'
)
# print(LL_GEO)


FILE_NAME = '.\Datasets\Raw\臺北市區界圖_20220915'
print("Input 臺北市區界圖")
district_border = gpd.read_file(FILE_NAME, encoding='utf-8') 
district_border.crs = 'EPSG:3826' #轉台灣常用座標格式
district_border = district_border.to_crs('EPSG:4326') #轉全球通用格式
district_border = district_border[['PTNAME', 'geometry']]
overlay_df = gpd.overlay(
    LL_GEO,
    district_border,
    how='intersection'
).explode(index_parts=True).reset_index() #index_parts=True是Warning叫我加的
GEO_LIST = overlay_df['GEO'].to_list() #獲取交集的座標群
# print(GEO_LIST)



# #獲取24小時時間點
DateTime_L = CVP_Info_Sort["DateTime"].unique().tolist() 


#開始依據每小時統計處裡 (要一段時間)
for i in range(len(DateTime_L)):
    temp_item= {}
    CVP_TEMP = CVP_Info_Sort.loc[CVP_Info_Sort['DateTime'] == DateTime_L[i],['GEO', 'EN', 'ES', 'WN', 'WS' , 'Stop', 'Total']]
    for index, row in CVP_TEMP.iterrows():
        if row['GEO'] not in GEO_LIST: #不在交集的座標內就直接略過
            continue 
        if row['GEO'] not in temp_item:
            temp_item[row['GEO']]={}
            temp_item[row['GEO']]['EN']=0
            temp_item[row['GEO']]['ES']=0
            temp_item[row['GEO']]['WN']=0
            temp_item[row['GEO']]['WS']=0
            temp_item[row['GEO']]['Stop']=0
            temp_item[row['GEO']]['Total']=0
        temp_item[row['GEO']]['EN']+=row['EN']
        temp_item[row['GEO']]['ES']+=row['ES']
        temp_item[row['GEO']]['WN']+=row['WN']
        temp_item[row['GEO']]['WS']+=row['WS']
        temp_item[row['GEO']]['Stop']+=row['Stop']
        temp_item[row['GEO']]['Total']+=row['Total']
    for key in temp_item:
        CVP_Info_By_Hour['DateTime'].append(DateTime_L[i])
        CVP_Info_By_Hour['GEO'].append(key)
        CVP_Info_By_Hour['EN'].append(temp_item[key]['EN'])
        CVP_Info_By_Hour['ES'].append(temp_item[key]['ES'])
        CVP_Info_By_Hour['WN'].append(temp_item[key]['WN'])
        CVP_Info_By_Hour['WS'].append(temp_item[key]['WS'])
        CVP_Info_By_Hour['Stop'].append(temp_item[key]['Stop'])
        CVP_Info_By_Hour['Total'].append(temp_item[key]['Total'])
    
    # print(CVP_Info_By_Hour)   
    # print(len(CVP_Info_By_Hour))  

CVP_Hour = pd.DataFrame.from_dict(CVP_Info_By_Hour) 
# print(CVP_Hour) 

# 轉換Geo pandas、查詢座標、儲存檔案
CVP_Hour[['lng', 'lat']] = CVP_Hour['GEO'].str.split(',', expand=True)
CVP_Hour['geometry'] = CVP_Hour.apply(
    lambda x: Point(
        x.lng,
        x.lat)
, axis=1)
CVP_Info.drop(['GEO'], axis=1, inplace=True)
print(CVP_Hour.head(5))
# CVP_Hour.to_csv("CVP_Hours.csv")
for i in range(len(DateTime_L)):
    print(DateTime_L[i])
    CVP_TEMP = CVP_Hour.loc[CVP_Hour['DateTime'] == DateTime_L[i]]
    CVP_TEMP.to_csv("CVP_"+DateTime_L[i]+".csv")
    CVP_TEMP_GEO = gpd.GeoDataFrame(
        CVP_TEMP,
        crs='EPSG:4326'
    )
    CVP_TEMP_GEO.to_file(
        'CVP_'+DateTime_L[i]+'_geo.geojson',
        driver='GeoJSON'
    )





