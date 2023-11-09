
import geopandas as gpd
import geocoder
import json
import pandas as pd
from shapely.geometry import LineString, Point, Polygon
import func



## **B.臺北市身障設施+臺北市身障社區長照機構+村里界 -> 身障友善機構**

# Output data- 身障友善機構
print("預想的結果:")
FILE_NAME = '.\Datasets\Processed\身障友善機構.csv'
friendly_institution = pd.read_csv(FILE_NAME)

print(friendly_institution.head())

# Input 1. 身障設施
print("Input 1. 臺北市身障設施 (身障機構收容暨空位狀態)")
# shp是一種儲存地理圖資的檔案格式，一定至少包含 3 個檔案： .shp (記錄地理圖資的點線面資訊)， .shx (地理圖資的索引)，.dbf (地理圖資的屬性資料)；
disable_institution = gpd.read_file('.\Datasets\Raw\身障設施_202309\身障設施_202309.shp')
print(disable_institution.head(3))

# Input 2. 臺北市身障社區長照機構
print("Input 2. 臺北市身障社區長照機構")
rid = '5e6dd32d-ac91-48cd-87ab-776fcc4811b7'
raw_disability_community_longterm_care_institutions = func.get_datataipei_api(rid)
dis_longterm = raw_disability_community_longterm_care_institutions.copy()
print(dis_longterm)



"""
### ETL Code
將`身障機構收容暨空位狀態`與`臺北市身障社區長照機構`合併成一個資料集，並產生適合的空間資訊。
1. 一致的columns name
2. 正確的column type
3. `臺北市身障社區長照機構`須加上"屬性"
4. 利用地址為`臺北市身障社區長照機構`加上行政區
5. (下半)利用Geocoder取得座標
6. (下半)產生TWD97座標值
7. (下半)利用村里界取得行政區
8. (下半)合併`身障機構收容暨空位狀態`與`臺北市身障社區長照機構`
"""


# 0.Set Config
LONGTERM_RID = '5e6dd32d-ac91-48cd-87ab-776fcc4811b7'
GITHUB_DATA_URL = 'https://raw.githubusercontent.com/tpe-doit/Taipei-Codefest-2023-Workshop/3-ETL/Datasets/Processed/%E8%BA%AB%E9%9A%9C%E5%8F%8B%E5%96%84%E6%A9%9F%E6%A7%8B.csv?token=GHSAT0AAAAAACHYWWNIZWPL36D3VIXR74BUZJY233Q'
GITHUB_DOWNLOAD_FILE_NAME = 'disable_friendly_institution.csv'
OUTPUT_FILENAME = 'disable_friendly_facility.csv'



# 1.Collection
# Input- 身障機構收容暨空位狀態
# 臺北市身障設施
print("Input 1. 重新讀取 臺北市身障設施 (以EPSG:3826格式轉碼座標)")
raw_disable_institution = gpd.read_file(
    f'.\Datasets\Raw\身障設施_202309\身障設施_202309.shp', from_crs='EPSG:3826'
)
dis_institution = raw_disable_institution.copy()

# 1.5 remove the institutions in New Taipei City
# .str是獲取panda內建的string API
# .str.startswith() 判斷個row data是否以给定的字符串开头
# 位元運算子〜是補碼運算子。如果操作數為1，則傳回0，如果為0，則傳回1
# 篩選Pandas DataFrame資料: df[df["math"] > 80]
print( ~dis_institution.address.str.startswith('新北市'))
dis_institution = dis_institution[
    ~dis_institution.address.str.startswith('新北市')]

print(dis_institution.head(3))

# value_counts依據type做統計
# ex: 按字母順序排列結果: value_counts().sort_index(ascending=True) 
# ex: 結果包括NA: value_counts(dropna=False)
print(dis_institution['type'].value_counts()) 


# 3.Rename 臺北市身障社區長照機構資料
print("Rename 臺北市身障社區長照機構資料")
print(dis_longterm.head())

col_map = {
    '機構類型': 'type',
    '機構名稱': 'name',
    '地址': 'addr',
    '電話': 'tel'
}
dis_longterm.rename(columns=col_map, inplace=True) #inplace=True修改原資料

print("Rename 臺北市身障設施資料")
dis_institution.rename(columns={'lon': 'lng'}, inplace=True)

# 4.Define data type
print("Define data type (請參考Example1)")


# 5.Fill missing value
print("Fill missing value (這部份範例沒有實作，單純看我們自己要怎麼處裡)")



# 6....... other process ......
print("其他處理")
print("臺北市身障社區長照機構須加上屬性")
dis_longterm['attr'] = '待查'

print("臺北市身障社區長照機構須加上行政區")
# 正則表達式取得指定字串，'臺北市([非數字的]{2個字}區)'
# https://docs.python.org/zh-tw/3/howto/regex.html
dis_longterm['town'] = dis_longterm['addr'].str.extract('臺北市([^\\d]{2}區)')

print(dis_longterm)

"""
# 空間資料處理 (geopandas)

GeoPandas implements two main data structures, a GeoSeries and a GeoDataFrame. These are subclasses of pandas.Series and pandas.DataFrame, respectively.

GeoPandas has three basic classes of geometric objects (which are actually shapely objects):
- Points / Multi-Points
- Lines / Multi-Lines
- Polygons / Multi-Polygons

Note that all entries in a GeoSeries need not be of the same geometric type, although certain export operations will fail if this is not the case.
"""

print("空間資料處理 (geopandas)")
addr_0 = dis_longterm.loc[0, 'addr'] #獲取地址欄位的第一筆資料
addr_0_info = geocoder.arcgis(addr_0) #查詢座標資訊
print(addr_0_info.json)
# 從查詢結果取出經緯度
addr_0_lng = addr_0_info.json['lng']
addr_0_lat = addr_0_info.json['lat']


# 第二筆反查，取出經緯度
addr_1 = dis_longterm.loc[1, 'addr'] #獲取地址欄位的第二筆資料
addr_1_info = geocoder.arcgis(addr_1)
# 從查詢結果取出經緯度
addr_1_lng = addr_1_info.json['lng']
addr_1_lat = addr_1_info.json['lat']

# transfer string to Point
point0 = Point(addr_0_lng, addr_0_lat) #製作座標點0
point1 = Point(addr_1_lng, addr_1_lat) #製作座標點1

# get info of point0
print(point0.area) #製作座標點面積
print(point0.bounds) # minx, miny, maxx, maxy #製作座標點面積範圍
print(point0.geom_type) #座標類型 (Points、Lines、Polygons)
print(point0.distance(point1)) #製作座標點0與1距離

"""
    Print("GeoPanda具體用法")

    # point
    print(Point(3, 4))

    # line
    print(LineString([(1, 2), (3, 4)]))

    # polygon
    print(Polygon([(1, 2), (3, 4), (5, 6)]))

    # GeoSeries
    s = gpd.GeoSeries(
        [
            Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
            Polygon([(10, 0), (10, 5), (0, 0)]),
            Polygon([(0, 0), (2, 2), (2, 0)]),
            LineString([(0, 0), (1, 1), (0, 1)]),
            Point(0, 1)
        ]
    )

    # GeoDataFrame
    d = {
        'col1': ['name1', 'name2'],
        'geometry': [Point(1, 2), Point(2, 1)]
    }
    gdf = gpd.GeoDataFrame(d, crs='EPSG:4326', geometry='geometry')

    # buffer
    # 緩衝區，緩衝區用於表示點、線、面等向量資料的影響範圍或服務範圍
    # buffer (distance, resolution)
    # distance：用於指定向外緩衝的距離
    # resolution：Polygon類型總是由有限個點所構成的，因此需要近似拼接出圓形的輪廓，resolution參數就用來決定每個四分之一圓弧上使用多少段連續的線段來近似拼接以表示圓的形狀，預設參數值為16，足以近似模擬圓面積的99.8%
    # https://www.cnblogs.com/feffery/p/12909284.html
    point0.buffer(1) #給予半徑為1m的緩衝區
    point0.buffer(1, resolution=1) # 


    # crs (Coordinate Reference System)

    # 'EPSG:3826' : Taiwan, bounds: (119.99, 20.41, 122.06, 26.72)
    # - X[east]: Easting (metre)
    # - Y[north]: Northing (metre)

    # 'EPSG:4326' : World, bounds: (-180.0, -90.0, 180.0, 90.0)
    # - Lat[north]: Geodetic latitude (degree)
    # - Lon[east]: Geodetic longitude (degree)

"""
# get 臺北市區界圖 from data.taipei
# URL = 'https://data.taipei/api/frontstage/tpeod/dataset/resource.download?rid=d8b7eb29-136f-49fc-b14b-3489d3656122'
FILE_NAME = '.\Datasets\Raw\臺北市區界圖_20220915'
print("Input 臺北市區界圖")
#直接整個資料夾讀入???
district_border = gpd.read_file(FILE_NAME, encoding='utf-8') 
print(district_border.head(2))

# # change crs
print("將臺北市區界圖 物件轉台灣常用座標格式")
district_border.crs = 'EPSG:3826' #轉台灣常用座標格式
print(district_border.head(2))

print("將臺北市區界圖 物件轉全球通用座標格式")
district_border = district_border.to_crs('EPSG:4326') #轉全球通用格式
print(district_border.head(2))

print("將臺北市區界圖 物件轉台灣常用座標格式")
# change crs
district_border = district_border.to_crs('EPSG:3826')

print("將臺北市區界圖 物件只保留['PTNAME', 'geometry']")
district_border = district_border[['PTNAME', 'geometry']]


print("將臺北市身障社區長照機構 物件加上geometry")
# lambda是匿名Method需告
# 以下等同於 
# dis_longterm['geometry'][i] = Point( 
#        geocoder.arcgis(dis_longterm['addr'][i]).json['lng'],
#        geocoder.arcgis(dis_longterm['addr'][i]).json['lat']
# )
dis_longterm['geometry'] = dis_longterm['addr'].apply(
    lambda x: Point(
        geocoder.arcgis(x).json['lng'],
        geocoder.arcgis(x).json['lat']
    )
)


# from pd to gpd
print("將臺北市身障社區長照機構 物件轉換為Geopandas物件")
dis_longterm = gpd.GeoDataFrame(
    dis_longterm,
    crs='EPSG:4326'
)
print(dis_longterm.head(2))

# change crs
print("將臺北市身障社區長照機構 物件轉台灣常用座標格式")
dis_longterm = dis_longterm.to_crs('EPSG:3826')
print(dis_longterm.head(2))

# get buffer
print("以臺北市身障社區長照機構 物件之座標，以1km半徑，設置每個座標點的影響範圍")
dis_longterm['buffer'] = dis_longterm['geometry'].buffer(1000)


# get the districts that intersect with buffer0
print("以臺北市身障社區長照機構 第一個座標範圍，看看臺北市區界(POLYGON)是否重疊")
buffer0 = dis_longterm.loc[0, 'buffer'] 
idx = buffer0.intersects(district_border['geometry']) #以第一筆交互所有資料的座標看有無重疊
print(idx) #有11筆資料，True者重疊
print('- '* 20)
print("獲取重疊的地區名稱")
print(district_border[idx].PTNAME.tolist()) #獲取重疊的地區名稱


print("擷取臺北市身障社區長照機構物件之 機構名稱 與 座標範圍 ")
dis_longterm_buffer = dis_longterm[['name', 'buffer']]
print(dis_longterm_buffer)

print("透過set_geometry()讓geopandas知道 buffer 欄位是座標點，以方便overlay計算")
dis_longterm_buffer = dis_longterm_buffer.set_geometry('buffer')
print(dis_longterm_buffer)


# overlay()用於計算兩個GeoDataFrame(可以當作地圖)，並依據how條件決定回傳的區域清單
# how=union : 將所有區域回傳
# how=intersection : 只回傳重疊區域
# how=symmetric_difference : 回傳沒有重疊的部分
# 簡單來說，就是給它兩張地圖，它將兩張地圖疊起來，然後給你合起來的地圖。
print("獲取 臺北市身障社區長照機構 + 臺北市區界圖 疊起來後的座標清單 (應該是為了確認在地圖上確實有該機構位置)")
overlay_df = gpd.overlay(
    dis_longterm_buffer,
    district_border,
    how='union'
).explode(index_parts=True).reset_index() #index_parts=True是Warning叫我加的
"""
# 由於重疊在一起的區域，預設會以"MULTIPOLYGON(可以當作三維空間，POLYGON是二維，很多個POLYGON疊在一起)"回傳，
# 回傳的清單會二維三維混在一起，會很混亂，因此如果想要回傳的結果都是POLYGON，則使用.explode().reset_index()

ex: 原始回傳:
    df1	df2	geometry
0	1.0	1.0	POLYGON ((2.00000 2.00000, 2.00000 1.00000, 1....
1	2.0	1.0	POLYGON ((2.00000 2.00000, 2.00000 3.00000, 3....
2	2.0	2.0	POLYGON ((4.00000 4.00000, 4.00000 3.00000, 3....
3	1.0	NaN	POLYGON ((2.00000 0.00000, 0.00000 0.00000, 0....
4	2.0	NaN	MULTIPOLYGON (((3.00000 3.00000, 4.00000 3.000...
5	NaN	1.0	MULTIPOLYGON (((2.00000 2.00000, 3.00000 2.000...
6	NaN	2.0	POLYGON ((3.00000 5.00000, 5.00000 5.00000, 5....

透過.explode().reset_index()攤開:
	level_0	level_1	df1	df2	geometry
0		0	   0	1.0	1.0	POLYGON ((2.00000 2.00000, 2.00000 1.00000, 1....
1		1	   0	2.0	1.0	POLYGON ((2.00000 2.00000, 2.00000 3.00000, 3....
2		2	   0	2.0	2.0	POLYGON ((4.00000 4.00000, 4.00000 3.00000, 3....
3		3	   0	1.0	NaN	POLYGON ((2.00000 0.00000, 0.00000 0.00000, 0....
4		4	   0	2.0	NaN	POLYGON ((3.00000 3.00000, 4.00000 3.00000, 4....
5		4	   1	2.0	NaN	POLYGON ((3.00000 3.00000, 2.00000 3.00000, 2....
6		5	   0	NaN	1.0	POLYGON ((2.00000 2.00000, 3.00000 2.00000, 3....
7		5	   1	NaN	1.0	POLYGON ((2.00000 2.00000, 1.00000 2.00000, 1....
8		6	   0	NaN	2.0	POLYGON ((3.00000 5.00000, 5.00000 5.00000, 5....
"""
print(overlay_df)
print("上面結果的意思:")
print("1. PTNAME如果NaN就代表該機構不在台北市的區域內，如果name欄位為NaN，就代表該座標沒有所屬機構")
print("2. 剩下的代表在台北市區域內，地圖上畫得出來的")


print("save as GeoJson儲存結果:")
# drop()刪除，axis=0 刪除row，axis=1 刪除col，這裡是將整個"geometry"刪除
dis_longterm.drop(['geometry'], axis=1, inplace=True)

# 將buffer改為geometry
dis_longterm.rename(columns={'buffer': 'geometry'}, inplace=True)

#添加fax、is_accessi、code欄位
dis_longterm['fax'] = ''
dis_longterm['is_accessi'] = ''

# 直接給予值到code欄位
# 這裡有個問題: 作者是因為知道 "臺北市身障社區長照機構" 資料就剩下四列，所以直接塞值上去，實際應用時不應該這麼做
dis_longterm['code'] = ['C01010001', 'C01010002', 'C01010003', 'C01010004']
dis_longterm = dis_longterm.to_crs('EPSG:4326')
print(dis_longterm.head(10))



print("將 臺北市身障設施 物件中'geometry'座標POINT替換成1km範圍POLYGON")
dis_institution['geometry'] = dis_institution['geometry'].buffer(1000) 
dis_institution = dis_institution.to_crs('EPSG:4326')
print(dis_institution)

# concat(,設定): 默認情況下是縱向(直向)連接兩個DataFrame
# axis=0 為直向合併
# ignore_index = True 可以忽略合併時舊的 index 欄位，改採用自動產生的 index
# concat 的 join 屬性有兩種模式 inner, outer(預設)
# outer(預設): 會直接把沒有的資料用 NaN 代替
# inner: 會直接把沒有完整資料的刪除掉
print("將 '臺北市身障設施' 與 '臺北市身障社區長照機構' 組合，後者放下面，空值補NaN")
dis_friendly_institution = pd.concat([dis_institution, dis_longterm])
dis_friendly_institution.to_crs('EPSG:4326') #Warning叫我這樣做

print("匯出dis_origin_radius.geojson")
dis_friendly_institution.to_file(
    'dis_origin_radius.geojson',
    driver='GeoJSON'
)

print("將 組合 物件中，'geometry'替換成每個POLYGON的中心點座標POINT")
dis_friendly_institution['geometry'] = dis_friendly_institution['geometry'].centroid

print("匯出dis_origin_center.geojson")
dis_friendly_institution.to_file(
    'dis_origin_center.geojson',
    driver='GeoJSON'
)

# groupby(): 分群，與SQL語法相同，會回傳DataFrameGroupBy物件，照理說要使用get_group("")獲取分好的Group
# https://zhuanlan.zhihu.com/p/101284491
# to_dict(): 將 DataFrame 轉換為字典
# size(): 元素總數
# 在 series 情況，它將返回行數。在 DataFrame 的情況下，它將返回行乘以列。在groupby()下，回傳每個Group內元素數
print("將 組合 物件依據區域分群")
stat = dis_friendly_institution.groupby('town').size().to_dict()
print(stat)

specified_order = [
    '北投區', '士林區', '內湖區', '南港區',
    '松山區', '信義區', '中山區', '大同區',
    '中正區', '萬華區', '大安區', '文山區'
]


print("將分群結果製作成all_components.js使用的data格式，以下結果: ")
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

with open('dis_friendly_institution.json', "w",encoding='utf8') as json_file:
    json.dump(results, json_file, ensure_ascii=False)


stat = dis_friendly_institution['type'].unique()
print(stat)


print("  ")
print("本範例缺點: ")
print("1. 作者是因為知道 '臺北市身障社區長照機構' 資料就剩下四列，所以code欄位直接塞4個值上去，實際應用時不應該這麼做")
print("2. 座標是否在台北市區域內的檢查只對 '臺北市身障社區長照機構' 檢查，沒有對 '臺北市身障設施' 檢查")



"""
    print("常用資料處理function")

    # read KML (讀取KML圖資檔案，Google Earth支援)
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    df = gpd.read_file(files, driver='KML')

    # Cleaning
    data[col].fillna(0) #用 0 取代 nan
    .fillna(value=0, inplace=True) # 用 0 取代 nan
    .fillna(value=df['Col'].mean(), inplace=True) #用平均值取代 nan
    .zfill(宽度) #依據宽度用零填充字符串的左侧

    # Reshape

    disability_welfare.melt()
    # 當我們需要多層級分拆資料時，透過 melt 功能就能省去繁雜的操作
    # .melt(frame, id_vars=None, value_vars=None, var_name=None, value_name='value', col_level=None)
    # frame : 你想要更動的 DataFrame。
    # id_vars: 可使用 tuple、list、或 ndarray，用以設定不想要被轉換的欄位。
    # value_vars: 可使用 tuple、list、或 ndarray，用以設定想要被拆解的欄位。 如果省略則拆解全部欄位。
    # var_name : 轉換後 id 的名稱。如果省略則設定為原本 DataFrame 的欄位名稱或是 variable。
    # value_name : 轉換後 value 欄位的名稱。如果省略則顯示原本 DataFrame 的欄位名稱或 value。
    # col_level : 可使用 int、string。如果 columns 是 MultiIndex，則使用該參數來進行選擇。
    # ex: pd.melt(df, id_var(['B'], value_var(['A']), var_name='varName', value_name='valName')


    disability_welfare.pivot()
    # 重塑DataFrame
    # DataFrame.pivot(*, columns, index=_NoDefault.no_default, values=_NoDefault.no_default)
    # ex: df.pivot(index='foo', columns='bar', values='baz')
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.pivot.html

    set(dis_longterm['id']) - set(dis_institution['id'])
    left_outer = dis_longterm.merge(dis_institution, how='left', on='id')
    left_outer.loc[left_outer[]'id_y'].isna()]

    # Transformation
    select_col = ['年份', '日間及住宿式照顧補助金額(元)', '生活補助金額(元)', '輔具補助金額(元)']
    disability_welfare = disability_welfare[select_col]
    cut, qcut
    time

    # Aggregation
    groupby(['col1', 'col2']).agg({'': 'nunique'})
"""


