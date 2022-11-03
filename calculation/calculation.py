from constans import *


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
