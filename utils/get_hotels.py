from typing import Dict, List, Union
from utils.api_reqiest import request_to_api
from config_data.config import RAPID_API_HEADERS, RAPID_API_ENDPOINTS
from loguru import logger
import json
from utils.misc.get_address import get_hotel_address
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time


@logger.catch
def parse_hotels(data_dict: Dict) -> Union[Dict[str, List[Dict]], None]:
    """
    Функция делает запрос в request_to_api и десериализирует результат. Если запрос получен и десериализация прошла -
    возвращает обработанный результат в виде словаря, иначе None.

    :param data_dict: Словарь - данные для запроса по api.
    :return: None или словарь с ключом 'results' и значением - списком словарей полученных отелей.
    """

    if data_dict.get('last_command') == 'highprice':
        sort_order = 'PRICE_HIGH_TO_LOW'
    elif data_dict.get('last_command') == 'bestdeal':
        sort_order = 'DISTANCE'
    else:
        sort_order = 'PRICE_LOW_TO_HIGH'

    check_in_lst2 = (str(data_dict["start_date"])).split("-")
    check_out_lst2 = (str(data_dict["end_date"])).split("-")

    if data_dict.get('last_command') in ('bestdeal', 'lowprice'):
        if data_dict.get('last_command') == 'lowprice':

            payload = {
                "destination": {"regionId": data_dict['city_id']},
                "resultsSize": data_dict['amount_hotels'],
                "checkInDate": {
                    "day": int(check_in_lst2[2]),
                    "month": int(check_in_lst2[1]),
                    "year": int(check_in_lst2[0])
                },
                "checkOutDate": {
                    "day": int(check_out_lst2[2]),
                    "month": int(check_out_lst2[1]),
                    "year": int(check_out_lst2[0])
                },
                "rooms": [{"adults": 1, "children": []}],
                "sort": sort_order,
            }

        else:
            payload = {
                "destination": {"regionId": data_dict['city_id']},
                "pageNumber": "1",
                "resultsSize": data_dict['amount_hotels'],
                "checkInDate": {
                    "day": int(check_in_lst2[2]),
                    "month": int(check_in_lst2[1]),
                    "year": int(check_in_lst2[0])
                },
                "checkOutDate": {
                    "day": int(check_out_lst2[2]),
                    "month": int(check_out_lst2[1]),
                    "year": int(check_out_lst2[0])
                },
                "rooms": [{"adults": 1, "children": []}],
                "sort": sort_order,
                "filters": {"price": {
                    "max": data_dict['end_price'],
                    "min": data_dict['start_price']
                }},
            }

        response = request_to_api(
            method_type='POST',
            url=RAPID_API_ENDPOINTS['hotel-list'],
            payload=payload,
            headers=RAPID_API_HEADERS)
        data = json.loads(response.text)

        hotels = dict()
        if data.get('data').get('propertySearch').get('properties'):
            for element in data.get('data').get('propertySearch').get('properties'):
                if len(hotels) < 25:
                    if element.get('__typename') == 'Property':
                        hotel_id = element.get('id')
                        hotel_primary_img = element.get('propertyImage').get('image').get('url')
                        current_price = round(element.get('price').get('lead').get('amount'), 2)
                        hotel_distance = round(float(
                            element.get('destinationInfo').get('distanceFromDestination').get('value')) * 1.6, 2)
                        total_price = ''
                        for elem in element.get('price').get('displayMessages'):
                            for k, v in elem.items():
                                if k == 'lineItems':
                                    for var in v:
                                        for n, val in var.items():
                                            if n == "value" and "total" in val:
                                                total_price = val
                                                break
                        hotels[element.get('name')] = [
                            hotel_id, hotel_distance, current_price, hotel_primary_img, total_price
                        ]
                else:
                    break
        return hotels

    elif data_dict.get('last_command') == 'highprice':

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(cache_valid_range=10).install()))
        url = f'https://www.hotels.com/Hotel-Search?' \
              f'adults=1' \
              f'&children=' \
              f'&d1={int(check_in_lst2[0])}-{int(check_in_lst2[1])}-{int(check_in_lst2[2])}' \
              f'&endDate={int(check_out_lst2[0])}-{int(check_out_lst2[1])}-{int(check_out_lst2[2])}' \
              f'&d2={int(check_out_lst2[0])}-{int(check_out_lst2[1])}-{int(check_out_lst2[2])}' \
              f'&latLong=' \
              f'&mapBounds=' \
              f'&pwaDialog=' \
              f'&regionId={data_dict["city_id"]}' \
              f'&rooms=1' \
              f'&semdtl=' \
              f'&sort={sort_order}' \
              f'&sortTriggerPill=' \
              f'&startDate={int(check_in_lst2[0])}-{int(check_in_lst2[1])}-{int(check_in_lst2[2])}' \
              f'&theme=' \
              f'&useRewards=true' \
              f'&userIntent='
        driver.get(url)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(5)
        html = driver.page_source

        hotel_name = re.findall(r'class="is-visually-hidden">More information about (.+?), opens in a new tab', html)
        hotel_id = re.findall(r'expediaPropertyId=(\d+)&amp', html)
        hotel_price_period = re.findall(r'>The price is (€\d+,?\d+)</div>', html)
        hotel_price_night = re.findall(r'"uitk-text uitk-type-end uitk-type-200 uitk-text-default-theme">(€\d+,?\d+) per night', html)

        hotel_item = dict()
        hotel_list = list()
        hotels = dict()
        amount_hotels = data_dict['amount_hotels']

        for el in range(amount_hotels):
            h_id = str(hotel_id[el])
            h_price_period = str(hotel_price_period[el])
            h_price_night = str(hotel_price_night[el])
            hotel = list()
            hotel.extend([h_id, 'distance', h_price_night, 'link', h_price_period])
            hotel_item[hotel_name[el]] = hotel
            hotel_list.append(hotel_item)

            hotels[hotel_name[el]] = [h_id, 'distance', h_price_night, 'link', h_price_period]

        return hotels


@logger.catch
def process_hotels_info(hotels_info_list, data_dict: Dict) -> Dict[int, Dict]:
    """
    Функция получает список словарей - результат парсинга отелей, выбирает нужную информацию, обрабатывает и складывает
    в словарь hotels_info_dict

    :param hotels_info_list: Список со словарями. Каждый словарь - полная информация по отелю (результат парсинга).
    :param amount_nights: Количество ночей.
    :return: Словарь с информацией по отелю: {hotel_id: {hotel_info}} (теоретически может быть пустым).
    """

    hotels_info_dict = dict()
    for key, value in hotels_info_list.items():
        hotel_name = key
        hotel_id = value[0]
        price_per_night = value[2]
        distance_city_center = value[1]
        total_price = value[4]
        if data_dict.get('last_command') != 'highprice':
            hotel_neighbourhood = get_hotel_address(value[0])
        else:
            hotel_neighbourhood = 0

        hotels_info_dict[hotel_id] = {
            'name': hotel_name,
            'price_per_night': price_per_night,
            'total_price': total_price,
            'distance_city_center': distance_city_center,
            'hotel_url': f'https://www.hotels.com/h{hotel_id}.Hotel-Information/',
            'hotel_neighbourhood': hotel_neighbourhood
        }
    return hotels_info_dict


@logger.catch
def get_hotel_info_str(hotel_data: Dict, amount_nights: int) -> str:
    """
    Функция преобразует данные по отелю из словаря в строку с html.
    Используется для вывода информации через сообщение (bot.send_message).

    :param hotel_data: Словарь с информацией по отелю.
    :param amount_nights: Количество ночей.
    :return: Строка с html с информацией по отелю
    """

    result = f"<b> Отель:</b> {hotel_data['name']}\n"

    if hotel_data['hotel_neighbourhood'] != 0:
        result +=\
            f"<b> Район:</b> {hotel_data['hotel_neighbourhood']}\n" \
            f"<b> Расстояние до центра:</b> {hotel_data['distance_city_center']} Км\n" \
            f"<b> Цена за 1 ночь: </b> от {hotel_data['price_per_night']}$\n" \
            f"<b> Примерная стоимость за {amount_nights} ноч.:</b> {hotel_data['total_price']}$\n" \
            f"<b> Подробнее об отеле <a href='{hotel_data['hotel_url']}'>на сайте >></a></b>"

    else:
        result +=\
            f"<b> Цена за 1 ночь: </b> от {hotel_data['price_per_night']}$\n" \
            f"<b> Примерная стоимость за {amount_nights} ноч.:</b> {hotel_data['total_price']}$\n" \
            f"<b> Подробнее об отеле <a href='{hotel_data['hotel_url']}'>на сайте >></a></b>"

    return result


@logger.catch
def get_hotel_info_str_nohtml(hotel_data: Dict, amount_nights: int) -> str:
    """
    Функция преобразует данные по отелю из словаря в строку без html.
    Используется для вывода информации через медиа группу (bot.send_media_group).

    :param hotel_data: Словарь с информацией по отелю.
    :param amount_nights: Количество ночей.
    :return: Строка без html с информацией по отелю.
    """
    result = f"Отель: {hotel_data['name']}\n"

    if hotel_data['hotel_neighbourhood'] != 0:
        result += \
            f"Район: {hotel_data['hotel_neighbourhood']}\n" \
            f"Расстояние до центра: {hotel_data['distance_city_center']} Км\n" \
            f"Цена за 1 ночь: от {hotel_data['price_per_night']}$\n" \
            f"Примерная стоимость за {amount_nights} ноч.: {hotel_data['total_price']}$\n" \
            f"Подробнее об отеле {hotel_data['hotel_url']}"

    else:
        result += \
            f"Цена за 1 ночь: от {hotel_data['price_per_night']}$\n" \
            f"Примерная стоимость за {amount_nights} ноч.: {hotel_data['total_price']}$\n" \
            f"Подробнее об отеле {hotel_data['hotel_url']}"

    return result
