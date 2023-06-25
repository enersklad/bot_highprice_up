data_dict = {'city_id': '2114', 'amount_hotels': '2'}
check_in_lst2 = ('2023', '08', '01')
check_out_lst2 = ('2023', '08', '09')
sort_order = 'PRICE_HIGH_TO_LOW'

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


url = f'https://www.hotels.com/Hotel-Search?' \
      f'adults={payload["rooms"][0]["adults"]}' \
      f'&children=' \
      f'&d1={payload["checkInDate"]["year"]}-{payload["checkInDate"]["month"]}-{payload["checkInDate"]["day"]}' \
      f'&d2={payload["checkOutDate"]["year"]}-{payload["checkOutDate"]["month"]}-{payload["checkOutDate"]["day"]}' \
      f'&latLong=' \
      f'&mapBounds=' \
      f'&pwaDialog=' \
      f'&regionId={payload["destination"]["regionId"]}' \
      f'&rooms=1' \
      f'&semdtl=' \
      f'&sort={sort_order}' \
      f'&sortTriggerPill=' \
      f'&theme=' \
      f'&useRewards=true' \
      f'&userIntent='

# print(payload)
# print('city_id=', payload['destination']['regionId'])
# print('checkInDate_day=', payload['checkInDate']['day'])
print(url)
