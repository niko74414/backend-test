import json
from flask import Response
from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, List, TypedDict, Union, Tuple

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


################## Excepciones ##################
class ServiceCustomException(Exception):
    """ Error customizado del servicio consultado """


################# Common types ##################
AnyDict = Dict[str, Any]
ListedDict = List[AnyDict]

class PaginatedType(TypedDict):
    results: ListedDict
    maxElems: int
    maxPages: int

class ResTrx(TypedDict):
    msg: str
    codigo: str
    status: bool
    obj: Any

ResponseValue = Union[Response, ResTrx]
StatusCode = int

# the possible types for an individual HTTP header
HeaderName = str
HeaderValue = Union[str, List[str], Tuple[str, ...]]

# the possible types for HTTP headers
HeadersValue = Union[Dict[HeaderName, HeaderValue], List[Tuple[HeaderName, HeaderValue]]]
ResponseReturnValue = Union[
    ResponseValue,
    Tuple[ResponseValue, HeadersValue],
    Tuple[ResponseValue, StatusCode],
    Tuple[ResponseValue, StatusCode, HeadersValue],
]
