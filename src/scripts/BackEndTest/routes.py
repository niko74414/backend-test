import logging
from . import controllers
from flask import Blueprint, Response, request


################## Python loggers ##################
__logger = logging.getLogger(f"back_end_test_blueprint_logger")


back_end_test_blueprint = Blueprint(
    "back_end_test_blueprint",
    __name__,
    url_prefix='/api',
)

back_end_test_blueprint.add_url_rule(
    '/day-of-the-programmer',
    view_func=controllers.day_of_the_programmer,
    methods=["POST"]
)
back_end_test_blueprint.add_url_rule(
    '/bon-appetit',
    view_func=controllers.bon_appetit,
    methods=["POST"]
)
back_end_test_blueprint.add_url_rule(
    '/sock-merchant',
    view_func=controllers.sock_merchant,
    methods=["POST"]
)
back_end_test_blueprint.add_url_rule(
    '/drawing-book',
    view_func=controllers.drawing_book,
    methods=["POST"]
)
back_end_test_blueprint.before_request(
    lambda: __logger.info(f"{request.method} {request.full_path} {request.environ.get('SERVER_PROTOCOL', '')}")
)

def aft_req(res: Response):
    try:
        __logger.info(f"{res.status} {res.get_data()}")
    except:
        __logger.info(f"{res.status} {res.content_type}")
    return res
back_end_test_blueprint.after_request(aft_req)

back_end_test_blueprint.teardown_request(
    lambda err: __logger.error(f"End request {request.full_path} error: {err}") if err else __logger.info(f"End request {request.full_path}")
)
