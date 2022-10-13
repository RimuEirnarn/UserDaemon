from typing import Iterable, Type, Union
from sqlalchemy import Column, ForeignKey, String, Integer, TypeDecorator, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine
from csv import reader, writer
from pwd import getpwnam, getpwuid
from io import StringIO

Base = declarative_base()
global_engine: Engine = None
Session: sessionmaker = None

def _return_keys(data: dict):
    x = {}
    for k,v in data.items():
        k: str = k
        if k.startswith('_'):
            continue
        x[k] = v
    return x

def AfterInit(func):
    def wrapper(*args, **kwargs):
        if global_engine is None or Session is None:
            raise Exception("Cannot start this function, the enine is not initialized with init_db")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

class CSV(TypeDecorator):
    """CSV"""

    impl = String

    cache_ok = True

    def process_bind_param(self, value: Iterable, dialect) -> str:
        io = StringIO()
        csvw = writer(io)
        csvw.writerow(value)
        return io.getvalue()

    def process_result_value(self, value, dialect) -> list:
        csvr = reader([value])
        return next(csvr)


class User(Base):
    __tablename__ = 'user'

    uid = Column(Integer, primary_key=True, unique=True)
    name =Column(String)
    gecos = Column(CSV)
    mode_id = Column(Integer, ForeignKey('mode.mid'))

    def __repr__(self):
        return f"<Linux-User(uid={self.uid}, name={self.name}, gecos={True if self.gecos else False}, mode={get_modename(self.mode_id)})>"

class Mode(Base):
    __tablename__ = 'mode'

    mid = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, unique=True)
    wallmsg = Column(String)

    def __repr__(self):
        return "<Mode %s (%s)>" % (self.mid, self.name)

class Containers(Base):
    __tablename__ = "containers"

    cid = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    path = Column(String)
    config = Column(CSV)

    def __repr__(self):
        return "<Mode %s (%s)>" % (self.mid, self.name)

def init_db(path, **kwargs):
    """kwargs option will be passed to create_engine"""
    global global_engine, Session
    if not global_engine:
        engine = create_engine(path, **kwargs)
        Base.metadata.create_all(engine)
        global_engine = engine
        Session = sessionmaker(engine)
        # We should add a null/default mode so that user-related addition not going to crash.
        with Session.begin() as s:
            null = s.query(Mode).filter(Mode.mid == 0).first()
            if null is None:
                m = Mode(mid=0, name="Default", wallmsg="")
                s.add(m)
            # This is for root user.
            root = s.query(User).filter(User.uid == 0).first()
            if root is None:
                pw = getpwuid(0)
                root = User(uid=0, name='root', gecos=pw.pw_gecos, mode_id=0)
                s.add(m)
        return engine, Session
    return global_engine, Session

def get_engine():
    return global_engine if global_engine else init_db("sqlite://")

def push_user_by_id(uid: int):
    global Session
    pw = getpwuid(uid)
    if pw.pw_shell.split('/')[-1] not in ('zsh', 'bash', 'csh', 'sh'):
        raise Exception("The user is a system or a user program. Try pass a real user.")
    with Session.begin() as s:
        user = User(uid=uid, name=pw.pw_name, gecos=pw.pw_gecos, mode_id=0)
        s.add(user, True)

def push_user_by_name(name: str):
    global Session
    pw = getpwnam(name)
    if pw.pw_shell.split('/')[-1] not in ('zsh', 'bash', 'csh', 'sh'):
        raise Exception("The user is a system or a user program. Try pass a real user.")
    with Session.begin() as s:
        user = User(uid=pw.pw_uid, name=name, gecos=pw.pw_gecos, mode_id=0)
        s.add(user, True)

def get_user_by_id(uid: int):
    global Session
    with Session.begin() as s:
        return User(**_return_keys(s.query(User).filter(User.uid == uid).first().__dict__))

def get_user_by_name(name: str):
    global Session
    with Session.begin() as s:
        return User(**_return_keys(s.query(User).filter(User.name == name).first().__dict__))

def get_mode(mode: Union[int, str]):
    global Session
    with Session.begin() as s:
        return Mode(**_return_keys(s.query(Mode).filter(Mode.mid == mode if isinstance(mode, int) else Mode.name == mode).first().__dict__))

def get_modename(mode: int):
    global Session
    with Session.begin() as s:
        return s.query(Mode).filter(Mode.mid == mode if isinstance(mode, int) else Mode.name == mode).first().name