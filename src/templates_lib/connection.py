import os
import logging
from psycopg2 import connect
from contextlib import contextmanager
from psycopg2.extensions import connection
from psycopg2.extras import LoggingConnection
from typing import Generator, List, TypedDict, Union


class DBInitData(TypedDict):
    user: str
    password: str
    host: str
    port: Union[str, int]
    database: str


def getDBInfo():
    users = [x.strip() for x in os.getenv("DB_USER", "").split(";")]
    passwords = [x.strip() for x in os.getenv("DB_PASSWORD", "").split(";")]
    hosts = [x.strip() for x in os.getenv("DB_HOST", "").split(";")]
    ports = [x.strip() for x in os.getenv("DB_PORT", "").split(";")]
    databases = [x.strip() for x in os.getenv("DB_DBNAME", "").split(";")]

    lenadbs = max(len(users), len(passwords), len(hosts), len(ports), len(databases))

    def safe_list_get(l, idx, default = None):
        try:
            return l[idx]
        except IndexError:
            return default

    available_dbs: List[DBInitData] = []
    for index in range(lenadbs):
        tempDict = {
            "user": safe_list_get(users, index, ""),
            "password": safe_list_get(passwords, index, ""),
            "host": safe_list_get(hosts, index, ""),
            "port": safe_list_get(ports, index, ""),
            "database": safe_list_get(databases, index, ""),
        }
        available_dbs.append(tempDict)

    return available_dbs

class Connection:
    def __init__(self) -> None:
        self.__available_dbs = getDBInfo()

    def _connect(self, db: int = 0) -> connection:
        try:
            connection = connect(**self.__available_dbs[db], connection_factory=LoggingConnection)
            connection.initialize(logging.getLogger("db_logger"))
            return connection
        except Exception as e:
            raise Exception(f"No fue posible realizar una conexion (psycopg2 error): {e}")
    
    @contextmanager
    def _open_connection(self, db: int = 0) -> Generator[connection, None, None]:
        try:
            connection = connect(**self.__available_dbs[db], connection_factory=LoggingConnection)
            connection.initialize(logging.getLogger("db_logger"))
        except Exception as e:
            raise Exception(f"No fue posible realizar una conexion (psycopg2 error): {e}")
        else:
            try:
                with connection as conn:
                    yield conn
            finally:
                connection.close()

    def _closeConnection(self, connection: connection):
        connection.close()
