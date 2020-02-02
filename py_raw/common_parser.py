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
import datetime

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep


# чтение ymal-файла с настройками логирования, создание логгера
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)



def get_links_from_xlsx(price_dict, brand):
    """
    считываем из файла словарик, у которого ключ - id, значения - название и урлы
    """
    try:
        name = "./../urls/" + brand + "_urls.xlsx"
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
        logger.error('Error: no file with urls in "./../urls/"', brand)


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
                strbt_item_name = soup.find('h1', itemprop='name').text
                price_dict[id][0] = strbt_item_name

                strbt_item_price = soup.find('span', class_='price').text

                for char in strbt_item_price:  # чистим цену от всяких знаков, ибо нефиг
                    if char.isdigit():
                        clear_strbt_item_price += char
                
                price_dict[id][3] = int(clear_strbt_item_price)
            else:
                logger.error('Connection error in strbt url', price_dict[id][1])
        except Exception as catch_exception:
            # print(catch_exception)
            logger.error('Ошибка', catch_exception)


    # TODO разделить блоки парсинга стройбата и всех инструментов на две функции

    # блок парсинга всех инструментов, пока через селениум, т.к. подгрузка сайта идет через скрипт

    # # Открытие браузера и задание времени ожидания элемента на странице
    browser = webdriver.Chrome()
    browser.implicitly_wait(0.2)

    try:
        for key, value in price_dict.items():
            if price_dict[key][2] != 'nope':
                browser.get(price_dict[key][2])  # заходим на каждую ссылку в списке
                sleep(10)
                try:  # пытаемся найти элемент, если он по распродаже
                    browser.find_element_by_css_selector('span.price-value')
                    vse_instr_item_price = browser.find_element_by_css_selector('span.price-value').text
                except NoSuchElementException:
                    logger.error('Не нашел цены в 1: ')

                try:  # пытаемся найти элемент, если он не по распродаже
                    browser.find_element_by_css_selector('div.price > span.price-value')
                    vse_instr_item_price = browser.find_element_by_css_selector('div.price > span.price-value').text
                except NoSuchElementException:
                    logger.error('Не нашел цены в 2: ')

                # чсистим цену от пробелов
                vse_instr_item_price_clear = ''
                for char in vse_instr_item_price:
                    if char.isdigit():
                        vse_instr_item_price_clear += char

                price_dict[key][4] = int(vse_instr_item_price_clear)
                # print(vse_instr_item_price_clear)
            else:
                price_dict[key][4] = 0
        browser.close()
    except Exception as catch_exception:  # TODO правильно прописать эксепшены
        logger.error('Critical error', catch_exception)


def prices_analysis(price_dict, brand):
    """
    На вход словарик, где id - ключ, начение - список, в котором сначала название, потом ссылка стройбата, потом ссылка всех инструментов, потом цена стройбата, потом цена всех инструментов
    Формирует один файл экселя, где:
    на первом листе все значения из словаря, на втором те значения, где стройбатовская цена выше, на третьем листе те позиции, где все-инструментовская позиция выше
    """
    strb_price_more_then_vse_instrumenti = {}
    vse_instrumenti_price_more_then_strbt = {}

    for key, value in price_dict.items():
        if price_dict[key][3] > price_dict[key][4]:  # если стройбатовская цена больше, чем всех инструментов
            strb_price_more_then_vse_instrumenti[key] = price_dict[key]
        elif price_dict[key][3] < price_dict[key][4]:  # если стройбатовская меньше, чем всех инструментовская
            vse_instrumenti_price_more_then_strbt[key] = price_dict[key]
        else:  # на случай, если цены равны
            strb_price_more_then_vse_instrumenti[key] = price_dict[key]


    # запихиваем все в эксель:
    today = datetime.datetime.today()
    today_file_name = '../xlsx/' + brand + '_strbt_vseinstr_price_compare_' + today.strftime("%d.%m.%Y") + '.xlsx'
    print(today_file_name)
    price_dict_df = pd.DataFrame.from_dict(price_dict, orient='index')
    vse_instrumenti_price_more_then_strbt_df = pd.DataFrame.from_dict(vse_instrumenti_price_more_then_strbt, orient='index')
    strb_price_more_then_vse_instrumenti_df = pd.DataFrame.from_dict(strb_price_more_then_vse_instrumenti, orient='index')
    price_dict_df.reset_index(drop=False, inplace=True)
    vse_instrumenti_price_more_then_strbt_df.reset_index(drop=False, inplace=True)
    strb_price_more_then_vse_instrumenti_df.reset_index(drop=False, inplace=True)

    # демонстрация датафреймов
    # print(price_dict_df)
    # print(vse_instrumenti_price_more_then_strbt_df)
    # print(strb_price_more_then_vse_instrumenti_df)


    # price_compare = pd.read_excel(today_file_name)
    writer = pd.ExcelWriter(today_file_name, engine='xlsxwriter')
    price_dict_df.to_excel(writer, sheet_name='main', index=False)
    strb_price_more_then_vse_instrumenti_df.to_excel(writer, sheet_name='strbt > vse_instr', index=False)
    vse_instrumenti_price_more_then_strbt_df.to_excel(writer, sheet_name='vse_instr > strbt', index=False)




    ########  ########  ######   #######  ########
    ##     ## ##       ##    ## ##     ## ##     ##
    ##     ## ##       ##       ##     ## ##     ##
    ##     ## ######   ##       ##     ## ########
    ##     ## ##       ##       ##     ## ##   ##
    ##     ## ##       ##    ## ##     ## ##    ##
    ########  ########  ######   #######  ##     ##

    workbook = writer.book

    cell_format = workbook.add_format({
        'bold': True,
        'font_color': 'black',
        'align': 'center',
        'valign': 'center',
        'bg_color': '#ecf0f1'
    })

    for sheet in ['main', 'strbt > vse_instr', 'vse_instr > strbt']:

        worksheet = writer.sheets[sheet]
        worksheet.set_column('A:A', 7)
        worksheet.set_column('B:B', 60)
        worksheet.set_column('C:F', 10)
        worksheet.write('A1', 'код 1С', cell_format)
        worksheet.write('B1', 'название', cell_format)
        worksheet.write('C1', 'стрбт', cell_format)
        worksheet.write('D1', 'все_инстр', cell_format)
        worksheet.write('E1', 'стрбт', cell_format)
        worksheet.write('F1', 'все_инстр', cell_format)

        worksheet.freeze_panes(1, 0)

    writer.save()



##     ##    ###    #### ##    ##
###   ###   ## ##    ##  ###   ##
#### ####  ##   ##   ##  ####  ##
## ### ## ##     ##  ##  ## ## ##
##     ## #########  ##  ##  ####
##     ## ##     ##  ##  ##   ###
##     ## ##     ## #### ##    ##

if __name__ == "__main__":
    price_dict = {}
    list_of_brands = ['bosch', 'makita']
    for brand in list_of_brands:
        get_links_from_xlsx(price_dict, brand)
        get_prices_from_sites(price_dict)
        prices_analysis(price_dict, brand)
    pass
