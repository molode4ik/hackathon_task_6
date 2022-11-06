import datetime
import os
from peewee import SqliteDatabase, Model, TextField, DateTimeField, PrimaryKeyField, CharField, IntegerField, \
    BooleanField, FloatField

db = SqliteDatabase(os.path.dirname(os.path.realpath(__file__)) + '/avito_parser.db')


class BaseModel(Model):
    class Meta:
        database = db


class Advertisement(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    id_avito = IntegerField(unique=True)
    url = CharField()
    name = CharField()
    description = TextField()
    category = CharField()
    location = CharField()
    time = DateTimeField()
    price = IntegerField()
    images = TextField()
    address = CharField()
    phone = BooleanField()
    delivery = BooleanField()
    message = BooleanField()
    parameters = CharField(null=True, default=None)
    coords_lat = FloatField()
    coords_lng = FloatField()
    date_creation = DateTimeField(default=datetime.datetime.now)
    date_update = DateTimeField(default=datetime.datetime.now)
    activated = BooleanField(default=True)
    house_type = CharField(null=True, default=None, max_length=50)
    segment = CharField(null=True, default=None, max_length=50)
    passenger_elevator = IntegerField(null=True, default=None)
    cargo_elevator = IntegerField(null=True, default=None)
    courtyard = CharField(null=True, default=None, max_length=50)
    parking = CharField(null=True, default=None, max_length=50)
    number_rooms = IntegerField(null=True, default=None)
    total_area = FloatField(null=True, default=None)
    kitchen_area = FloatField(null=True, default=None)
    living_area = FloatField(null=True, default=None)
    floor = IntegerField(null=True, default=None)
    floor_total = IntegerField(null=True, default=None)
    balcony = CharField(null=True, default=None, max_length=50)
    bathroom = CharField(null=True, default=None, max_length=50)
    windows = CharField(null=True, default=None, max_length=50)
    repairs = CharField(null=True, default=None, max_length=50)
    ceiling_height = FloatField(null=True, default=None)
    selling_method = CharField(null=True, default=None, max_length=50)
    transaction_type = CharField(null=True, default=None, max_length=50)
    metro_info = TextField(null=True, default=None)
    nearest_metro_station = TextField(null=True, default=None)
    nearest_metro_time = IntegerField(null=True, default=None)
    vendor = CharField(null=True, default=None, max_length=50)

    class Meta:
        table_name = 'Advertisement'
        order_by = 'id'


class Users(BaseModel):
    id_users = IntegerField(primary_key=True)
    login = CharField()
    password = CharField()
    blacklist_avito = TextField(null=True, default=None)

    class Meta:
        table_name = 'Users'
        order_by = 'id'
