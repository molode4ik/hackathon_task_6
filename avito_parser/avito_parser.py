import datetime
import json
import urllib.parse
from selenium.webdriver.common.by import By
from .models import Advertisement
from calculation.calculation import get_geocode
import peewee
import os
import re

import logging
import time
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Parser:
    """Открывает браузер (хром) заходит на сайт"""

    def __init__(self, url, login=None, password=None, timeout=4):
        self.url = url
        self.login = login
        self.password = password
        self.timeout = timeout
        try:
            caps = DesiredCapabilities().CHROME
            # caps["pageLoadStrategy"] = "normal"  # complete
            caps["pageLoadStrategy"] = "eager"  # interactive
            # caps["pageLoadStrategy"] = "none"
            option = ChromeOptions()
            # option.add_experimental_option('dom.webdriver.enabled', False)
            option.add_argument("--disable-blink-features=AutomationControlled")
            option.add_argument('--log-level=50')
            option.add_argument("--start-maximized")
            option.headless = True
            option.add_experimental_option('prefs', {
                # "download.default_directory": "C:/Users/517/Download", #Change default directory for downloads
                # "download.prompt_for_download": False, #To auto download the file
                # "download.directory_upgrade": True,
                "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
            })
            self.driver = Chrome(service=Service(ChromeDriverManager().install()),
                                 options=option,
                                 desired_capabilities=caps)
            logging.info(f'Браузер открыт')
        except:
            logging.error('Ошибка браузера!!! Веб драйвер не работает')
            raise Exception()
        try:
            self.driver.get(self.url)
            logging.info(f'Открываю страницу: {self.url}')
            time.sleep(self.timeout)
        except:
            logging.error('Ошибка браузера!!! Не удалось открыть сайт')
            raise Exception()

    def __del__(self):
        self.driver.close()
        # self.driver.quit()
        logging.info(f'Браузер закрыт')

    def get_html_elm(self, elm):
        return elm.get_attribute("outerHTML")

    def get_page_source(self):
        return self.driver.page_source

    def open_new_page(self, url: str):
        logging.info(f'Открываю страницу: {url}')
        self.driver.get(url)
        time.sleep(self.timeout)


class AvitoParser(Parser):
    """Парсер авито. Получение информации со страниц поисковой выдаче"""

    def _get_data(self):
        script = self.driver.find_element(By.XPATH,
                                          '//script[contains(text(), "window.__initialData__")]').get_attribute(
            "outerHTML")
        script = script.split('"')[1]
        if script:
            script = urllib.parse.unquote(script)
            script = json.loads(script)
            for elm in script.keys():
                if '@avito/bx-single-page' in elm:
                    data = script[elm]['data']
                    return data

    def _get_more_data(self, url):
        result = {}
        try:
            self.open_new_page(url)
            script = self.driver.find_element(By.XPATH,
                                              '//script[contains(text(), "window.__initialData__")]').get_attribute(
                "outerHTML")
            script = script.split('"')[1]
            if script:
                script = urllib.parse.unquote(script)
                script = json.loads(script)
                for elm in script.keys():
                    if '@avito/bx-item-view' in elm:
                        house_data = script[elm]['buyerItem']['item']['houseParams']['data'][
                            'items']
                        flat_data = script[elm]['buyerItem']['paramsBlock'][
                            'items']
                        metro_data = script[elm]['buyerItem']['item']['geo']['references']
                        for item in house_data:
                            if item['title'] == "Тип дома":
                                result.update({'house_type': item['description']})
                            elif item['title'] == "Год постройки":
                                result.update({'construction_year': int(item['description'])})
                            elif item['title'] == "Пассажирский лифт":
                                result.update({'passenger_elevator': int(item['description'])})
                            elif item['title'] == "Грузовой лифт":
                                result.update(
                                    {'cargo_elevator': int(item['description']) if item[
                                                                                       'description'] != 'нет' else None})
                            elif item['title'] == "Двор":
                                result.update({'courtyard': item['description']})
                            elif item['title'] == "Парковка":
                                result.update({'parking': item['description']})
                            elif item['title'] == "Срок сдачи":
                                result.update({'deadline': item['description']})
                        for item in flat_data:
                            if item['title'] == "Количество комнат":
                                result.update(
                                    {'number_rooms': int(item['description']) if item[
                                                                                     'description'] != 'студия' else 1})
                            elif item['title'] == "Общая площадь":
                                result.update({'total_area': float(re.findall(r'\d+', item['description'])[0])})
                            elif item['title'] == "Площадь кухни":
                                result.update({'kitchen_area': float(re.findall(r'\d+', item['description'])[0])})
                            elif item['title'] == "Жилая площадь":
                                result.update({'living_area': float(re.findall(r'\d+', item['description'])[0])})
                            elif item['title'] == "Этаж":
                                floor_info = item['description'].split(" из ")
                                result.update({'floor': floor_info[0]})
                                result.update({'floor_total': floor_info[1]})
                            elif item['title'] == "Балкон или лоджия":
                                result.update({'balcony': item['description']})
                            elif item['title'] == "Санузел":
                                result.update({'bathroom': item['description']})
                            elif item['title'] == "Окна":
                                result.update({'windows': item['description']})
                            elif item['title'] == "Ремонт":
                                if item['description'] in ['евро', 'косметический', 'дизайнерский']:
                                    result.update({'repairs': 'современный ремонт'})
                                elif item['description'] in ['требует ремонта']:
                                    result.update({'repairs': 'муниципальный ремонт'})
                            elif item['title'] == "Высота потолков":
                                result.update({'ceiling_height': float(re.findall(r'\d+', item['description'])[0])})
                            elif item['title'] == "Отделка":
                                result.update({'repairs': item['description']})
                            elif item['title'] == "Способ продажи":
                                result.update({'selling_method': item['description']})
                            elif item['title'] == "Вид сделки":
                                result.update({'transaction_type': item['description']})
                        if metro_data:
                            print(metro_data[0]['content'])
                            result.update({'metro_info': metro_data})
                            result.update({'nearest_metro_station': metro_data[0]['content']})
                            result.update({'nearest_metro_time': int(re.findall(r'\d+',
                                                                                metro_data[0]['afterWithIcon'][
                                                                                    'text'][0])[0])})
                            return result

        except Exception:
            logging.error('Ошибка!!! Жду 30 секунд')
            time.sleep(30)
            return result

    def get_pages(self):
        data = self._get_data()
        count = data['count']
        logging.info(f'Найдено {count} объявлений')
        pages = []
        for page in data['catalog']['pager']['pages'].values():
            pages.append('https://www.avito.ru' + page)
        return pages

    def get_advertisements(self):
        data = self._get_data()
        for item in data['catalog']['items']:
            if item.get('id'):
                geoReferences = []
                for geo in item['geo']['geoReferences']:
                    after = geo.get('after')
                    if after is None:
                        after = ''
                    else:
                        after = after.replace(' ', ' ')
                    geoReferences.append({'content': geo['content'], 'after': after})
                try:
                    parameters = str(item['iva']['AutoParamsStep'][0]['payload'][
                                         'text'])  # возможно стоит убрать 0 если много параметров
                except:
                    parameters = None

                try:
                    vendor = str(item['iva']['SecondLineStep'][0]['payload']['value'])
                except:
                    vendor = None

                try:
                    lat, lng = get_geocode(item['location']['name'], item['geo']['formattedAddress'])
                except:
                    logging.error('Ошибка!!! Жду 30 секунд')
                    time.sleep(30)
                advertisements = {
                    'id_avito': item['id'],
                    'url': 'https://www.avito.ru' + item['urlPath'],
                    'name': item['title'].replace(' ', ' '),
                    'description': item['description'].replace(' ', ' ').replace('\n', ' '),
                    'category': item['category']['name'],
                    'location': item['location']['name'],
                    'time': datetime.datetime.fromtimestamp(item['sortTimeStamp'] // 1000),
                    'price': item['priceDetailed']['value'],
                    'images': [image['636x476'] for image in item['images']],
                    'address': item['geo']['formattedAddress'],
                    'geoReferences': geoReferences,
                    'phone': item['contacts']['phone'],
                    'delivery': item['contacts']['delivery'],
                    'message': item['contacts']['message'],
                    'parameters': parameters,
                    'coords_lat': lat,
                    'coords_lng': lng,
                    'vendor': vendor,
                }
                yield advertisements

    @staticmethod
    def __log():
        """Логирование скрипта в консоль и файл"""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        handler = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/avito_parser.log', 'a', 'utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        handler.setLevel(logging.INFO)
        root_logger.addHandler(handler)
        logging.getLogger("selenium").setLevel(logging.ERROR)
        logging.getLogger("webdriver_manager").setLevel(logging.ERROR)

    @staticmethod
    def run_parser(url: str):
        while True:
            AvitoParser.__log()
            parser = AvitoParser(url)
            pages = parser.get_pages()
            i = 1
            for url_page in pages:
                if url_page != url:
                    parser.open_new_page(url_page)
                advertisements = parser.get_advertisements()
                for advertisement in advertisements:
                    try:
                        advertisements_info = parser._get_more_data(advertisement["url"])
                        print(advertisements_info)
                        if advertisements_info:
                            Advertisement.create(**advertisement)
                            elm = Advertisement.get(Advertisement.id_avito == advertisement['id_avito'])
                            elm.house_type = advertisements_info.get('house_type')
                            elm.construction_year = advertisements_info.get('construction_year')
                            elm.passenger_elevator = advertisements_info.get('passenger_elevator')
                            elm.cargo_elevator = advertisements_info.get('cargo_elevator')
                            elm.courtyard = advertisements_info.get('courtyard')
                            elm.parking = advertisements_info.get('parking')
                            elm.deadline = advertisements_info.get('deadline')
                            elm.number_rooms = advertisements_info.get('number_rooms')
                            elm.total_area = advertisements_info.get('total_area')
                            elm.kitchen_area = advertisements_info.get('kitchen_area')
                            elm.living_area = advertisements_info.get('living_area')
                            elm.floor = advertisements_info.get('floor')
                            elm.floor_total = advertisements_info.get('floor_total')
                            elm.balcony = advertisements_info.get('balcony')
                            elm.bathroom = advertisements_info.get('bathroom')
                            elm.windows = advertisements_info.get('windows')
                            elm.repairs = advertisements_info.get('repairs')
                            elm.ceiling_height = advertisements_info.get('ceiling_height')
                            elm.selling_method = advertisements_info.get('selling_method')
                            elm.transaction_type = advertisements_info.get('transaction_type')
                            elm.metro_info = advertisements_info.get('metro_info')
                            elm.nearest_metro_station = advertisements_info.get('nearest_metro_station')
                            elm.nearest_metro_time = advertisements_info.get('nearest_metro_time')
                            elm.vendor = advertisements_info.get('vendor')
                            elm.save()
                            logging.info(
                                f'Добавлено новое объявление {advertisement["url"]} с ценой {advertisement["price"]}')
                    except peewee.IntegrityError:
                        elm = Advertisement.get(Advertisement.id_avito == advertisement['id_avito'])
                        if advertisement['price'] != elm.price:
                            price_difference = elm.price - advertisement['price']
                            elm.price = advertisement['price']
                            if price_difference > 0:
                                logging.info(f'Снижение цены для {advertisement["url"]} на {price_difference}')
                        elm.date_update = datetime.datetime.now()
                        if not elm.activated:
                            elm.activated = True
                            logging.info(f'Объявление {elm.url} активировано')
                        elm.save()
                logging.info(f'Просмотрено {i} страниц из {len(pages)}')
                i += 1
            date_update = datetime.datetime.now() - datetime.timedelta(days=1)
            deactivation_list = Advertisement.select().where(
                (Advertisement.date_update < date_update) & (Advertisement.activated is True))
            for elm in deactivation_list:
                logging.info(f'Объявление {elm.url} снято')
                elm.activated = False
                elm.save()
            time.sleep(3600)
