import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.ui import Select

# from http://www.marinamele.com/selenium-tutorial-web-scraping-with-selenium-and-python
def init_driver(download_path):
    profile = webdriver.FirefoxProfile();
    profile.set_preference("browser.download.dir", download_path)
    profile.set_preference("browser.download.folderList", 2) # ?
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/force-download, text/csv")
    driver = webdriver.Firefox(firefox_profile=profile)
    driver.wait = WebDriverWait(driver, 5)
    return driver

def get_stn_id_from_url(url):
    for s in url.split('&'):
        if 'StationID' in s: return s.split('=')[1]
    return None

def get_almanac(driver, search_term, download_path):
    almanac_search_url = ('http://climate.weather.gc.ca/climateData/almanacselection_e.html'
                          '?Month=9&Day=23&Year=2015&timeframe=4&txtStationName=')
    driver.get(almanac_search_url)
    box = driver.wait.until(EC.presence_of_element_located((By.ID, 'stationName')))
    button = driver.wait.until(EC.element_to_be_clickable((By.NAME, "stnSubmit")))
    box.send_keys(search_term)
    button.click()
    
    # if there is a search results screen
    if 'almanac_results' in driver.current_url:
        # there are many stnSubmit buttons on the page. click the first button. 
        first_button = driver.wait.until(EC.element_to_be_clickable((By.NAME, "stnSubmit")))
        first_button.click()
    
    stn_id = get_stn_id_from_url(driver.current_url)
    download_data_button = driver.wait.until(EC.element_to_be_clickable((By.NAME, "submit")))
    # delete old datafile
    if os.path.exists(download_path + 'eng-almanac-0101-1231.csv'):
        os.remove(download_path + 'eng-almanac-0101-1231.csv')
    download_data_button.click()
    time.sleep(5)
    os.rename(download_path + 'eng-almanac-0101-1231.csv', download_path+create_filename(search_term))
    
    
def get_metadata(file_path):
    f = open(file_path, 'r')
    s = f.readlines()
    f.close()
    obj = {}
    n = 0
    while s[n] != '\n':
        prop = s[n].split(',')[0][1:-1]
        val = s[n].split(',')[1][1:-2]
        obj[prop] = val
        n+=1
    return obj

def create_filename(name):
    return ''.join(['_' if c == ' ' else c for c in name]) + '.csv'

_ = sys.argv[0] # this filename
save_path = sys.argv[1]
city = sys.argv[2]

# almanac_path = "/Users/stephenmcmurtry/work/weather_chart/data/almanac/"
driver = init_driver(save_path)
get_almanac(driver, city, save_path)
driver.quit()