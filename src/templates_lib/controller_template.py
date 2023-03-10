import json
from abc import ABC
from flask import request
from functools import wraps
from logging import Logger, getLogger
from psycopg2.errors import Error as PGError
from typing import Callable, List, Optional, Union, Tuple
from schema import Schema, SchemaError, And, Optional as SchemaOptional, Use
from src.templates_lib.utils import AnyDict, ListedDict, ResponseReturnValue, JSONEncoder


ControllerEntry = Union[AnyDict, ListedDict]
# AdaptedInput = Union[AnyDict, ControllerEntry, Tuple[AnyDict, ControllerEntry]]


class ErrorResponse(Exception):
    """Custom exception response class"""
    def __init__(self, *args: object) -> None:
        if not args:
            raise Exception("No se han pasado parametros a 'ErrorResponse'.")
        if len(args) == 1:
            args = args[0]

        self.args: ResponseReturnValue = args
        

class Controller(ABC):
    """
    The Abstract Class defines a template method that contains a skeleton of
    some algorithm, composed of calls to (usually) abstract primitive
    operations.

    Concrete subclasses should implement these operations, but leave the
    template method itself intact.
    """

    def __init__(self, _logger: Optional[Logger] = None) -> None:
        self.logger = _logger or getLogger(self.__name__)

    # These operations have to be implemented in subclasses.

    # These are "hooks." Subclasses may override them, but it's not mandatory
    # since the hooks already have default (but empty) implementation. Hooks
    # provide additional extension points in some crucial places of the
    # algorithm.

    """"""
    

class GetController(Controller):
    _schema_to_validate_args: Schema
    _validator_args: Callable[[Schema, AnyDict], AnyDict]
    _params: AnyDict

    def __init__(
        self, 
        logger: Optional[Logger] = None, 
        schema: Optional[Schema] = None, 
        validator: Optional[Callable[[Schema, AnyDict], AnyDict]] = None
    ) -> None:
        super().__init__(logger)
        self._schema_to_validate_args = schema
        self._validator_args = validator

    def __call__(self, controller: Callable[[AnyDict, AnyDict], ResponseReturnValue]) -> ResponseReturnValue:
        @wraps(controller)
        def run(**kwargs):
            self._params = kwargs
            res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
            try:
                data = self._adapt_input()
            except ErrorResponse as e:
                return e.args
            except Exception as ex:
                res["msg"] = f"Error sin controlar validando la entrada: {ex}"
                return res, 500

            try:
                return controller(data, self._params)
            except ErrorResponse as e:
                return e.args
            except Exception as ex:
                res["msg"] = f"Error sin controlar durante la ejecucion del controlador: {ex}"
                return res, 500
        
        return run

    def _adapt_input(self) -> AnyDict:
        res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
        try:
            if self._validator_args:
                return self._validator_args(self._schema_to_validate_args, self._params)

            args = request.args.copy()

            if self._schema_to_validate_args:
                schema = Schema(self._schema_to_validate_args)

                args: AnyDict = schema.validate(args)

                self.logger.info(f"Parametros validados validados: {json.dumps(args, cls=JSONEncoder)}")
            return args
        except SchemaError as e:
            self.logger.error(f"SchemaError: {e}")
            res["msg"] = f"SchemaError: {e}"
            raise ErrorResponse(res, 400)
        except Exception as e:
            self.logger.error(f"Exception (schema): {e}")
            res["msg"] = f"Exception (schema): {e}"
            raise ErrorResponse(res, 500)


class GetControllerPaginated(GetController):
    def _adapt_input(self) -> AnyDict:
        res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
        try:
            new_schema = {
                **self._schema_to_validate_args,
                SchemaOptional("page", default=1): And(
                    Use(int),
                    lambda n: n > 0,
                    error="'page' debe ser un numero entero mayor a cero"
                ),
                SchemaOptional("limit", default=10): And(
                    Use(int),
                    lambda n: n >= 0,
                    error="'limit' debe ser un numero entero mayor o igual a cero"
                ),
                SchemaOptional("sortBy"): And(
                    str,
                    lambda w: len(w) > 0,
                    error="'sortBy' no debe ser vacio"
                ),
                SchemaOptional("sortDir"): And(
                    str,
                    lambda w: w in ["ASC", "DESC"],
                    error="'sortDir' debe ser uno de estos valores: ['ASC', 'DESC']"
                ),
            }

            if self._validator_args:
                return self._validator_args(new_schema, self._params)

            args = request.args.copy()

            schema = Schema(new_schema)

            args: AnyDict = schema.validate(args)
            self.logger.info(f"Parametros validados validados: {json.dumps(args, cls=JSONEncoder)}")
            return args
        except SchemaError as e:
            self.logger.error(f"SchemaError: {e}")
            res["msg"] = f"SchemaError: {e}"
            raise ErrorResponse(res, 400)
        except Exception as e:
            self.logger.error(f"Exception (schema): {e}")
            res["msg"] = f"Exception (schema): {e}"
            raise ErrorResponse(res, 500)


class PostController(Controller):
    _schema_to_validate_body: Schema
    _validator_body: Callable[[Schema, AnyDict], ControllerEntry]
    _params: AnyDict

    def __init__(
        self, 
        logger: Optional[Logger] = None, 
        schema: Optional[Schema] = None,
        validator: Optional[Callable[[Schema, AnyDict], ControllerEntry]] = None
    ) -> None:
        super().__init__(logger)
        self._schema_to_validate_body = schema
        self._validator_body = validator

    def __call__(self, controller: Callable[[ControllerEntry, AnyDict], ResponseReturnValue]) -> ResponseReturnValue:
        @wraps(controller)
        def run(**kwargs):
            self._params = kwargs
            res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
            try:
                data = self._adapt_input()
            except ErrorResponse as e:
                return e.args
            except Exception as ex:
                res["msg"] = f"Error sin controlar validando la entrada: {ex}"
                return res, 500

            try:
                return controller(data, self._params)
            except ErrorResponse as e:
                return e.args
            except Exception as ex:
                res["msg"] = f"Error sin controlar durante la ejecucion del controlador: {ex}"
                return res, 500
        
        return run

    def _adapt_input(self) -> ControllerEntry:
        res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
        try:
            if self._validator_body:
                return self._validator_body(self._schema_to_validate_body, self._params)

            postData = {}
            if self._schema_to_validate_body:
                # if not request.json:
                #     self.logger.error("Request con body vacio")
                #     raise Exception("Request con body vacio")

                postData = request.json

                schema = Schema(self._schema_to_validate_body)

                postData: ControllerEntry = schema.validate(postData)

                self.logger.info(f"Body del request validado: {json.dumps(postData, cls=JSONEncoder)}")

            return postData
        except SchemaError as e:
            self.logger.error(f"SchemaError: {e}")
            res["msg"] = f"SchemaError: {e}"
            raise ErrorResponse(res, 400)
        except Exception as e:
            self.logger.error(f"Exception (schema): {e}")
            res["msg"] = f"Exception (schema): {e}"
            raise ErrorResponse(res, 500)


class PutController(Controller):
    _schema_to_validate_args: Schema
    _schema_to_validate_body: Schema
    _validator_args: Callable[[Schema, AnyDict], Union[AnyDict, List[str]]]
    _validator_body: Callable[[Schema, AnyDict], ControllerEntry]
    _params: AnyDict

    def __init__(
        self, 
        logger: Optional[Logger] = None, 
        schema_args: Optional[Schema] = None, 
        schema_body: Optional[Schema] = None,
        validator_args: Optional[Callable[[Schema, AnyDict], Union[AnyDict, List[str]]]] = None,
        validator_body: Optional[Callable[[Schema, AnyDict], ControllerEntry]] = None,
    ) -> None:
        super().__init__(logger)
        self._schema_to_validate_args = schema_args
        self._schema_to_validate_body = schema_body
        self._validator_args = validator_args
        self._validator_body = validator_body

    def __call__(self, controller: Callable[[Union[AnyDict, List[str]], ControllerEntry, AnyDict], ResponseReturnValue]) -> ResponseReturnValue:
        @wraps(controller)
        def run(**kwargs):
            self._params = kwargs
            res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
            try:
                args, data = self._adapt_input()
            except ErrorResponse as e:
                return e.args
            except Exception as ex:
                res["msg"] = f"Error sin controlar validando la entrada: {ex}"
                return res, 500

            try:
                return controller(args, data, self._params)
            except ErrorResponse as e:
                return e.args
            except Exception as ex:
                res["msg"] = f"Error sin controlar durante la ejecucion del controlador: {ex}"
                return res, 500
        
        return run

    def _adapt_input(self) -> Tuple[Union[AnyDict, List[str]], ControllerEntry]:
        return GetController._adapt_input(self), PostController._adapt_input(self)


class DBGetController(GetController):
    def __call__(self, _db_query: Callable[[AnyDict, AnyDict], ResponseReturnValue]) -> ResponseReturnValue:
        @wraps(_db_query)
        def _make_business_logic(args: AnyDict, params: AnyDict) -> ResponseReturnValue:
            res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
            try:
                return _db_query(args, params)
            except ErrorResponse as e:
                return e.args
            except PGError as e:
                self.logger.error(f"Psycopg2Error: {e}")
                res["msg"] = f"Psycopg2Error: {e}"
                raise ErrorResponse(res, 400)
            except Exception as e:
                self.logger.error(f"Exception (db): {e}")
                res["msg"] = f"Exception (db): {e}"
                raise ErrorResponse(res, 500)

        return super().__call__(_make_business_logic)


class DBGetControllerPaginated(GetControllerPaginated):
    def __call__(self, _db_query: Callable[[AnyDict, AnyDict], ResponseReturnValue]) -> ResponseReturnValue:
        @wraps(_db_query)
        def _make_business_logic(args: AnyDict, params: AnyDict) -> ResponseReturnValue:
            res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
            try:
                return _db_query(args, params)
            except ErrorResponse as e:
                return e.args
            except PGError as e:
                self.logger.error(f"Psycopg2Error: {e}")
                res["msg"] = f"Psycopg2Error: {e}"
                raise ErrorResponse(res, 400)
            except Exception as e:
                self.logger.error(f"Exception (db): {e}")
                res["msg"] = f"Exception (db): {e}"
                raise ErrorResponse(res, 500)

        return super().__call__(_make_business_logic)


class DBPostController(PostController):
    def __call__(self, _db_query: Callable[[ControllerEntry, AnyDict], ResponseReturnValue]) -> ResponseReturnValue:
        @wraps(_db_query)
        def _make_business_logic(postData: ControllerEntry, params: AnyDict) -> ResponseReturnValue:
            res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
            try:
                return _db_query(postData, params)
            except ErrorResponse as e:
                return e.args
            except PGError as e:
                self.logger.error(f"Psycopg2Error: {e}")
                res["msg"] = f"Psycopg2Error: {e}"
                raise ErrorResponse(res, 400)
            except Exception as e:
                self.logger.error(f"Exception (db): {e}")
                res["msg"] = f"Exception (db): {e}"
                raise ErrorResponse(res, 500)

        return super().__call__(_make_business_logic)


class DBPutController(PutController):
    def __call__(self, _db_query: Callable[[AnyDict, ControllerEntry, AnyDict], ResponseReturnValue]) -> ResponseReturnValue:
        @wraps(_db_query)
        def _make_business_logic(args: AnyDict, postData: ControllerEntry, params: AnyDict) -> ResponseReturnValue:
            res = {"status": False, "codigo": 0, "msg": "", "obj": {}}
            try:
                return _db_query(args, postData, params)
            except ErrorResponse as e:
                return e.args
            except PGError as e:
                self.logger.error(f"Psycopg2Error: {e}")
                res["msg"] = f"Psycopg2Error: {e}"
                raise ErrorResponse(res, 400)
            except Exception as e:
                self.logger.error(f"Exception (db): {e}")
                res["msg"] = f"Exception (db): {e}"
                raise ErrorResponse(res, 500)

        return super().__call__(_make_business_logic)

