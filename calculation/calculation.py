from utm import from_latlon
import math
from config.config import Yandex
from avito_parser.models import Advertisement
from datetime import datetime
import re


FLOOR_PERCENTS_LIST = [[0.0, 7.5, 3.2], [-7.0, 0, -4], [-3.1, 4.2, 0]]
FLOORS_LIST = [["первый этаж"], ["средние этажи"], ["последний этаж"]]

HOME_PERCENTS_LIST = [[0, -6, -12, None, None, None], [6, 0, -7, -12, None, None], [14, 7, 0, -6, -11, None],
                      [None, 14, 6, 0, -6, -8], [None, None, 13, 6, 0, -3], [None, None, None, 9, 3, 0]]
HOME_SQUARES_LIST = [[i for i in range(30)], [i for i in range(30, 50)], [i for i in range(50, 65)],
                     [i for i in range(50, 65)], [i for i in range(65, 90)], [i for i in range(90, 120)],
                     [i for i in range(120, 300)]]

KITCHEN_PERCENTS_LIST = [[0, 3, 9], [-2.9, 0, 5.8], [-8.3, -5.5, 0]]
KITCHEN_SQUARES_LIST = [[i for i in range(7)], [i for i in range(7, 10)], [i for i in range(10, 15)]]

BALCONY_PERCENTS_LIST = [[0, 5.3], [-5, 0]]
BALCONY_LIST = [['нет'], ['да']]

METRO_PERCENTS_LIST = [[0, -7, -11, None, None, None], [7, 0, -4, -8, None, None], [12, 4, 0, -5, -10, None],
                       [None, 9, 5, 0, -6, -9], [None, None, 11, 6, 0, -4], [None, None, None, 10, 4, 0]]
METRO_DISTANCES_LIST = [[i for i in range(5)], [i for i in range(5, 10)], [i for i in range(10, 15)],
                        [i for i in range(15, 30)], [i for i in range(30, 60)], [i for i in range(60, 90)]]

DECORATION_PERCENTS_LIST = [[0, 13400, 20100],
                            [-13400, 0, 6700], [-20100, -6700, 0]]
DECORATION_STATES_LIST = [['без отделки'], ['муниципальынй ремонт'], ['современная отделка']]


def get_geocode(address: str):
    coordinates = Yandex.client.coordinates(address)
    return float(coordinates[1]), float(coordinates[0])


def get_distance(point: tuple, radius: int):
    lng_min = point[1] - radius / abs(math.cos(math.radians(point[0])) * 111.0)
    lng_max = point[1] + radius / abs(math.cos(math.radians(point[0])) * 111.0)
    lat_min = point[0] - (radius / 111.0)
    lat_max = point[0] + (radius / 111.0)
    return (lat_min, lat_max), (lng_min, lng_max)


class Analog:    
    def __init__(self, location: str, rooms: int, segment: str, home_area: float, kitchen_area: float, metro_time: int,
                 floor: int,
                 floor_total: int, balcony: str, material: str, repairs: str):
        self.location = location
        self.rooms = rooms
        self.segment = segment.lower()
        self.home_area = home_area
        self.kitchen_area = kitchen_area
        self.metro_time = metro_time
        self.floor = floor
        self.floor_total = floor_total
        self.balcony = balcony.lower()
        self.material = material.lower()
        self.repairs = repairs.lower()

    def find_analog(self):
        lat_range, lng_range = get_distance(get_geocode(self.location), radius=1)
        # TODO: балкон, время до метро
        return Advertisement.select().where(
            (Advertisement.coords_lat.between(lat_range[0], lat_range[1]) & Advertisement.coords_lng.between(
                lng_range[0], lng_range[1])) &
            (self.rooms == Advertisement.get().number_rooms) &
            (Advertisement.floor_total.between(self.floor_total - 4, self.floor_total + 4)) &
            (self.material in Advertisement.get().house_type) &
            (self.segment in Advertisement.get().segment) &
            (Advertisement.floor.between(self.floor - 4, self.floor + 4)) &
            (Advertisement.total_area.between(self.home_area - 20, self.home_area + 20)) &
            (Advertisement.kitchen_area.between(self.kitchen_area - 5, self.kitchen_area + 5)) &
            #('лоджия/балкон' if not Advertisement.balcony is None else 'нет') &
            #(Advertisement.nearest_metro_time.between(self.metro_time - 5, self.metro_time + 5)) &
            (self.repairs in Advertisement.get().repairs)
        ).execute()

    def search_floor_lvl(floor:int, total_floor: int) -> str:
        if floor == 1: 
            return 'первый этаж'
        elif  1 < floor < total_floor:
            return 'средние этажи'
        elif floor == total_floor:
            return 'последний этаж'

    def search_balcony(balcony: str):
        if len(re.findall(r'балкон|лоджия|есть|да', balcony.lower())) > 0 :
            return 'да'
        return 'нет'

    def search_repair(repair: str) -> str:
        if len(re.findall(r'современ'), repair.lower()) >0:
            return 'современная отделка'
        elif len(re.findall(r'муницип'), repair.lower()) >0:
            return 'муниципальный ремонт'
        elif len(re.findall(r'без'), repair.lower()) >0:
            return 'без отделки'

    def search_gap(self, input_square: int, squares_list: list):
        for gap, squares in enumerate(squares_list):
            for square in squares:
                if square == input_square:
                    return gap
    
    def search_floor_percent(self, floor: int, total_floor: int):
        gap = self.search_gap(self.search_floor_lvl(floor, total_floor), FLOORS_LIST)
        analog_gap = self.search_gap(self.search_floor_lvl(self.floor, self.total_floor), FLOORS_LIST)
        return FLOOR_PERCENTS_LIST[analog_gap][gap]
    
    def searh_home_square_percent(self, home_area: int):
        gap = self.search_gap(home_area, HOME_SQUARES_LIST)
        analog_gap = self.search_gap(self.home_area, HOME_SQUARES_LIST)
        return HOME_PERCENTS_LIST[analog_gap][gap]  # return percent
    
    def search_kitchen_square_percent(self, kitchen_area: int):
        gap = self.search_gap(kitchen_area, KITCHEN_SQUARES_LIST)
        analog_gap = self.search_gap(self.kitchen_area, KITCHEN_SQUARES_LIST)
        return KITCHEN_PERCENTS_LIST[analog_gap][gap]
    
    def search_balcony_percent(self, balcony: str):
        gap = self.search_gap(self.search_balcony(balcony), BALCONY_LIST)
        analog_gap = self.search_gap(self.search_balcony(self.balcony), BALCONY_LIST)
        return BALCONY_PERCENTS_LIST[analog_gap][gap]
    
    def search_metro_distance_percent(self, metro_time: int):
        gap = self.search_gap(metro_time, METRO_DISTANCES_LIST)
        analog_gap = self.search_gap(self.metro_time, METRO_DISTANCES_LIST)
        return METRO_PERCENTS_LIST[analog_gap][gap]
    
    def search_decoration_state_percent(self, repairs: str):
        gap = self.search_gap(self.search_repair(repairs), DECORATION_STATES_LIST)
        analog_gap = self.search_gap(self.search_repair(self.repairs), DECORATION_STATES_LIST)
        return DECORATION_PERCENTS_LIST[analog_gap][gap]


def main():
    # TODO: Тут явно нужно что-то поменять
    ...
    # a = Analog('Средние этажи', 25, 6, 'Нет', 5, 'Без отделки')
    # print(a.search_floor_percent('Первый этаж'))
    # print(search_floor_percent(
    #     input_square='Первый этаж', analog_square='Средние этажи'))
    # print(searh_home_square_percent(input_square=25, analog_square=44))
    # print(search_kitchen_square_percent(input_square=6, analog_square=8))
    # print(search_balcony_percent(input_square='Нет', analog_square='Есть'))
    # print(search_distance_metro_percent(input_square=5, analog_square=8))
    # print(search_decoration_state_percent(
    #     input_square='Без отделки', analog_square='Эконом'))


# reference_data = {
#     'location': 'г. Москва, ул. Островитянова, 41к1',
#     'rooms': 1,
#     'home_square': 33.0,
#     'kitchen_square': 5.0,
#     'metro_distance': 1,
#     'amount_floor': 9,
#     'balcony': 'Нет',
#     'material': 'монолит',
#     'floor': 8,
#     'state': 'муниципальный ремонт'
# }
#
# analogs = Analog(location=reference_data['location'], rooms=reference_data['rooms'], segment="новостройки",
#                  home_area=reference_data['home_square'],
#                  kitchen_area=reference_data['kitchen_square'], metro_time=reference_data['metro_distance'],
#                  floor_total=reference_data['amount_floor'], balcony=reference_data['balcony'],
#                  material=reference_data['material'], floor=reference_data['floor'],
#                  repairs=reference_data['state']).find_analog()
