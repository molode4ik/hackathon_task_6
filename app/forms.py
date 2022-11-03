from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from avito_parser.models import Users

class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(),
        Length(min=5, max=20, message='Логин должен содержать не менее 5 и не более 20 символов!') ])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать!')])
    submit = SubmitField('Регистрация')

class LoginForm(FlaskForm):
    login = StringField('Логин', validators = [DataRequired()])
    password = PasswordField('Пароль', validators = [DataRequired()])
    submit = SubmitField('Войти')