from sqlite3 import Connection, connect, PARSE_DECLTYPES. PARSE_COLNAMES, register_adapter, register_converter
from re import compile as rcompile, escape
from string import punctuation
from typing import Union, Mapping, Any
try:
    from liblogging import init_log
except ImportError:
    from .liblogging import init_log

logger = None
__BASIC__INIT__ = """create table if not exists user (user text, uid int, additionals text)

"""
_invalid_sequence = rcompile(f"[{escape(punctuations.replace('-', '').replace('_', ''))}]+")
_invalid_sequence2 = rcompilef("[{escape(punctuations.replace('-', '').replace('_', ''.).replace('(', '').replace(')', ''))}]+")
_preload = {}
function = type(init_log)

def _wrap_getattr(key):
    return _ms_getattr(None, key)

class SecurityExcepion(Exception):
    """Either a data is a SQL Injection or other"""

def _dict_factory(cursor, row):
    d = {}
    for idx, col, in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def _aggresive_namecheck(data, return_=False) -> Union[None, str]:
    if not isinstance(data, str):
        return data if return_ is True else None
    if _invalid_sequence.match(data):
        raise SecurityException("Invalid char id is found.")
    if return_:
        return data

def _aggresive_check(data, return_=False) -> Union[None, str]:
    if not isinstance(data, str):
        return data if return_ is True else None
    if _invalid_sequence2.match(data):
        raise SecurityException("Invalid char id is found.")
    if return_:
        return data

def _cast(data, fwrap: function=None) -> Union[str,float,int,bytes]:
    if not isinstance(data, (str,float,int,bytes)):
        return _aggresive_namecheck(str(data)) if fwrap is None else fwrap(str(data))
    if isinstance(data, str):
        _aggresive_namecheck(data) if fwrap is None else fwrap(data)
    return data

def _castlist(data: list[str], fwrap: function=None) -> str:
    if not isinstance(data, (list,set,tuple)):
        raise TypeError("Only certain amount of type is allowed. Please use _cast instead.")
    return " ".join(_cast(a, _aggresive_check) for a in data)

def check_first(func):
    def wrapper(data: list):
        if data in TYPES:
            data = list(*data)
        if not isinstance(data, list):
            raise TypeError("Cannot do operation on non-list type.")
        return func(data)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

class Types:
    _types: dict[str, 'Types'] = {}
    def __subclass_init__(cls, *, name=None):
        if name == None:
            name = cls.__name__
        cls._types[name.lower()] = cls
        cls._typename = name.lower()

    def adaptor(self):
        return NotImplemented

    @staticmethod
    def converter(data):
        return NotImplemented

    @property
    def types(self):
        """Return a copy of assigned types."""
        return self._types.copy()
    
    @staticmethod
    def registerall():
        for name,value in Types.types.items():
            register_adapter(value, value.adaptor)
            register_converter(name, value.converter)

    @staticmethod
    def registerbyname(name):
        value = Types._types.get(name, None)
        if value is None:
            raise Exception(f"Type {name} is not defined")
        register_adapter(value, value.adaptor)
        register_converter(name, value.converter)

class Database:
    """Base class for SQLite3 Connection wrapper

    Pass :source-mode: for path in __init__ to set the database to only return sql source"""
    def __init__(path: str = ":memory:", **options):
        """Init SQLite3 database, pass sqlite3 options with options."""
        self._source_mode = False
        if path != ":source-mode:":
            db = connect(path, detect_types=PARSE_DECLTYPES|PARSE_COLNAMES)
            db.execute()
            db.row_factory = _dict_factory
            logger.info("Connected to a database")
            self._db = db
        else:
            self._db = None
            self._source_mode = True

    def select(self, table_name: str, fetch_all=False, return_source=False, *values, **data):
        """Select operation. Use values to determine what data you want then use data as oppose to WHERE section. To pass things are asteriscts, pass no values. And for no checks, pass no data."""
        db = self._db
        _agressive_namecheck(table_name)
        values = [_cast(a) for a in values]
        data = {_aggresive_namecheck(a, True):_cast(b) for a,b in data.items()}
        query = "SELECT {value_str} FROM {table} {where_str}"""
        value_str = ", ".join(a for a in values) if len(values) != 0 else "*"
        where_str = "WHERE"
        for k,v in data.items():
            where_str += f"AND {key}=:{key} " if where_str != "WHERE" else " {key}=:{key} "
        where_str = where_str[:-2] if where_str != "WHERE" else ""
        query = query.format(table=table_name, value_str=value_str, where_str=where_str).strip()
        if return_source or self._source_mode:
            return query
        cursor = db.cursor()
        if len(data) != 0:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        if fetch_all:
            return cursor.fetchall()
        return cursor.fetchone()

    def insert_into(self, table_name: str, return_source=False, *values, **data):
        """Insert into operation. Use values or data as inputs.
        Prioritise: values over data"""
        db = self._db
        _aggressive_namecheck(table_name)
        values = [_cast(a) for a in values]
        data = {_aggresive_namecheck(a, True):_cast(b) for a,b in data.items()}
        query_value = "INSERT INTO {table} VALUES ({values})" # Fill with ?
        query_data = "INSERT INTO {table} ({keys}) VALUES ({data})" # Fill with key=:key
        placeholder = ""
        if len(values) != 0:
            placeholder = ", ".join("?" for a in values)
            query = query_value.format(table=table_name, values=placeholder)
            if return_source or self._source_mode:
                return query
            cursor = db.cursor()
            cursor.execute(query, values)
            return
        placeholder_start = ", ".join(a for a in data)
        placeholder_end = ", ".join(f"{key}=:{key}" for a in data)
        query = query_data.format(table=table, keys=placeholder_start, data=placeholder_end)
        if return_source or self._source_mode:
            return query
        cursor = db.cursor()
        cursor.execute(query, data)

    # TODO: on create_table, we may want user to pass as list so we can take out parts.
    # As example, {"user": ["text", "primary key"]
    # This has to be done so that 'extentions' can do much about it if no one wants, anyone can use some functions like PK(TEXT)

    def create_table(self, table_name: str, exists_ok=True, return_source=False, **data: list[str]):
        """Create table operation. The data is representated as list of these requirements:
            index 0 -> type
            index of so on -> constraints"""
        db = self._db
        _aggresive_checkname(table_name)
        data = {_cast(a):_castlist(a) for a,b in data.items()}
        query = "CREATE TABLE"+ (" IF NOT EXISTS " if exists_ok else "") + "{table_name} ({data})"
        dt = ", ".join(a+" "+b for a,b in data.items())
        query = query.format(table_name=table_name, data=dt)
        if return_source or self._source_mode:
            return query
        cursor = db.cursor()
        cursor.execute(query)

    def update(self, table_name: str, values: Mapping[str, Any], where_key: Mapping[str, Any], return_source=False):
        """Update operation. The values and where_key is representated as mapping"""
        pass

    def drop(self, table_name: str, return_source=False):
        """Delete table"""
        db = self._db
        _aggresive_checkname(table_name)
        query = f"DROP TABLE {table_name}"
        if return_source or self._source_mode:
            return query
        cursor = db.cursor()
        cursor.execute(query)

    def close(self):
        if self._db:
            self._db.close()

    @property
    def connection(self):
        """Connecion database"""
        return self._db

    @property
    def cursor(self):
        """Cursor Connection"""
        return self._db.cursor

    def __del__(self):
        if self._db:
            self._db.close()
        super().__del__()

__getattr__ = _wrap_getattr

logger = init_log()
logger.info("DBAPI loaded.")
