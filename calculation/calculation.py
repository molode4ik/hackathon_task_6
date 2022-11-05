from utm import from_latlon
from math import sqrt
from config.config import Yandex

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
BALCONY_LIST = [['нет'], ['есть']]

METRO_PERCENTS_LIST = [[0, -7, -11, None, None, None], [7, 0, -4, -8, None, None], [12, 4, 0, -5, -10, None],
                       [None, 9, 5, 0, -6, -9], [None, None, 11, 6, 0, -4], [None, None, None, 10, 4, 0]]
METRO_DISTANCES_LIST = [[i for i in range(5)], [i for i in range(5, 10)], [i for i in range(10, 15)],
                        [i for i in range(15, 30)], [i for i in range(30, 60)], [i for i in range(60, 90)]]

DECORATION_PERCENTS_LIST = [[0, 13400, 20100],
                            [-13400, 0, 6700], [-20100, -6700, 0]]
DECORATION_STATES_LIST = [['без отделки'], ['эконом'], ['улучшеный']]


def get_geocode(city: str, address: str):
    coordinates = Yandex.client.coordinates(f"{city} {address}")
    return float(coordinates[1]), float(coordinates[0])


def get_distance(point_a: tuple, point_b: tuple):
    utm_point_a = from_latlon(point_a[0], point_a[1])
    utm_point_b = from_latlon(point_b[0], point_b[1])
    return round(sqrt((utm_point_b[0] - utm_point_a[0]) ** 2 + (utm_point_b[1] - utm_point_a[1]) ** 2))


def replace_symbols(string: str, list_symbols: list):
    for ch in list_symbols:
        if ch in string:
            string = string.replace(ch, "")
    return string


class Analog:
    def __init__(self, floor: str, home_square: int, kitchen_square: int, balcony: str, metro_distance: float,
                 decoration_state: str):
        self.floor = floor.lower()
        self.home_square = home_square
        self.kitchen_square = kitchen_square
        self.balcony = balcony.lower()
        self.metro_distance = metro_distance
        self.decoration_state = decoration_state.lower()

    def search_gap(self, input_square: int, squares_list: list):
        for gap, squares in enumerate(squares_list):
            for square in squares:
                if square == input_square:
                    return gap

    def search_floor_percent(self, input_square: str):
        gap = self.search_gap(input_square.lower(), FLOORS_LIST)
        analog_gap = self.search_gap(self.floor, FLOORS_LIST)
        return FLOOR_PERCENTS_LIST[analog_gap][gap]

    def searh_home_square_percent(self, input_square: int):
        gap = self.search_gap(input_square, HOME_SQUARES_LIST)
        analog_gap = self.search_gap(self.home_square, HOME_SQUARES_LIST)
        return HOME_PERCENTS_LIST[analog_gap][gap]  # return percent

    def search_kitchen_square_percent(self, input_square: int):
        gap = self.search_gap(input_square, KITCHEN_SQUARES_LIST)
        analog_gap = self.search_gap(self.kitchen_square, KITCHEN_SQUARES_LIST)
        return KITCHEN_PERCENTS_LIST[analog_gap][gap]

    def search_balcony_percent(self, input_square: str):
        gap = self.search_gap(input_square, BALCONY_LIST)
        analog_gap = self.search_gap(self.balcony, BALCONY_LIST)
        return BALCONY_PERCENTS_LIST[analog_gap][gap]

    def search_metro_distance_percent(self, input_square: int):
        gap = self.search_gap(input_square, METRO_DISTANCES_LIST)
        analog_gap = self.search_gap(self.metro_distance, METRO_DISTANCES_LIST)
        return METRO_PERCENTS_LIST[analog_gap][gap]

    def search_decoration_state_percent(self, input_square: str):
        gap = self.search_gap(input_square, DECORATION_STATES_LIST)
        analog_gap = self.search_gap(self.decoration_state, DECORATION_STATES_LIST)
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


if __name__ == "__main__":
    main()
