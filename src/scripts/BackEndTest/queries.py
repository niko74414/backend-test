from src.templates_lib import BaseQuery
from src.templates_lib import DBPostController, ControllerEntry, AnyDict, ListedDict
from typing import List, Optional, Union, TypedDict
import math
from psycopg2.extras import execute_values

class PaginatedType(TypedDict):
    results: ListedDict
    maxElems: int
    maxPages: int

class Query(BaseQuery):
    """Open to create custom method and use the basic ones"""