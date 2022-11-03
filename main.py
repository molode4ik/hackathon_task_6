from app import app
from config.config import Flask, Avito
from avito_parser.avito_parser import AvitoParser
from avito_parser.models import db, Advertisement
import threading


def main():
    db.connect()
    # TODO: Авито убирать или нет?
    db.create_tables([Advertisement])
    threading.Thread(target=AvitoParser.run_parser, args=(Avito.url,)).start()
    app.run(host=Flask.host, port=Flask.port, debug=Flask.debug)


if __name__ == "__main__":
    main()
