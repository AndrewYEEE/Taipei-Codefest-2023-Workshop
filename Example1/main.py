
import geopandas as gpd
import geocoder
import json
import pandas as pd
from shapely.geometry import LineString, Point, Polygon
import func


## **A.臺北市身心障礙者福利服務 -> 無障礙需求歷年趨勢**

### Designing Processing Plan
"""
(實際步驟是先了解`Input data`與`Output data`才制定出`處理計畫`，但為了閱讀方便，將計畫放在最前面)
1. 修改欄位名
2. 民國年修改成西元年
3. 定義data type
4. 選擇指定欄位
"""

print("目標: A.臺北市身心障礙者福利服務 -> 無障礙需求歷年趨勢")

# Want Ouput data: 無障礙需求歷年趨勢
print("Want Ouput data: 無障礙需求歷年趨勢")
FILE_NAME = ".\Datasets\Processed\無障礙需求歷年趨勢.csv"
accessibility_need = pd.read_csv(FILE_NAME)
print(accessibility_need.head())


# Input data- 臺北市身心障礙者福利服務
print("Input data- 臺北市身心障礙者福利服務")
disability_welfare = func.get_datataipei_api('a09d5ff1-6b83-4bce-abbb-480b126db611')
print(disability_welfare.head(3))
print(disability_welfare.dtypes)




"""
### ETL code

預設儲存資料於`/content`路徑下
"""

import pandas as pd
# Designing Processing Plan
# 1. 修改欄位名，[]變成()
# 2. 民國年修改成西元年
# 3. 定義data type，具量詞欄位應為float

# 0.Set Config
RID = 'a09d5ff1-6b83-4bce-abbb-480b126db611'
# GITHUB_DATA_URL = 'https://raw.githubusercontent.com/tpe-doit/Taipei-Codefest-2023-Workshop/2-Initial-Data-Cleaning-Visualization/Datasets/Processed/%E7%84%A1%E9%9A%9C%E7%A4%99%E9%9C%80%E6%B1%82%E6%AD%B7%E5%B9%B4%E8%B6%A8%E5%8B%A2.csv?token=GHSAT0AAAAAACHYWWNICD23CYPEE25UQQSSZJXOERA'
GITHUB_DOWNLOAD_FILE_NAME = ".\Datasets\Processed\無障礙需求歷年趨勢.csv"


# 1.Collection
# input 臺北市身心障礙者福利服務
print("input 臺北市身心障礙者福利服務")
raw_disability_welfare = func.get_datataipei_api(RID)
disability_welfare = raw_disability_welfare.copy() 


# 2.Inspection
print('臺北市身心障礙者福利服務:')
print(disability_welfare.columns)

print('先檢查一遍有無NaN資料: ')
print(disability_welfare.isna().sum(axis=0)) #axis=0代表以Column做為Sum的標的

print('實際以"住宿及照顧福利機構核定服務人數"檢查，發現空資料是以"-"表示而不是NaN:')
print(disability_welfare['住宿及照顧福利機構核定服務人數[人]'].value_counts(dropna=False)) #dropna=False代表不丟棄NaN

# 3.Rename
# 修改欄位名，[]變成()
# disability_welfare.rename(columns={'old_column_name': 'new_column_name'}, inplace=True)
# disability_welfare.columns = ['column_name1', 'column_name2']

print('Rename 將所有Column中"[]"換成"()"、替換"年份":')
col_map = {}
for col in disability_welfare.columns:
    new_col = col.replace('[', '(').replace(']', ')')
    col_map[col] = new_col
disability_welfare.rename(columns=col_map, inplace=True) #inplace: 是否要改變原數據，False是不改變，True是改變，預設是False
disability_welfare.rename(columns={'年別': '年份'}, inplace=True)
print(disability_welfare.columns)

# 4.Define data type
# 定義data type，具量詞欄位應為float
# (int無法容許np.nan!!!!!)
print("Define data type (int無法容許np.nan)")

# data.Chinese === data["Chinese"]
disability_welfare['年份'] = disability_welfare['年份'].astype(str) #將指定的Column資料轉換成指定類型
df_row_len, df_col_len = disability_welfare.shape #獲取row,col數量
for col_index in range(3, df_col_len): #從第3的col往後獲取
    col_name = disability_welfare.columns[col_index] #獲取該col的名稱
    fine_col = disability_welfare[col_name].copy() #將該col擁有的rows複製
    # panda可以直接對整個rows進行邏輯運算
    # 運算結果會以bool array[]方式回傳
    is_dash = (fine_col=='-') #全部檢查滿足=='-'者標記為True
    fine_col.loc[is_dash] = None #將標記為True的row設為None先清空
    fine_col = fine_col.astype(float)  #當清空的欄位轉成float時，就會是NaN
    disability_welfare[col_name] = fine_col #整個rows複寫回去
print(disability_welfare)



print('重新檢查一遍有無NaN資料: ')
print(disability_welfare.isna().sum(axis=0)) #axis=0代表以Column做為Sum的標的

# DataFrame.iloc[“索引數字”, “欄位數字”]
# data.iloc[:,0]
# data.iloc[:,:2]
# describe: 一次求得計數(count), 均值(mean), 標準差(std), max, min, 中位數, 1/4位數, 3/4位數
print(disability_welfare.iloc[:, 3:].describe())

# 5.Fill missing value
# 這部份範例沒有實作，單純看我們自己要怎麼處裡
print("Fill missing value (這部份範例沒有實作，單純看我們自己要怎麼處裡)")

# 6. ......other process......
print("其他處理")
# 民國年修改成西元年
# panda中內建的字串處裡功能都在.str中，例如: .str.cat()、.str.replace()、.str.split()....
chinese_year = disability_welfare['年份'].str.replace('年', '')  #取代rows內字串
bc_year = chinese_year.astype(int) + 1911 #民國 轉 西元
bc_year = bc_year.astype(str) + '年' # 補回 "年"
disability_welfare['年份'] = bc_year # 塞回"年分" column
print(disability_welfare['年份'])

# 7.Select
# 年份                 object
# 日間及住宿式照顧補助金額(元)    object
# 生活補助金額(元)          object
# 輔具補助金額(元)          object
print("資料篩選")
select_col = ['年份', '日間及住宿式照顧補助金額(元)', '生活補助金額(元)', '輔具補助金額(元)']
disability_welfare = disability_welfare[select_col] #獲取指定欄位
disability_welfare.head()

# 8.Save
OUTPUT_FILENAME = 'disability_welfare_over_the_years.csv'
disability_welfare.to_csv(OUTPUT_FILENAME, index=False, encoding='UTF-8')

print("  ")
print("本範例缺點: ")
print("1. 並沒有排除NaN欄位或初始化NaN欄位")
print("2. 中途由於NaN，將欄位值皆轉float，但實際上應該要先檢查欄位是否適合轉float")
print("3. 最後輸出仍保持float，但金額應該要以int比較適合，但int不支援NaN")



