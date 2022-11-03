import datetime
import logging
import peewee
from models import db, Advertisement
from avito_parser import Avito_parser


def log():
    """Логирование скрипта в консоль и файл"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.FileHandler('avito_parser.log', 'a', 'utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    handler.setLevel(logging.INFO)
    root_logger.addHandler(handler)
    logging.getLogger("selenium").setLevel(logging.ERROR)
    logging.getLogger("webdriver_manager").setLevel(logging.ERROR)


def main():
    log()
    url = "https://www.avito.ru/moskva/kvartiry/prodam-ASgBAgICAUSSA8YQ"
    db.connect()
    db.create_tables([Advertisement])
    parser = Avito_parser(url)
    pages = parser.get_pages()
    i = 1
    for url_page in pages:
        if url_page != url:
            parser.open_new_page(url_page)
        advertisements = parser.get_advertisements()
        for advertisement in advertisements:
            try:
                Advertisement.create(**advertisement)
                advertisements_info = parser.get_more_data(advertisement["url"])
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
                elm.balcony = advertisements_info.get('balcony')
                elm.bathroom = advertisements_info.get('bathroom')
                elm.windows = advertisements_info.get('windows')
                elm.repairs = advertisements_info.get('repairs')
                elm.ceiling_height = advertisements_info.get('ceiling_height')
                elm.facing = advertisements_info.get('facing')
                elm.selling_method = advertisements_info.get('selling_method')
                elm.transaction_type = advertisements_info.get('transaction_type')
                elm.metro = advertisements_info.get('metro')
                elm.vendor = advertisements_info.get('vendor')
                elm.save()
                logging.info(f'Добавлено новое объявление {advertisement["url"]} с ценой {advertisement["price"]}')
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
        (Advertisement.date_update < date_update) & (Advertisement.activated == True))
    for elm in deactivation_list:
        logging.info(f'Объявление {elm.url} снято')
        elm.activated = False
        elm.save()
    db.close()


if __name__ == '__main__':
    main()
