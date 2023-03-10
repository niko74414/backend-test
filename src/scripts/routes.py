from flask import Blueprint

from src.scripts.BackEndTest.routes import back_end_test_blueprint

base_blueprint = Blueprint("base_blueprint", __name__)

from .logs import add_logs

base_blueprint.register_blueprint(back_end_test_blueprint)


## * Register logs
add_logs()