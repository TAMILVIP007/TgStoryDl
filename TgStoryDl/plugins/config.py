from os import getenv

from dotenv import load_dotenv


class Config:
    load_dotenv()
    API_ID = int(getenv("API_ID"))
    API_HASH = getenv("API_HASH")
    TOKEN = getenv("TOKEN")
    DEVS = list(map(int, getenv("DEVS").split(",")))
    STRING_SESSION = getenv("STRING_SESSION", None)
    DATABASE_URL = getenv("DATABASE_URL")


config = Config()
