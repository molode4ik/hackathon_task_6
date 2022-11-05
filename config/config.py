from dataclasses import dataclass
from environs import Env
from yandex_geocoder import Client
import os

env = Env()
env.read_env()


@dataclass
class Flask:
    host: str = env.str("HOST")
    port: str = env.str("PORT")
    debug: bool = env.bool("DEBUG")
    upload_folder: str = os.getcwd() + env.str("UPLOAD_FOLDER")
    allowed_extensions = env.list("ALLOWED_EXTENSIONS", subcast=str)


@dataclass
class Avito:
    url: str = env.str("AVITO_URL")


@dataclass
class Yandex:
    api_key: str = env.str("YANDEX_API_KEY")
    client = Client(api_key)
