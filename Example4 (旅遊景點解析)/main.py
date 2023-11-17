
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





# print("Input 1. 臺北市借問站據點資訊")
# RAW_DATA_URL = 'https://data.taipei/api/dataset/020a8fb8-1f08-4b2f-8da4-fde3cea384b7/resource/6b15fb25-920c-43c6-bb13-f8fd18966612/download'
# FILE_NAME = os.path.join('Datasets\Processed', '臺北市借問站據點資訊.csv')
# if os.path.exists(FILE_NAME):
#         os.remove(FILE_NAME) # if exist, remove it directly
# wget.download(RAW_DATA_URL,out=FILE_NAME)
# Information_Station = pd.read_csv(FILE_NAME,encoding='big5')
# Information_Station.rename(columns={'序號': 'no'}, inplace=True)
# Information_Station.rename(columns={'名稱': 'name'}, inplace=True)
# Information_Station.rename(columns={'地址': 'address'}, inplace=True)
# Information_Station['type'] = '借問站'

# #轉換Geo pandas、查詢座標、儲存檔案
# Information_Station['geometry'] = Information_Station['address'].apply(
#     lambda x: Point(
#         geocoder.arcgis(x).json['lng'],
#         geocoder.arcgis(x).json['lat']
#     )
# )
# Information_Station_GEO = gpd.GeoDataFrame(
#     Information_Station,
#     crs='EPSG:4326'
# )
# print(Information_Station_GEO)

# Information_Station_GEO.to_file(
#     'information_station_geo.geojson',
#     driver='GeoJSON'
# )



# print("Input 2. 臺北市旅遊服務中心據點資訊")
# RAW_DATA_URL = 'https://data.taipei/api/dataset/1a4efbfa-d616-4b20-b4a5-bb5be1ed3120/resource/96094c94-2644-480a-b31d-726571c054d9/download'
# FILE_NAME = os.path.join('Datasets\Processed', '臺北市旅遊服務中心據點資訊.csv')
# if os.path.exists(FILE_NAME):
#     os.remove(FILE_NAME) # if exist, remove it directly
# wget.download(RAW_DATA_URL,out=FILE_NAME)
# Service_Station = pd.read_csv(FILE_NAME,encoding='big5')
# Service_Station['type'] = '服務中心'

# # 轉換Geo pandas、查詢座標、儲存檔案
# Service_Station['geometry'] = Service_Station['address'].apply(
#     lambda x: Point(
#         geocoder.arcgis(x).json['lng'],
#         geocoder.arcgis(x).json['lat']
#     )
# )
# Service_Station_GEO = gpd.GeoDataFrame(
#     Service_Station,
#     crs='EPSG:4326'
# )
# print(Service_Station_GEO)

# Service_Station_GEO.to_file(
#     'service_station_geo.geojson',
#     driver='GeoJSON'
# )


# print("Input 3. 臺北市遊憩景點")
# API_PATH = 'Attractions/All'
# Travel_Loc = func.get_traveltaipei_api(API_PATH)
# Travel_Loc.drop(['id','links','files','target','staytime','remind','facebook','official_site','months','zipcode','open_status','name_zh','email'], axis=1, inplace=True)
# Travel_Loc_Pars = Travel_Loc[['name','distric','address','nlat','elong','category','service']]

# #================資料清理==============
# Travel_Loc_Pars.rename(columns={'elong': 'lng'}, inplace=True)
# Travel_Loc_Pars.rename(columns={'nlat': 'lat'}, inplace=True)
# # 去除新北市的機構
# Travel_Loc_Pars = Travel_Loc_Pars[
#     Travel_Loc_Pars.address.str.contains('|'.join(['臺北市', '台北市']))]

# # ====================處裡category (景點類型)========================
# Category_CP = Travel_Loc_Pars['category'].to_list() 
# for i in range(len(Category_CP)): 
#     C_Str = []
#     if Category_CP[i] :
#         for item in Category_CP[i]:
#             if item['name']:
#                 C_Str.append(item['name'])
#             else:
#                 C_Str.append("")
#     else:
#         C_Str.append("")
#     Category_CP[i] = ','.join(C_Str)
# Travel_Loc_Pars['category'] = Category_CP


# # ====================處裡service (提供的服務類型)========================
# Service_CP = Travel_Loc_Pars['service'].to_list() 
# for i in range(len(Service_CP)): 
#     C_Str = []
#     if Service_CP[i] :
#         for item in Service_CP[i]:
#             if item['name']:
#                 C_Str.append(item['name'])
#             else:
#                 C_Str.append("其他")
#     else:
#         C_Str.append("其他")
#     Service_CP[i] = ','.join(C_Str)
# Travel_Loc_Pars['service'] = Service_CP

# # ====================處裡address (地址)========================
# Address_CP = Travel_Loc_Pars['address'].to_list() 
# print(Address_CP)



# # 轉換Geo pandas、查詢座標、儲存檔案
# Travel_Loc_Pars['geometry'] = Travel_Loc_Pars['address'].apply(
#     lambda x: Point(
#         geocoder.arcgis(x).json['lng'],
#         geocoder.arcgis(x).json['lat']
#     )
# )
# Travel_Loc_Pars_GEO = gpd.GeoDataFrame(
#     Travel_Loc_Pars,
#     crs='EPSG:4326'
# )
# print(Travel_Loc_Pars_GEO)

# Travel_Loc_Sort_By_Distric_GEO = Travel_Loc_Pars_GEO.sort_values(by=['distric'], ascending=True)

# Travel_Loc_Sort_By_Distric_GEO.to_file(
#     'travel_loc_sort_by_distric_geo.geojson',
#     driver='GeoJSON'
# )


# # 依據category分類輸出
# Travel_Loc_Pars_CP = Travel_Loc_Pars_GEO.copy()
# Travel_Loc_Pars_CP['cate']=Travel_Loc_Pars_CP['category'].str.split(",")
# Travel_Loc_Sort_By_Category_GEO = Travel_Loc_Pars_CP.explode('cate').reset_index()
# Travel_Loc_Sort_By_Category_GEO.drop(['category'], axis=1, inplace=True)
# Travel_Loc_Sort_By_Category_GEO.rename(columns={'cate': 'category'}, inplace=True)
# Travel_Loc_Sort_By_Category_GEO = Travel_Loc_Sort_By_Category_GEO.sort_values(by=['category'], ascending=True)

# Travel_Loc_Sort_By_Category_GEO.to_file(
#     'travel_loc_sort_by_category_geo.geojson',
#     driver='GeoJSON'
# )


# # 依據service分類輸出
# Travel_Loc_Pars_CP2 = Travel_Loc_Pars_GEO.copy()
# Travel_Loc_Pars_CP2['ser']=Travel_Loc_Pars_CP2['service'].str.split(",")
# Travel_Loc_Sort_By_Service_GEO = Travel_Loc_Pars_CP2.explode('ser').reset_index()
# Travel_Loc_Sort_By_Service_GEO.drop(['service'], axis=1, inplace=True)
# Travel_Loc_Sort_By_Service_GEO.rename(columns={'ser': 'service'}, inplace=True)
# Travel_Loc_Sort_By_Service_GEO = Travel_Loc_Sort_By_Service_GEO.sort_values(by=['service'], ascending=True)
# print(Travel_Loc_Sort_By_Service_GEO)
# Travel_Loc_Sort_By_Service_GEO.to_file(
#     'travel_loc_sort_by_service_geo.geojson',
#     driver='GeoJSON'
# )


print("Input 4. 臺北市主要觀光遊憩區遊客人次")
RAW_DATA_URL = 'https://data.taipei/api/dataset/1ddeff62-8872-441c-aaf2-10fd0515ddb1/resource/eacbdbbc-8f7b-4156-b0c8-e6cbe9f4d9cb/download'
FILE_NAME = os.path.join('Datasets\Processed', '臺北市主要觀光遊憩區遊客人次.csv')
if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME) # if exist, remove it directly
wget.download(RAW_DATA_URL,out=FILE_NAME)
Recreational_Area_People_Num = pd.read_csv(FILE_NAME,encoding='big5')
Recreational_Area_People_Num = Recreational_Area_People_Num[-1:]
cols = Recreational_Area_People_Num.columns.to_list()
Recreational_Area_People_Num.loc[len(Recreational_Area_People_Num)] = cols
Recreational_Area_People_Num = Recreational_Area_People_Num.set_index('年別') #更改index
Recreational_Area_People_Num = Recreational_Area_People_Num.transpose()
Recreational_Area_People_Num=Recreational_Area_People_Num.reset_index(drop=True)
Recreational_Area_People_Num = Recreational_Area_People_Num.replace('-', 0) #將'-'替換成 '0'
cols = Recreational_Area_People_Num.columns.to_list()
Recreational_Area_People_Num.rename(columns={cols[0]: 'nums'}, inplace=True) #將"年別"名稱換成"address" 以免會錯意
Recreational_Area_People_Num.rename(columns={cols[1]: 'address'}, inplace=True) #將"年別"名稱換成"address" 以免會錯意


# ===== 修改資料類型 ======
Recreational_Area_People_Num["nums"] = Recreational_Area_People_Num["nums"].astype(int)

# ===== 處理address =======
Recreational_Area_People_Num["address"] = Recreational_Area_People_Num["address"].str.replace('|'.join(["遊客人次", "\[含商場\]","\[含廣場\]","\[商\]","\[\]"]), "") #移除 "遊客人次" 字樣
Recreational_Area_People_Num["address"] = Recreational_Area_People_Num["address"].str.replace("市立", "臺北市立") #移除 "遊客人次" 字樣
Recreational_Area_People_Num["address"] = Recreational_Area_People_Num["address"].str.replace(" ", "") #移除空格
Address_L = Recreational_Area_People_Num["address"].to_list()
substrings = ["臺北市", "台北市", "國立"]
for i in range(len(Address_L)):
     if any(x in Address_L[i] for x in substrings):
          continue
     else:
          Address_L[i] = "臺北市"+Address_L[i] #將地點資訊加入 "臺北市" 前綴
Recreational_Area_People_Num["address"] = Address_L 
Recreational_Area_People_Num = Recreational_Area_People_Num.sort_values(by=['nums'], ascending=False)


temp_PA = "\""+Recreational_Area_People_Num["address"]+"\","
temp = temp_PA.to_list()

for i in range(len(temp)):
    print(temp[i]) 



temp_PA = Recreational_Area_People_Num["address"].to_list()
results = {
    'data': [
        {
            'name':'臺北市主要觀光遊憩區遊客人次',
            'data': [
                {
                    'x': row['address'],
                    'y': row['nums']
                }
                for index, row in Recreational_Area_People_Num.iterrows()
            ]
        }
    ]
}

print(results)
with open('recreational_area_people_num.json', "w",encoding='utf8') as json_file:
    json.dump(results, json_file, ensure_ascii=False)



# 轉換Geo pandas、查詢座標、儲存檔案
# Recreational_Area_People_Num['geometry'] = Recreational_Area_People_Num['address'].apply(
#     lambda x: Point(
#         geocoder.arcgis(x).json['lng'],
#         geocoder.arcgis(x).json['lat']
#     )
# )
# Recreational_Area_People_Num_CP_GEO = gpd.GeoDataFrame(
#     Recreational_Area_People_Num,
#     crs='EPSG:4326'
# )



# # 注意: 每種座標系統對distance的單位與運算不同，切換成以"m"為單位的座標系統，這樣buffer才能正常運作
# # Recreational_Area_People_Num_CP_GEO = Recreational_Area_People_Num_CP_GEO.to_crs('EPSG:3826')

# # Recreational_Area_People_Num_CP_GEO['geometry'] = Recreational_Area_People_Num_CP_GEO['geometry'].buffer(Recreational_Area_People_Num_CP_GEO['nums']/1000+1, resolution=2) #繪製mutlipolygon，為了Mapbox的3D效果

# # Recreational_Area_People_Num_CP_GEO = Recreational_Area_People_Num_CP_GEO.to_crs('EPSG:4326')


# print(Recreational_Area_People_Num_CP_GEO)
# Recreational_Area_People_Num_CP_GEO.to_file(
#     'recreational_area_people_num_cp_geo.geojson',
#     driver='GeoJSON'
# )


