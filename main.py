from app import app
from config.config import Flask, Avito
from avito_parser.avito_parser import AvitoParser
from avito_parser.models import db, Advertisement, Users
import threading
import sqlite3
import os

def main():
    db.connect()
    # TODO: Авито убирать или нет?
    db.create_tables([Advertisement])
    db.create_tables([Users])
    threading.Thread(target=AvitoParser.run_parser, args=(Avito.url,)).start()
    app.run(host=Flask.host, port=Flask.port, debug=True)


if __name__ == "__main__":
    main()
