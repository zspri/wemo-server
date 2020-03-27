from dotenv import load_dotenv
from os import getenv

load_dotenv()
assert getenv('NET_SPACE') is not None

from wemo import app

if __name__ == '__main__':
    app.start()
