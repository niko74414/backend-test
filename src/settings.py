import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def isTrue(val: str = "") -> bool:
    if not val:
        return False
    
    valComp = val.lower()
    if valComp[0] != "t" and valComp[0] != "1":
        return False

    return True

class Config(object):
    def __init__(self) -> None:
        self.DEVELOPMENT = isTrue(os.getenv("DEVELOPMENT"))
        self.DEBUG = isTrue(os.getenv("DEBUG"))
        self.TESTING = isTrue(os.getenv("TESTING"))
        self.ENV = os.getenv("ENV").lower()
        # self.CSRF_ENABLED = True

configuration = Config()

application = Flask(__name__)
CORS(application)
application.config.from_object(configuration)
