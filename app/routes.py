from app import app, login_manager
from app.forms import RegistrationForm, LoginForm
from flask import render_template, request, redirect, url_for, flash,g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, LoginManager, login_required, UserMixin, logout_user
from avito_parser.models import Users, db, Advertisement
from excel_parser.excel_parser import parse_excel
from config.config import Flask
import os
from werkzeug.utils import secure_filename
import openpyxl
from calculation.calculation import Analog
n = 4  # pages в analogue и adjustments (кол-во аналагов, которые будут показываться), используется в jinja

app.config['UPLOAD_FOLDER'] = Flask.upload_folder


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Flask.allowed_extensions


class UserLogin(UserMixin):
    def __init__(self, id, login, password):
        self.id = id
        self.login = login
        self.password = password

#
@login_manager.user_loader
def load_user(user):
    return UserLogin

#
@app.route('/', methods=["GET", "POST"])
def start():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    return redirect(url_for('index'))

#
@app.route('/auth', methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    # form1 = generate_password_hash(LoginForm().login)
    # form2 = generate_password_hash(LoginForm().password)
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # user = Users.get(login=form.login.data, password=form.password.data)
            # print(LoginForm().login.data)
            # print()
            for person in Users.select():
                # print(person.login)
                if check_password_hash(person.login, LoginForm().login.data) and check_password_hash(person.password,
                                                                                                     LoginForm().password.data):
                    user = Users.get(login=person.login, password=person.password)
                    user_auth = UserLogin(id=user.id_users, login=user.login, password=user.password)
                    login_user(user_auth)
                    return redirect(url_for('welcome'))
        except:
            return render_template('auth.html', form=form)
        flash('Неверный логин или пароль!')
    return render_template('auth.html', form=form)

#
@app.route('/welcome', methods=["GET", "POST"])
@login_required
def welcome():
    if request.method == 'POST':
        try:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                new_filename = f'{Flask.upload_folder}\\{file.filename}'
                save_location = os.path.join('input', new_filename)
                file.save(save_location)
                file_data = parse_excel(new_filename)[0]
                return render_template('welcome.html', allowed_extensions=",".join(Flask.allowed_extensions),
                                       file_data=file_data)

        except:
            return redirect(url_for('logout'))

        return render_template('welcome.html', allowed_extensions=",".join(Flask.allowed_extensions))

    return render_template('welcome.html', allowed_extensions=",".join(Flask.allowed_extensions))


#
@app.route('/analogue', methods=["GET", "POST"])
@login_required
def analogue():
    if request.method == 'POST':
        global dict_charters
        dict_charters = dict()
        dict_charters['Местоположение'] = request.form['place']
        dict_charters['Количество комнат'] = request.form['rooms_num']
        dict_charters['Сегмент (Новостройка, современное жилье, старый жилой фонд)'] = request.form['type_house']
        dict_charters['Этажность дома'] = request.form['level_house']
        dict_charters['Материал стен (Кипич, панель, монолит)'] = request.form['material_house']
        dict_charters['Этаж расположения'] = request.form['level_room']
        dict_charters['Площадь квартиры, кв.м'] = request.form['area_room']
        dict_charters['Площадь кухни, кв.м'] = request.form['area_kitchen']
        dict_charters['Наличие балкона/лоджии'] = request.form['balcony']
        dict_charters['Удаленность от станции метро, мин. пешком'] = request.form['metro_time']
        dict_charters['Состояние (без отделки, муниципальный ремонт, с современная отделка)'] = request.form[
            'renovation']

        class_list = Analog(location=dict_charters['Местоположение'], rooms=int(dict_charters['Количество комнат']),
                            segment=dict_charters['Сегмент (Новостройка, современное жилье, старый жилой фонд)'],
                            home_area=int(dict_charters['Площадь квартиры, кв.м']),
                            kitchen_area=int(dict_charters['Площадь кухни, кв.м']),
                            metro_time=int(dict_charters['Удаленность от станции метро, мин. пешком']),
                            floor_total=int(dict_charters['Этажность дома']),
                            balcony=dict_charters['Наличие балкона/лоджии'],
                            material=dict_charters['Материал стен (Кипич, панель, монолит)'],
                            floor=int(dict_charters['Этаж расположения']),
                            repairs=dict_charters[
                                'Состояние (без отделки, муниципальный ремонт, с современная отделка)']).find_analog()

        class_list_id = " ".join([str(i.id) for i in class_list])

        return render_template('welcome.html', allowed_extensions=",".join(Flask.allowed_extensions),
                               file_data=dict_charters, list_class=class_list, list_id=class_list_id)
    return render_template('welcome.html', allowed_extensions=",".join(Flask.allowed_extensions))

#
@app.route('/adjustments/<list_id>', methods=["GET", "POST"])
@login_required
def adjustments(list_id):
    str1 = list_id.split()
    analogs_dict = dict()
    global dict_charters
    list_price = list()
    for item_id,i in enumerate(str1):
        analog_value = Advertisement.get(id=int(i))
        analog = Analog(analog_value.location, analog_value.number_rooms, analog_value.segment,
                        analog_value.total_area, analog_value.kitchen_area, analog_value.nearest_metro_time,
                        analog_value.floor, analog_value.floor_total, analog_value.balcony,
                        analog_value.house_type, analog_value.repairs)

        floor = analog.search_floor_percent(int(dict_charters['Этаж расположения']),int(dict_charters['Этажность дома']))
        balcony = analog.search_balcony_percent(dict_charters['Наличие балкона/лоджии'])
        kitchen = analog.search_kitchen_square_percent(float(dict_charters['Площадь кухни, кв.м']))
        repairs = analog.search_decoration_state_percent(dict_charters['Состояние (без отделки, муниципальный ремонт, с современная отделка)'])
        metro = analog.search_metro_distance_percent(int(dict_charters['Удаленность от станции метро, мин. пешком']))
        area = analog.searh_home_square_percent(float(dict_charters['Площадь квартиры, кв.м']))
        if metro == None:
            metro = 0
        analogs_dict.update({
            item_id: [-4.5, area, metro, floor, kitchen, balcony, repairs]
            })
        list_price.append(round(analog_value.price/analog_value.total_area,3)) # цена на кв.м
    
    prices = []  # Массив цен
    sizes = []  # Размер примерных корректировок
    for key, price in zip(analogs_dict.keys(), list_price):
        start_price = price
        sizes.append(sum(map(abs, analogs_dict[key])))
        for item_id, item in enumerate(analogs_dict[key]):
            if item_id == 6:
                if item > 0:
                    analogs_dict[key].append(start_price/item)
                    start_price = start_price + start_price/item
                else:
                    analogs_dict[key].append(item)
                    start_price = start_price + (start_price * item/100)
            else:
                start_price = start_price + (start_price * item/100)
        prices.append(start_price)
    weights = []  # Вес аналога
    for size in sizes:
        weights.append(round((1/size)/sum([1/i for i in sizes]), 2))
    
    etalon_price_per_m = 0  # Рыночная стоимость, руб./кв.м. (с НДС)
    for price, weight in zip(prices,weights):
        etalon_price_per_m += int((etalon_price_per_m + price) * weight)

    # Рыночная стоимость, руб. (с НДС)
    etalon_price = int(etalon_price_per_m * float(dict_charters['Площадь квартиры, кв.м']))

    max_min = round((max(prices)/min(prices)) * 100 - 100, 2)  # Разница между max и min значением

    return render_template('adjustments.html', data=list_id, analogs_dict=analogs_dict,
                           etalon_price_per_m=etalon_price_per_m, etalon_price=etalon_price,
                           weights=weights, sizes=sizes, max_min=max_min)


@app.route('/registration', methods=["GET", "POST"])
def registration():
    form_reg = RegistrationForm()
    if form_reg.validate_on_submit():

        login_reg = form_reg.username.data
        password_reg = form_reg.password.data
        Users.create(login=generate_password_hash(login_reg), password=generate_password_hash(password_reg))

        return redirect(url_for('index'))
    return render_template('registration.html', form=form_reg)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
