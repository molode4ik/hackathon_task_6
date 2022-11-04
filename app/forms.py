from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(),
        Length(min=5, max=20, message='Логин должен содержать не менее 5 и не более 20 символов!') ],
                           render_kw={"placeholder": "Введите логин"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"placeholder": "Введите пароль"})
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать!')],
        render_kw={"placeholder": "Повторите пароль"})
    submit = SubmitField('Регистрация')

class LoginForm(FlaskForm):
    login = StringField('Логин', validators = [DataRequired()], render_kw={"placeholder": "Логин"})
    password = PasswordField('Пароль', validators = [DataRequired()], render_kw={"placeholder": "Пароль"})
    submit = SubmitField('Войти')