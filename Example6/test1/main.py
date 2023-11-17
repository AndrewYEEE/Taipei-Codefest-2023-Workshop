from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 
import time
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

Google_Result = {}
Related_Search = {}
Search_Key = "'臺北 台北 觀光 趨勢'"

chrome_options = webdriver.ChromeOptions()
# chrome_options = Options()
# chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox") # linux only
# chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--headless=new") # for Chrome >= 109
# user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
# chrome_options.add_argument(f'user-agent={user_agent}')
s = Service(r'D:\go\Taipei_city\Taipei-Codefest-2023-Workshop\Example6\test1\chromedriver\chromedriver.exe')
driver = webdriver.Chrome(service=s, options=chrome_options)
driver.implicitly_wait(10)
driver.get('https://www.google.com')  # 連線到Google搜尋網站
print(Search_Key)
try:
    # 定位搜尋輸入框
    search_input = driver.find_element(By.NAME, 'q')

    # 送出搜尋文字
    search_input.send_keys(Search_Key)
    time.sleep(1)

    # 送出ENTER按鍵
    search_input.send_keys(Keys.ENTER)
    time.sleep(1)

    search_tools = driver.find_element(By.CLASS_NAME, 't2vtad')     # 相關搜尋
    search_tools.click()
    time.sleep(1)

    search_tools_time = driver.find_elements(By.CSS_SELECTOR, 'a[aria-checked="false"]')     # 相關搜尋
    for re in search_tools_time:
        tmp = re.get_attribute('innerHTML')
        if tmp == " 過去 1 週":
            print(re.get_attribute('href'))
            driver.get(re.get_attribute('href'))
            break
        # tmp = re.find_element(By.TAG_NAME, 'div')
        # if tmp.text == " 過去 1 週":
        #     print(tmp)
        #     tmp.click()
        #     break
    
    #search_tools_time.click()
    time.sleep(1)




    # driver內容就是當前的頁面，不管網頁跳到哪裡去
    t_H =0 
    while True:
        driver.execute_script("window.scrollBy(0, 11000);") #滾輪向下滾11000
        time.sleep(1)
        height = driver.execute_script("return document.body.scrollHeight")
        print(height)
        if t_H == height:
            break
        t_H = height

    # 相關搜尋
    print('相關搜尋:')
    related = driver.find_elements(By.CLASS_NAME, 's75CSd')     # 相關搜尋
    for re in related:
        print(re.find_element(By.TAG_NAME, 'b').text)
    

    # 解析搜尋結果
    subjects = driver.find_elements(By.CLASS_NAME, 'LC20lb')  # 搜尋結果標題
    links = driver.find_elements(By.CLASS_NAME, 'yuRUbf')     # 搜尋結果連結

    all = zip(subjects, links)

    for item in all:
        addr = item[1].find_element(By.TAG_NAME, 'a').get_attribute('href')
        # print(f'{item[0].text} [{addr}]') 

    # 練習: 將搜尋結果的前五頁都爬出來
    for page_num in range(2, 6):
        print('Page', page_num)
        time.sleep(1)
        # 定位每一頁的分頁超連結
        # page = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="更多結果"]')
        page = driver.find_element(By.CLASS_NAME, 'T7sFge')
        if page == None:
            break
        print(page.text)
        time.sleep(2)
        if page.is_displayed() and page.is_enabled():
            # 點擊分頁超連結
            page.click()



            t_H =0 
            while True:
                driver.execute_script("window.scrollBy(0, 11000);") #滾輪向下滾11000
                time.sleep(1)
                height = driver.execute_script("return document.body.scrollHeight")
                print(height)
                if t_H == height:
                    break
                t_H = height
            

            temp_item = {}
            related_item = {}
            # 解析搜尋結果
            subjects = driver.find_elements(By.CLASS_NAME, 'LC20lb')  # 搜尋結果標題
            links = driver.find_elements(By.CLASS_NAME, 'yuRUbf')     # 搜尋結果連結

            # 相關搜尋
            # print('相關搜尋:')
            related = driver.find_elements(By.CLASS_NAME, 's75CSd')     # 相關搜尋
            for re in related:
                related_item[re.find_element(By.TAG_NAME, 'b').text] = "1"
                print(re.find_element(By.TAG_NAME, 'b').text)

            all = zip(subjects, links)

            for item in all:
                addr = item[1].find_element(By.TAG_NAME, 'a').get_attribute('href')
                temp_item[item[0].text] = addr
                # print(f'{item[0].text} {addr}') 

            Google_Result = temp_item
            Related_Search = related_item
        # time.sleep(1)
except ElementNotInteractableException as msg:
    print(msg)
    if msg == "Message: element not interactable: element has zero size":
        print("以上錯誤正常")
        pass

except NoSuchElementException:
    print('定位失敗')

driver.quit()



Google_Result_df=pd.DataFrame.from_dict(Google_Result,orient='index',columns=['link'])
print(Google_Result_df)

Related_Search_df=pd.DataFrame.from_dict(Related_Search,orient='index',columns=['none'])
print(Related_Search_df)


Google_Result_df.to_csv("Google_Result.csv",encoding="utf-8")
Related_Search_df.to_csv("Related_Search.csv",encoding="utf-8")