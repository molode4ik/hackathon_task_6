import datetime

import peewee
from peewee import SqliteDatabase, Model, TextField, DateTimeField, PrimaryKeyField, CharField, \
    IntegerField, BooleanField, TimestampField, FloatField

db = SqliteDatabase('parser.db')


class BaseModel(Model):
    class Meta:
        database = db


class Advertisement(BaseModel):
    id = PrimaryKeyField(primary_key=True)
    id_avito = IntegerField(unique=True)
    url = CharField()
    name = CharField()
    description = TextField()
    category = CharField()  # разделить
    location = CharField()  # разделить
    time = DateTimeField()
    price = IntegerField()  # разделить
    images = TextField()  # разделить
    address = CharField()
    phone = BooleanField()
    delivery = BooleanField()
    message = BooleanField()
    parameters = CharField(null=True, default=None)
    coords_lat = IntegerField()
    coords_lng = IntegerField()
    date_creation = DateTimeField(default=datetime.datetime.now)
    date_update = DateTimeField(default=datetime.datetime.now)
    activated = BooleanField(default=True)
    house_type = CharField(null=True, default=None, max_length=50)
    construction_year = IntegerField(null=True, default=None)
    passenger_elevator = IntegerField(null=True, default=None)
    cargo_elevator = IntegerField(null=True, default=None)
    courtyard = CharField(null=True, default=None, max_length=50)
    parking = CharField(null=True, default=None, max_length=50)
    deadline = CharField(null=True, default=None, max_length=50)
    number_rooms = IntegerField(null=True, default=None)
    total_area = FloatField(null=True, default=None)
    kitchen_area = FloatField(null=True, default=None)
    living_area = FloatField(null=True, default=None)
    floor = CharField(null=True, default=None, max_length=50)
    balcony = CharField(null=True, default=None, max_length=50)
    bathroom = CharField(null=True, default=None, max_length=50)
    windows = CharField(null=True, default=None, max_length=50)
    repairs = CharField(null=True, default=None, max_length=50)
    ceiling_height = FloatField(null=True, default=None)
    facing = CharField(null=True, default=None, max_length=50)
    selling_method = CharField(null=True, default=None, max_length=50)
    transaction_type = CharField(null=True, default=None, max_length=50)
    metro = TextField(null=True, default=None)
    vendor = CharField(null=True, default=None, max_length=50)

    class Meta:
        table_name = 'Advertisements'
        order_by = 'id'
