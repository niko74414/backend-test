import math
import json
from functools import reduce
from psycopg2.extras import execute_values
from typing import List, Optional, Union, TypedDict
from src.templates_lib.connection import Connection
from src.templates_lib.utils import AnyDict, ListedDict
from src.templates_lib.utils import JSONEncoder, AnyDict, ListedDict, PaginatedType
from psycopg2.extensions import register_adapter
from psycopg2.extras import execute_values, Json



class PaginatedType(TypedDict):
    results: ListedDict
    maxElems: int
    maxPages: int

class Json_pyscopg2(Json):
    def dumps(self, obj):
        return json.dumps(obj, cls=JSONEncoder)

class BaseQuery(Connection):
    def __init__(self) -> None:
        super().__init__()
        register_adapter(dict, Json_pyscopg2)


    def _adaptType(self, val):
        if isinstance(val, (dict, list)):
            return Json_pyscopg2(val)
        return val


    def _adaptInputs(self, inputDict: AnyDict):
        return { x: self._adaptType(inputDict[x]) for x in inputDict }


    def _adaptList(self, inputList: ListedDict):
        return [self._adaptInputs(x) for x in inputList]


    def _filterDiff(self, updated: ListedDict, to_check: AnyDict, keys: List[str]):
        return not reduce(lambda x, item: x or reduce(lambda a, y: a and item[y] == to_check[y], keys, True), updated, False)


    def crear(self, table: str, inputJson: Union[ListedDict, AnyDict], returning: str = "*") -> Optional[ListedDict]:
        if type(inputJson) == dict:
            inputJson = [inputJson]
        if not len(inputJson):
            raise Exception("No se enviaron datos de entrada para el insert")

        query = f"""INSERT INTO {table} 
        ({", ".join(inputJson[0].keys())}) 
        OVERRIDING SYSTEM VALUE
        VALUES %s
        {f"RETURNING {returning}" if returning else ""};"""
        
        with self._open_connection() as conexion:
            with conexion.cursor() as cursor:
                Lista = execute_values(
                    cursor, 
                    query, 
                    self._adaptList(inputJson), 
                    f'({", ".join(map(lambda x: f"%({x})s", inputJson[0].keys()))})',
                    fetch=True
                )

                if returning:
                    cols = [obj[0] for obj in cursor.description]
                    Lista = [
                        {
                            cols[index]: val for index, val in enumerate(obj)
                        } for obj in Lista
                    ]
                    return Lista

    def modificar(self, table: str, args: List[str], inputJson: Union[ListedDict, AnyDict], insert_on_non_exiting: bool = False) -> None:
        if type(inputJson) == dict:
            inputJson = [inputJson]

        if not len(inputJson):
            raise Exception("No se enviaron datos de entrada para el update")

        query = f"""UPDATE {table} SET {", ".join(map(lambda x: f"{x} = data.{x}", filter(lambda x: not x in args, inputJson[0].keys())))} 
            FROM (VALUES %s) AS data ({", ".join(inputJson[0].keys())})
            WHERE {", ".join(map(lambda x: f"{table}.{x} = data.{x}", args))}
            RETURNING *;"""
        
        with self._open_connection() as conexion:
            with conexion.cursor() as cursor:
                Lista = execute_values(
                    cursor, 
                    query, 
                    self._adaptList(inputJson), 
                    f'({", ".join(map(lambda x: f"%({x})s", inputJson[0].keys()))})',
                    fetch=True
                )
                cols = [obj[0] for obj in cursor.description]
                Lista = [
                    {
                        cols[index]: val for index, val in enumerate(obj)
                    } for obj in Lista
                ]
                if len(Lista) != len(inputJson):
                    if insert_on_non_exiting:
                        self.crear(
                            table, 
                            list(
                                filter(
                                    lambda to_check: self._filterDiff(Lista, to_check, args), 
                                    inputJson
                                )
                            )
                        )
                    else:
                        raise Exception(f"Hay datos que no se encuentran en la tabla {table}")

    def crearSimple(self, table: str, inputJson: AnyDict, returning: str = "*") -> Optional[ListedDict]:
        query = f"""INSERT INTO {table} 
        ({", ".join(inputJson.keys())}) 
        VALUES ({", ".join([f"%({x})s" for x in inputJson.keys()])})
        {f"RETURNING {returning}" if returning else ""};"""

        with self._open_connection() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(query, inputJson)

                if returning:
                    cols = [obj[0] for obj in cursor.description]
                    Lista = [
                        {
                            cols[index]: val for index, val in enumerate(obj)
                        } for obj in cursor.fetchall()
                    ]
                    return Lista

    def modificarSimple(self, table: str, args: List[str], inputJson: AnyDict, insert_on_non_exiting: bool = False) -> None:
        query = f"""UPDATE {table} SET {", ".join([f"{x} = %({x})s" for x in inputJson.keys()])} 
            WHERE {", ".join([f"{table}.{x} = %({x})s" for x in args])}
            RETURNING *;"""
        with self._open_connection() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(query, inputJson)
                
                cols = [obj[0] for obj in cursor.description]
                Lista = [
                    {
                        cols[index]: val for index, val in enumerate(obj)
                    } for obj in cursor.fetchall()
                ]
                if len(Lista) == 0:
                    if not insert_on_non_exiting:
                        raise Exception(f"Hay datos que no se encuentran en la tabla {table}")
                    
                    self.crear(table, inputJson)

    def consultar(self, table: str, searchObj: AnyDict, bringName=False) -> Union[ListedDict, PaginatedType]:
        pages = ""
        order = ""
        if "page" in searchObj and "limit" in searchObj:
            pages = f"""
            OFFSET ((%(page)s - 1) * %(limit)s) ROWS
            FETCH NEXT %(limit)s ROWS ONLY
            """
        if "sortBy" in searchObj:
            order = f'ORDER BY {searchObj.get("sortBy")} {searchObj.get("sortDir", "ASC")}'

        condition = []
        for key in searchObj:
            if key in ["page", "limit", "sortBy", "sortDir"]:
                continue
            if isinstance(searchObj[key], str):
                searchObj[key] = f'%{searchObj[key].lower()}%'
                condition.append(f"LOWER({key}) LIKE %({key})s")
            else:
                condition.append(f"{key}=%({key})s")
        condition = " AND ".join(condition)

        query = f"""SELECT * FROM {table} 
        {f"WHERE {condition}" if condition else ""}
        {order} {pages};"""

        with self._open_connection() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(query, searchObj)
                Lista = cursor.fetchall()
                if bringName:
                    cols = [obj[0] for obj in cursor.description]
                    Lista = [
                        {
                            cols[index]: val for index, val in enumerate(obj)
                        } for obj in Lista
                    ]
                
                if "page" in searchObj and "limit" in searchObj:
                    queryElms = f'SELECT COUNT(*) FROM {table} {f"WHERE {condition}" if condition else ""};'
                    cursor.execute(queryElms, searchObj)
                    maxElems = cursor.fetchall()[0][0]
                    maxPages = math.ceil(maxElems/searchObj["limit"])

                    return {
                        "results": Lista,
                        "maxElems": maxElems,
                        "maxPages": maxPages,
                    }

                return Lista

    def getNextEmptyId(self, table: str, id_name: str) -> int:
        """
        Retorna el siguiente numero disponible para la tabla y 
        columna ingresada o 1 en caso de no tener registros
        """
        query = f"""SELECT  id
            FROM    (
                    SELECT  1 AS id
                    ) q1
            WHERE   NOT EXISTS
                    (
                    SELECT  1
                    FROM    {table}
                    WHERE   id = 1
                    )
            UNION ALL
            SELECT  *
            FROM    (
                    SELECT  {id_name} + 1 as id
                    FROM    {table} t
                    WHERE   NOT EXISTS
                            (
                            SELECT  1
                            FROM    {table} ti
                            WHERE   ti.{id_name} = t.{id_name} + 1
                            )
                    ORDER BY
                            {id_name}
                    LIMIT 1
                    ) q2
            ORDER BY
                    id
            LIMIT 1;"""
        with self._open_connection() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchone()[0]

    def fixIdSeq(self, table: str, id_name: str, seq_name: str) -> None:
        """
        Acomoda el numero de la secuencia para en caso de ingresar
        el id manualmente no se quede la secuencia atras
        """
        query = f"SELECT setval(%s::regclass, %s, true);"

        with self._open_connection() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(query, (seq_name, self.getNextEmptyId(table, id_name) - 1))
    
    def modificar_log(self, table: str, table_id_name: str, mods: AnyDict):
        query = f"""\
            UPDATE {table} 
            SET {", ".join([f"{col_name} = %({col_name})s" for col_name in mods.keys()])} 
            WHERE {table_id_name} = %({table_id_name})s AND pk_log_type = %(pk_log_type)s
            RETURNING *;"""
        with self._open_connection() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(query, mods)

                cols = [obj[0] for obj in cursor.description]
                return {
                    cols[index]: val for index, val in enumerate(cursor.fetchone())
                }