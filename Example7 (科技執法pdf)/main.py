
import geopandas as gpd
import geocoder
import json
import pandas as pd
from shapely.geometry import LineString, Point, Polygon
import func
from re import search
import wget 
import os
import csv
import re
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


"""
用以下網站將pdf轉csv
https://products.aspose.app/pdf/zh-hant/conversion/pdf-to-csv

"""


print("Input 1. 臺北市政府警察局固定式科技執法設備設置地點一覽表")
FILE_NAME = os.path.join('', '臺北市政府警察局固定式科技執法設備設置地點一覽表-1120630.csv')
file = open(FILE_NAME,encoding='utf-8')
csvreader = csv.reader(file)
csv_rows = []

for row in csvreader:
    count = 0
    length = 0
    for it in row:
        length = length + 1
        if it == '':
            count = count + 1
    if count > 2:
        continue  #忽略標題與有問題資料
    if row[0] == '編號':
        continue  #忽略欄位標題
    if length < 5 :
        continue #忽略欄位不足資料
    for i in range(len(row)):
        if row[i-1] == '':
            row.pop(i-1) #移除空欄位
    csv_rows.append(row)
# print(rows)

# 請務必記得關閉檔案
file.close()

Technology_Law = pd.DataFrame(csv_rows, columns =['No', 'Location', 'Item', 'Dist', 'Direction'])
pattern = '|'.join(['\r\n','\n',' '])
Technology_Law['No'] = Technology_Law['No'].str.replace(pattern, '',regex=True)
Technology_Law['Location'] = Technology_Law['Location'].str.replace(pattern, '',regex=True)
Technology_Law['Item'] = Technology_Law['Item'].str.replace(pattern, '',regex=True)
Technology_Law['Dist'] = Technology_Law['Dist'].str.replace(pattern, '',regex=True)
Technology_Law['Direction'] = Technology_Law['Direction'].str.replace(pattern, '',regex=True)
Technology_Law.drop(['No'], axis=1, inplace=True)

for index,row in Technology_Law.iterrows():
    if "(" in row['Location']:
        NumRegex = re.compile(r'[(](.+?)[])]')
        subs = Technology_Law.at[index,'Location']
        print(subs)
        ans = NumRegex.search(subs).group(1)
        print(ans)
        Technology_Law.at[index,'Location'] = ans



pattern = '|'.join(['口','口周邊','前','上方','周邊'])
Technology_Law['Location'] = Technology_Law['Location'].str.replace(pattern, '',regex=True)
# 先將business item轉換成List
Technology_Law['Location']=Technology_Law['Location'].str.split("與")
# 依據List擴展出來
Technology_Law = Technology_Law.explode('Location').reset_index()


Technology_Law['Location'] = "臺北市"+Technology_Law['Location']
print(Technology_Law)





print("ETL7 : 將地址加以解析經緯度座標 (這個要一點時間，它查一個座標蠻久的)")
Technology_Law['geometry'] = Technology_Law['Location'].apply(
    lambda x: Point(
        geocoder.arcgis(x).json['lng'],
        geocoder.arcgis(x).json['lat']
    )
)


# from pd to gpd
Technology_Law_GEO = gpd.GeoDataFrame(
    Technology_Law,
    crs='EPSG:4326'
)
print(Technology_Law_GEO)

Technology_Law_GEO.to_file(
    'technology_law_geo.geojson',
    driver='GeoJSON'
)







