
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


FILE_NAME = os.path.join('..\\test4', 'queries_data台北_rising.csv')
queries_rising_df1 = pd.read_csv(FILE_NAME)
# print(queries_rising_df1)

FILE_NAME = os.path.join('..\\test4', 'queries_data臺北_rising.csv')
queries_rising_df2 = pd.read_csv(FILE_NAME)
# print(queries_rising_df2)

queries_rising_df = pd.concat([queries_rising_df1,queries_rising_df2])
queries_rising_df['value'] = queries_rising_df['value'].astype(int)
queries_rising_df = queries_rising_df.loc[:, ~queries_rising_df.columns.str.contains('^Unnamed')]
queries_rising_df['query'] = queries_rising_df['query'].str.replace(" ", "") #移除空格
queries_rising_df = queries_rising_df.sort_values(by=['value'], ascending=False).reset_index(drop=True)
print(queries_rising_df)
# print(queries_rising_df.to_dict())
# print(queries_rising_df.columns)
stat = queries_rising_df.to_dict()
# print(stat)

results = {
    'data': [
        {
            'name':'Google關鍵字熱度查詢',
            'data': [
                {
                    'x': stat['query'][key],
                    'y': stat['value'][key]
                }
                for key in stat['query']
            ]
        }
    ]
}
print(results)
with open('queries_rising.json', "w",encoding='utf8') as json_file:
    json.dump(results, json_file, ensure_ascii=False)

# FILE_NAME = os.path.join('..\\test4', 'queries_data台北_top.csv')
# queries_top_df1 = pd.read_csv(FILE_NAME)
# print(queries_top_df1)

# FILE_NAME = os.path.join('..\\test4', 'queries_data臺北_top.csv')
# queries_top_df2 = pd.read_csv(FILE_NAME)
# print(queries_top_df2)






