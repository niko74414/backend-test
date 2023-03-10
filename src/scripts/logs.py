import os
import sys
import json
import logging
from datetime import datetime
from ..templates_lib.base_query import BaseQuery
from flask import Response, make_response, request, g
from .routes import base_blueprint
from pytz import timezone

from psycopg2 import Error as PGError

###### Logger entradas y salidas generales
io_logger = logging.getLogger("io_logger")


def before_app_request():
    reqPath = request.path
    methodReq = request.method
    if methodReq == "OPTIONS" or reqPath== "/":
        pass
    else:
        logs_table = os.getenv('LOGS_TABLE')
        logs_table_id = os.getenv('LOGS_TABLE_ID')
        log_body = {
            "time_start": datetime.now(timezone("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S"),
            "pk_log_type": "SERVICIO"
        }
        if request:
            if request.is_json:
                body = request.get_json()
            else:
                if len(request.form.keys()) > 0 or len(request.files.keys()) > 0:
                    body = {}
                    if len(request.form.keys()) > 0:
                        body['form'] = request.form.to_dict()
                    if len(request.files.keys()) > 0:
                        body['files'] = request.files.to_dict()
                        for key in body.get('files'):
                            body['files'][key] = body.get('files')[key].filename
                else:
                    body = request.get_data().decode('utf-8')

            log_body.update({
                "method": request.method,
                "endpoint": request.url,
                "input": {
                    "headers": dict(zip(request.headers.keys(), request.headers.values())),
                    "body": body
                }
            })

        if logs_table:
            query_helper = BaseQuery()
            try:
                reg, = query_helper.crear(logs_table, log_body)
                g.service_call_id = reg[logs_table_id]
                g.urllib3_calls_count = 0
                g.telnet_calls_count = 0
            except PGError as db_error:
                io_logger.error("Psycopg2Error: %s", db_error)
                return make_response(f"Psycopg2Error: {db_error}", 500)
            except Exception as unhandled_exc:
                io_logger.error("Exception: %s", unhandled_exc)
                return make_response(f"Exception: {unhandled_exc}", 500)


def after_app_request(res: Response) -> Response:
    reqPath = request.path
    if request.method == "OPTIONS" or reqPath== "/":
        return res
    else:
        logs_table = os.getenv('LOGS_TABLE')
        logs_table_id = os.getenv('LOGS_TABLE_ID')
        call_id = g.pop("service_call_id", None)
        g.pop("urllib3_calls_count", None)
        g.pop("telnet_calls_count", None)
        if call_id is None:
            io_logger.error("El id de llamada del servicio no se esta guardando")
            return res

        log_body = {
            logs_table_id: call_id,
            "pk_log_type": "SERVICIO",
            "time_end": datetime.now(timezone("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S")
        }
        if res:
            if res.is_json:
                body = res.get_json()
            else:
                try:
                    body = res.get_data()
                    if isinstance(body, bytes):
                        body = body.decode()
                except Exception:
                    body = res.content_type
            log_body.update({
                "output": {
                    "headers": dict(zip(res.headers.keys(), res.headers.values())),
                    "body": body,
                },
                "status": res.status,
            })

        io_logger.info("\n%s", json.dumps(log_body, default=str, indent=4))
        if logs_table:
            query_helper = BaseQuery()
            try:
                query_helper.modificar_log(logs_table, logs_table_id, log_body)
            except PGError as db_error:
                io_logger.error("Psycopg2Error: %s", db_error)
                return make_response(f"Psycopg2Error: {db_error}", 500)
            except Exception as unhandled_exc:
                io_logger.error("Exception: %s", unhandled_exc)
                return make_response(f"Exception: {unhandled_exc}", 500)

        return res


def teardown_app_request(error):
    if error:
        io_logger.error(error)
        # Log the error
        pass

def add_logs():
    base_blueprint.before_app_request(before_app_request)

    base_blueprint.after_app_request(after_app_request)

    base_blueprint.teardown_app_request(teardown_app_request)


################## Python loggers ##################
logs_formatter = logging.Formatter('%(asctime)s (%(name)s)::%(levelname)s -> %(message)s')
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logs_formatter)


loggers = {
    ###### Logger data bases
    "db_logger": {
        "level": logging.DEBUG,
        "print": False,
        "subfolder": "",
    },
    ###### Logger inputs y outputs
    "io_logger": {
        "level": logging.DEBUG,
        "print": False,
        "subfolder": "",
    },
    ###### Logger urllib3
    "urllib3": {
        "level": logging.DEBUG,
        "print": False,
        "subfolder": "",
    },
    ###### Another logger
    #### Logger services
    "back_end_test_blueprint_logger": {
        "level": logging.DEBUG,
        "print": True,
        "subfolder": "/back_end_test",
    },
}

for logger_name, logger_data in loggers.items():
    __logger = logging.getLogger(logger_name)
    __logger.setLevel(logger_data["level"])
    ## Print to console
    if logger_data["print"]:
        __logger.addHandler(stream_handler)
    ## Save in file
    if os.getenv("LOGS_FOLDER") and logger_name:
        filename = f'{os.getenv("LOGS_FOLDER")}{logger_data["subfolder"]}/{logger_name}.log'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        __file = logging.FileHandler(filename, "a")
        __file.setFormatter(logs_formatter)
        __logger.addHandler(__file)
