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
        name = "./../urls/urlsa.xlsx"
        id_name_urls_dict = pd.read_excel(name, sheet_name='Sheet1')
        for i in range(len(id_name_urls_dict['id'])):
            id = str(id_name_urls_dict['id'][i])
            price_dict[id] = []  # в дикт суем пустой список, сейчас заполним
            price_dict[id].append(id_name_urls_dict['name'][i])
            price_dict[id].append(id_name_urls_dict['strbt_urls'])
            price_dict[id].append(id_name_urls_dict['vse_instruments_urls'])
            price_dict[id].append(0)  # нули эти это пустые пока цены
            price_dict[id].append(0)
    except:
        logger.error(x)



if __name__ == "__main__":
    price_dict = {}
    x = 'some_shit_happened'
    pass
