"""
Получает из файла урлы стройбата и всех-инструментов.
Проходит Стройбат-сайт, кидает в файл цены товаров
Проходит Все-инструменты, кидает в файл цены товаров
Проходи файл с ценами, урлами, названиями, показывая у кого больше цена
"""

import pandas as pd
import requests
import logging.config
import yaml
from bs4 import BeautifulSoup as bs


# чтение ymal-файла с настройками логирования, создание логгера
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)



def get_links_from_xlsx(price_dict):
    """
    считываем из файла словарик, у которого ключ - id, значения - название и урлы
    """
    try:
        name = "./../urls/urls.xlsx"
        id_name_urls_dict = pd.read_excel(name, sheet_name='Sheet1')
        for i in range(len(id_name_urls_dict['id'])):
            id = str(id_name_urls_dict['id'][i])
            price_dict[id] = []  # в дикт суем пустой список, сейчас заполним
            price_dict[id].append(id_name_urls_dict['name'][i])
            price_dict[id].append(id_name_urls_dict['strbt_urls'][i])
            price_dict[id].append(id_name_urls_dict['vse_instrumenti_urls'][i])
            price_dict[id].append(0)  # нули эти это пустые пока цены
            price_dict[id].append(0)
    except FileNotFoundError:
        logger.error('Error: no file with urls in "./../urls/"')


def get_prices_from_sites(price_dict):
    headers = {
        'accpet': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    for id, value in price_dict.items():
        clear_strbt_item_price = ''
        clear_vse_instrumenti_item_price = ''
        session = requests.Session()

    # блок парсинга стройбата
        try:
            request = session.get(price_dict[id][1], headers=headers)
            if request.status_code == 200:
                soup = bs(request.content, 'html.parser')
                strbt_element_name = soup.find('h1', itemprop='name').text
                price_dict[id][0] = strbt_element_name
                strbt_element_price = soup.find('span', class_='price').text
                for char in strbt_element_price:  # чистим цену от всяких знаков, ибо нефиг
                    if char.isdigit():
                        clear_strbt_item_price += char
                price_dict[id][3] = clear_strbt_item_price
            else:
                logger.error('Connection error in strbt url', price_dict[id][1])
        except Exception as catch_exception:
            print(catch_exception)
            logger.error('Ошибка', catch_exception)

    # блок парсинга всех инструментов

        try:
            request = session.get(price_dict[id][2], headers=headers)
            if request.status_code == 200:
                soup = bs(request.content, 'html.parser')
                print('сюда дошли')
                vse_instrumenti_price = soup.find('span', class_='price-value')#.text
                print(vse_instrumenti_price)
            else:
                logger.error('Connection error in url:', price_dict[id][2])
        except Exception as catch_exception:
            print(catch_exception)
            logger.error('Ошибка:', catch_exception)




if __name__ == "__main__":
    price_dict = {}
    get_links_from_xlsx(price_dict)
    get_prices_from_sites(price_dict)
    for key, value in price_dict.items():
        print(key, value)
    pass
