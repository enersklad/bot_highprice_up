import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(cache_valid_range=10).install()))
url = 'https://www.hotels.com/Hotel-Search?adults=2&children=&d1=2023-07-09&d2=2023-07-10&destination=London%2C%20England%2C%20United%20Kingdom&endDate=2023-08-07&latLong=&mapBounds=&pwaDialog=&regionId=2114&rooms=1&semdtl=&sort=PRICE_HIGH_TO_LOW&sortTriggerPill=&startDate=2023-08-01&theme=&useRewards=true&userIntent='
driver.get(url)
driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
time.sleep(5)
html = driver.page_source

hotel_name = re.findall(r'class="is-visually-hidden">More information about (.+?), opens in a new tab', html)
hotel_id = re.findall(r'expediaPropertyId=(\d+)&amp', html)
hotel_price_period = re.findall(r'>The price is (€\d+,?\d+)</div>', html)
hotel_price_night = re.findall(r'"uitk-text uitk-type-end uitk-type-200 uitk-text-default-theme">(€\d+,?\d+) per night', html)

hotel = list()
hotel_item = dict()
hotel_list = list()
hotel_dict = dict()

print('hotel_name_LST=', hotel_name)
print('hotel_id_LST=', hotel_id)
print('hotel_price_period_LST=', hotel_price_period)
print('hotel_price_night_LST=', hotel_price_night)

for el in range(30):
    h_id = str(hotel_id[el])
    h_name = str(hotel_name[el])
    h_price_period = str(hotel_price_period[el])
    h_price_night = str(hotel_price_night[el])
    hotel = list()
    hotel.extend([h_id, '999', h_price_night, 'href', h_price_period])
    hotel_item[hotel_name[el]] = hotel
    hotel_list.append(hotel_item)

    hotel_dict[hotel_name[el]] = [h_id, '999', h_price_night, 'href', h_price_period]

print('hotel_list=', hotel_list)
print('hotel_dict=', hotel_dict)
