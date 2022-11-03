from dataclasses import dataclass
from environs import Env

env = Env()
env.read_env()


@dataclass
class Flask:
    host: str = env.str("HOST")
    port: str = env.str("PORT")
    debug: bool = env.bool("DEBUG")


@dataclass
class Avito:
    url: str = env.str("AVITO_URL")
