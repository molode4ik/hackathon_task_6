from app import app
from flask import render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

n = 4  # pages в analogue и adjustments (кол-во аналагов, которые будут показываться), используется в jinja

@app.route('/', methods=["GET", "POST"])
@app.route('/auth', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        login_text = request.form['login_auth']
        pass_text = request.form['pass_auth']
        print(login_text)
        print(pass_text)
        # проверка пароля через бд
        return redirect(url_for('welcome'))
    else:
        return render_template('auth.html')


@app.route('/welcome', methods=["GET", "POST"])
def welcome():
        return render_template('welcome.html')


@app.route('/analogue', methods=["GET", "POST"])
def analogue():
        return render_template('analogue.html', pages=n)


@app.route('/adjustments', methods=["GET", "POST"])
def adjustments():
        return render_template('adjustments.html', pages=n)


@app.route('/registration', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        email_text_reg_page = request.form['email_reg_page']
        login_text_reg_page = request.form['login_reg_page']
        pass_text_reg_page = request.form['pass_reg_page']
        sec_pass_text_reg_page = request.form['sec_pass_reg_page']
        print(email_text_reg_page)
        print(login_text_reg_page)
        print("sosi")
        print(generate_password_hash(pass_text_reg_page))
        print(sec_pass_text_reg_page)
        # проверка на сущ. пользователя
        return redirect(url_for('index'))
    else:
        return render_template('registration.html')
