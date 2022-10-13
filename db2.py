# TODO: Use custom class like statement to do various things.
# TODO: create class as opposed to: where, as, etc.
# Usage: where('user')=='median' should be equal to where name=median
# The default stmt should be: stmt(10)-5 to be 10-5
# Great for: set('quantity', stmt(10)-5)
# General syntax will be: 
"""
update('stuff')(
    set('stuff0', 5),
    where('stuff0')==5
).exec(db)

The where('...')==5 is equalivent to where('...', eq=5)
and stmt('stuff0')-5 is equalivent to stmt('stuff0', sub=5)

Note, if columns are defined, the internal usage will use :keyname
If not, determine from fixed length of given array and will use ?

fetch/all:
data = select()(
    ('data',),
    from_('user')
).execfetch(db, returnall=True|False)

to select all colums, use ALL constant.

insert into (single):
insert_to('table', ('col0', 'col2'))(
    ('data0', 'data1')
).exec(db)
OR
insert into (single):
insert_to('table', ('col0', 'col2'))(
    'data0',
    'data1'
).exec(db)

insert into (many):
insert_to("table", ("col0", "col2"))(
    ("data0", "data1"),
    ("data2", "data3")
).exec(db)

As hinting for insert many, only list, set, tuple, and dict are allowed.
However, for dict, the signature must be dict[str, list[Any]]

insert into (single,dict):
insert_to(table)({
    "col0": "data0",
    "col2": "data1"
}).exec(db)

insert ino (many,dict):
insert_to(table)({
    "col0": ["data0", "data2"],
    "col2": ["data1", "data3"],
}).exec(db)

For special constraint like FOREIGN KEY, UNIQUE, and PRIMARY KEY:
foreign_key('uid').reference(table('proc').userid)
unique('uid')
primary_key('uid')

"""

from sqlite3 import Connection, connect

_null = object()

class PreHolder:
    def __init__(self, data):
        self.data = data
    
    def __repr__(self):
        return str(self.data)
    
    def __str__(self):
        return repr(self)

    def exec(self, database: Connection):
        cr = database.cursor()
        cr.execute(str(self))

    def execfetch(self, database: Connection, returnall=False):
        cr = database.cursor()
        cr.execute(str(self))
        if returnall:
            return cr.fetchall()
        return cr.fetch()

def _translate_operands(data: list, replaceOf, replaceAs: tuple, pure=False):
    rt = ""
    opr = {'add': "+", 'sub':'-', 'mul':'*', 'div':'/', 'null':' '}
    for a in data:
        if (a is replaceOf) or (a == replaceOf):
            a = replaceAs
        
        rt += f'{opr[a[0]]} {a[1]} '
    return rt[2:-1] if pure is False else rt[:-1]

def _translate_chks(data, parent, return_basic=False):
    opr = {'eq': '=', 'ne': '!=', 'gt': ">", 'ge': '>=', 'lt': '<', 'le': '<='}
    if data[1] == _null:
        return ""
    return f"{parent} {opr[data[0]]} {data[1]}" if return_basic is False else f"{parent} {opr[data[0]]}"

class BaseSTMT:
    _keywords = {}
    _reversed = {}
    def __init_subclass__(cls, *, name=None):
        if name is None:
            name = cls.__name__
        cls._keywords[name.lower()] = cls
        cls._reversed[cls] = name.lower()
    
    def _raise_on_operand(self):
        if self._no_operand or self._no_fulloperand:
            raise Exception("Cannot do certain things")
    
    def _raise_on_check(self):
        if self._no_fulloperand:
            raise Exception("Cannot do certain things")

    def __init__(self, name, *args, **kwargs):
        self._name = name
        self._args = args
        self._kwargs = kwargs
        kwargs['ops'] = kwargs.get('ops', [_null])
        kwargs['chk'] = kwargs.get('chk', ('null', _null,))
        self._ourpos = kwargs['ops'].index(_null)
        self._no_operand = kwargs.get('no_operand', False)
        self._no_fulloperand = kwargs.get('no-foperands', False)

    def __eq__(self, other):
        kwargs = self._kwargs.copy()
        kwargs['chk'] = ('eq', other)
        return type(self)(self._name, *self._args, **kwargs)

    def __lt__(self, other):
        kwargs = self._kwargs.copy()
        kwargs['chk'] = ('lt', other)
        return type(self)(self._name, *self._args, **kwargs)

    def __le__(self, other):
        kwargs = self._kwargs.copy()
        kwargs['chk'] = ('le', other)
        return type(self)(self._name, *self._args, **kwargs)

    def __gt__(self, other):
        kwargs = self._kwargs.copy()
        kwargs['chk'] = ('gt', other)
        return type(self)(self._name, *self._args, **kwargs)
        
    def __ge__(self, other):
        kwargs = self._kwargs.copy()
        kwargs['chk'] = ('ge', other)
        return type(self)(self._name, *self._args, **kwargs)

    def __ne__(self, other):
        args = self._args.copy()
        kwargs = self._kwargs.copy()
        kwargs['chk'] = ('ne', other)
        return type(self)(self._name, *self._args, **kwargs)

    def __add__(self, other):
        self._raise_on_operand()
        kwargs = self._kwargs.copy()
        kwargs['ops'].append(('add', other))
        return type(self)(self._name, *self._args, **kwargs)

    def __sub__(self, other):
        self._raise_on_operand()
        kwargs = self._kwargs.copy()
        kwargs['ops'].append(('sub', other))
        return type(self)(self._name, *self._args, **kwargs)

    def __mul__(self, other):
        self._raise_on_operand()
        kwargs = self._kwargs.copy()
        kwargs['ops'].append(('mull', other))
        return type(self)(self._name, *self._args, **kwargs)

    def __div__(self, other):
        self._raise_on_operand()
        kwargs = self._kwargs.copy()
        kwargs['ops'].append(("div", other))
        return type(self)(self._name, *self._args, **kwargs)

    def __radd__(self, other):
        self._raise_on_operand()
        kwargs = self._kwargs.copy()
        kwargs['ops'].insert(0, ("add", other))
        return type(self)(self._name, *self._args, **kwargs)

    def __rsub__(self, other):
        self._raise_on_operand()
        kwargs = self._kwargs.copy()
        kwargs['ops'].insert(0, ("sub", other))
        return type(self)(self._name, *self._args, **kwargs)

    def __rmul__(self, other):
        self._raise_on_operand()
        kwargs = self._kwargs.copy()
        kwargs['ops'].insert(0, ("mul", other))
        return type(self)(self._name, *self._args, **kwargs)

    def __rdiv__(self, other):
        self._raise_on_operand()
        kwargs = self._kwargs.copy()
        kwargs['ops'].insert(0, ("div", other))
        return type(self)(self._name, *self._args, **kwargs)

    def __call__(self, *args, **kwargs):
        pass

    def __str__(self):
        d: list = self._kwargs['ops']
        e: tuple = self._kwargs['chk']
        if d[0] == _null and e[1] == _null:
            return f"{self._name}"
        rt0 = _translate_chks(e, self._name, return_basic=True if len(d) > 1 else False)
        rt1 = _translate_operands(d, _null, ('null', self._name if e[1] != _null and len(d) <= 1 else e[1]), pure=True)
        print(len(d), d)
        return self._reversed.get(type(self).__name__.lower(), '') + ' ' + rt0 + rt1[1:]
    
    def __repr__(self):
        return str(self)

class where(BaseSTMT):
    def __str__(self):
        d: list = self._kwargs['ops']
        e: tuple = self._kwargs['chk']
        if d[0] == _null and e[1] == _null:
            return f"{self._name}"
        rt0 = _translate_chks(e, self._name, return_basic=True if len(d) > 1 else False)
        rt1 = _translate_operands(d, _null, ('null', self._name if e[1] != _null and len(d) <= 1 else e[1]), pure=True)
        print(len(d), d)
        return 'WHERE ' + rt0 + rt1[1:]

class BaseCommand(BaseSTMT, name='void'): 
    """Base class for command"""
    # NOTE: Where is marked as non-command
    def __init__(self, reference, *args):
        """init"""
        super().__init__(reference, *args, no_operand=True)

    def __call__(self, *args):
        pass

    def __str__(self):
        return f"{self._reversed[type(self)]} {self._name}"
