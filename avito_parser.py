import datetime
import json
import urllib.parse
from selenium.webdriver.common.by import By

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
                    with open('test1.json', 'w', encoding='utf-8') as f:
                        json.dump(script, f, ensure_ascii=False, indent=2)
                    return data

    def get_more_data(self, url):
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
                        # with open('asd.json', 'w', encoding='utf-8') as f:
                        #     f.write(json.dumps(metro_data, ensure_ascii=False))
                        for item in house_data:
                            if item['title'] == "Тип дома":
                                result.update({'house_type': item['description']})
                            elif item['title'] == "Год постройки":
                                result.update({'construction_year': int(item['description'])})
                            elif item['title'] == "Пассажирский лифт":
                                result.update({'passenger_elevator': int(item['description'])})
                            elif item['title'] == "Грузовой лифт":
                                result.update({'cargo_elevator': int(item['description'])})
                            elif item['title'] == "Двор":
                                result.update({'courtyard': item['description']})
                            elif item['title'] == "Парковка":
                                result.update({'parking': item['description']})
                            elif item['title'] == "Срок сдачи":
                                result.update({'deadline': item['description']})
                        for item in flat_data:
                            if item['title'] == "Количество комнат":
                                result.update({'number_rooms': int(item['description'])})
                            elif item['title'] == "Общая площадь":
                                result.update({'total_area': float(item['description'].replace('&nbsp;м²', ''))})
                            elif item['title'] == "Площадь кухни":
                                result.update({'kitchen_area': float(item['description'].replace('&nbsp;м²', ''))})
                            elif item['title'] == "Жилая площадь":
                                result.update({'living_area': float(item['description'].replace('&nbsp;м²', ''))})
                            elif item['title'] == "Этаж":
                                result.update({'floor': item['description'].replace(" из ", "/")})
                            elif item['title'] == "Балкон или лоджия":
                                result.update({'balcony': item['description']})
                            elif item['title'] == "Санузел":
                                result.update({'bathroom': item['description']})
                            elif item['title'] == "Окна":
                                result.update({'windows': item['description']})
                            elif item['title'] == "Ремонт":
                                result.update({'repairs': item['description']})
                            elif item['title'] == "Высота потолков":
                                result.update({'ceiling_height': float(item['description'].replace('&nbsp;м²', ''))})
                            elif item['title'] == "Отделка":
                                result.update({'facing': item['description']})
                            elif item['title'] == "Способ продажи":
                                result.update({'selling_method': item['description']})
                            elif item['title'] == "Вид сделки":
                                result.update({'transaction_type': item['description']})
                        if metro_data:
                            result.update({'metro': metro_data})
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
                    'coords_lat': item['coords']['lat'],
                    'coords_lng': item['coords']['lng'],
                    'vendor': vendor,
                }
                yield advertisements
