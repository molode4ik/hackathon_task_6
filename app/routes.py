from app import app, login_manager
from app.forms import RegistrationForm, LoginForm
from flask import render_template, request, redirect, url_for, flash
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


@login_manager.user_loader
def load_user(user):
    return UserLogin


@app.route('/', methods=["GET", "POST"])
def start():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    return redirect(url_for('index'))


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
            place_welcome_to_xl = request.form['place']
            rooms_num_welcome_to_xl = request.form['rooms_num']
            type_house_welcome_to_xl = request.form['type_house']
            level_house_welcome_to_xl = request.form['level_house']
            material_house_welcome_to_xl = request.form['material_house']
            level_room_welcome_to_xl = request.form['level_room']
            area_room_welcome_to_xl = request.form['area_room']
            area_kitchen_welcome_to_xl = request.form['area_kitchen']
            balcony_welcome_to_xl = request.form['balcony']
            metro_time_welcome_to_xl = request.form['metro_time']
            renovation_welcome_to_xl = request.form['renovation']


            return render_template('welcome.html', allowed_extensions=",".join(Flask.allowed_extensions))

    return render_template('welcome.html', allowed_extensions=",".join(Flask.allowed_extensions))



@app.route('/analogue', methods=["GET", "POST"])
@login_required
def analogue():
    if request.method == 'POST':

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


        return render_template('welcome.html', allowed_extensions=",".join(Flask.allowed_extensions),
                               file_data=dict_charters, list_class=class_list)
    return render_template('welcome.html', allowed_extensions=",".join(Flask.allowed_extensions))


@app.route('/adjustments', methods=["GET", "POST"])
@login_required
def adjustments():
    return render_template('adjustments.html', pages=n)


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
