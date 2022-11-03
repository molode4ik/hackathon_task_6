from app import app, login_manager
from app.forms import RegistrationForm, LoginForm
from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, LoginManager, login_required, UserMixin, logout_user
from avito_parser.models import Users, db

n = 4  # pages в analogue и adjustments (кол-во аналагов, которые будут показываться), используется в jinja

class User_n(UserMixin):
    def __init__(self, id, login, password):
        self.id = id
        self.login = login
        self.password = password

@login_manager.user_loader
def load_user(user):
    return User_n

@app.route('/', methods=["GET", "POST"])
def start():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    return redirect(url_for('index'))

@app.route('/auth', methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = Users.get(login=form.login.data, password=form.password.data)
        except:
            return render_template('auth.html', form=form)
        user_auth = User_n(id=user.id_users, login=user.login, password=user.password)
        login_user(user_auth)
        return redirect(url_for('welcome'))
    return render_template('auth.html', form=form)

@app.route('/welcome', methods=["GET", "POST"])
@login_required
def welcome():
    return render_template('welcome.html')


@app.route('/analogue', methods=["GET", "POST"])
@login_required
def analogue():
    return render_template('analogue.html', pages=n)


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
        Users.create(login=login_reg, password=password_reg)
        return redirect(url_for('index'))
    return render_template('registration.html', form=form_reg)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))