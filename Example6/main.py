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
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--headless=new") # for Chrome >= 109
chrome_options.add_argument("--window-size=1920,1080")
user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
chrome_options.add_argument(f'user-agent={user_agent}')
s = Service(r'D:\go\Taipei_city\Taipei-Codefest-2023-Workshop\Example6\chromedriver\chromedriver.exe')
driver = webdriver.Chrome(service=s, options=chrome_options)
# driver.implicitly_wait(10)
driver.get('https://www.google.com')  # 連線到Google搜尋網站
print(driver.title)
driver.close()