from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 
import time
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = webdriver.ChromeOptions()
# chrome_options = Options()
# chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox") # linux only
# chrome_options.add_argument("--disable-notifications")
# chrome_options.add_argument("--headless=new") # for Chrome >= 109
user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument('lang=zh_TW.UTF-8')
chrome_options.add_experimental_option('useAutomationExtension', False)  # 取消Chrome受控制提示
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 取消 Chrome 受控制提示
s = Service(r'D:\go\Taipei_city\Taipei-Codefest-2023-Workshop\Example6\test1\chromedriver\chromedriver.exe')
driver = webdriver.Chrome(service=s, options=chrome_options)
driver.implicitly_wait(10)
driver.get('https://trends.google.com.tw/trends/explore?geo=TW&hl=zh-TW')  # 連線到Google搜尋網站
print(driver.title)
try:
    time.sleep(1)
    # 定位搜尋輸入框
    search_input = driver.find_element(By.CLASS_NAME, 'VfPpkd-fmcmS-wGMbrd')
    print(search_input)
    time.sleep(1)
    # 點擊分頁超連結
    search_input.click()

    # 送出搜尋文字

    time.sleep(1)
    search_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="新增搜尋字詞"]')
    search_input.send_keys('臺北')
    time.sleep(1)

    # search_input.send_keys(Keys.ENTER)
    # time.sleep(1)

    # RELATED_TOPICS = driver.find_element(By.CSS_SELECTOR, 'trends-widget[widget-name="RELATED_TOPICS"]')
    # TOPICS_BUTTON = RELATED_TOPICS.find_element(By.CSS_SELECTOR, 'button[title="CSV"]')
    # TOPICS_BUTTON.click()


    # time.sleep(1)
    # RELATED_QUERIES = driver.find_element(By.CSS_SELECTOR, 'trends-widget[widget-name="RELATED_QUERIES"]')
    # QUERIES_BUTTON = RELATED_QUERIES.find_element(By.CSS_SELECTOR, 'button[title="CSV"]') 
    # QUERIES_BUTTON.click()


except NoSuchElementException:
    print('失敗')


driver.quit()
