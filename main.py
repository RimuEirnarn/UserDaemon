#!/usr/local/bin/python3.9
from typing import Any, Union
from db3 import User, Session, get_mode as gmode, get_user_by_name, init_db, Mode, get_user_by_id, push_user_by_id, push_user_by_name
from pwd import getpwnam, getpwuid
from argh import ArghParser, arg
from os import getuid
from functools import lru_cache

_debug = True

# Need to be replaced

def _cast(data) -> Union[int, Any]:
    try:
        return int(data)
    except Exception:
        pass
    return data

def _ParseArgs(func):
    @lru_cache
    def wrapper(*args, **kwargs):
        args = [_cast(a) for a in args]
        kwargs = {a:_cast(b) for a,b in kwargs.items()}
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

# ===


@_ParseArgs # ???
def setMode(uid: int, mid: int):
    global Session
    with Session.begin() as s:
        mode = s.query(Mode).filter(Mode.mid == mid).first()
        if mode is None:
            raise Exception(f"Mode id {mid} is not found.")
        user = s.query(User).filter(User.uid == uid).first()
        if user is None:
            try:
                pw = getpwuid(uid)
            except Exception as exc:
                raise exc from None
            user = User(uid=uid, name=pw.nam, gecos=pw.gecos, mode_id=0)
            s.add(user)

        s.query(User).filter(User.uid == uid).update({'mode_id': mid})
    return True

def getModeFromUser(user: Union[str, int]) -> int:
    global Session
    if not isinstance(user, (str, int)):
        with Session.begin() as s:
            data = s.query(User).filter(User.name == user if isinstance(user, str) else User.uid == user).first()
            if data is None:
                raise Exception(f"User {user} not found")
            return data.mode_id
    raise Exception(f"Unknown data of {user}")

@_ParseArgs
def set_mode(user, mode):
    global Session
    if isinstance(user, int):
        user = get_user_by_id(user)
    if isinstance(mode, (int, str)):
        mode = gmode(mode)
    if isinstance(user, str):
        user = get_user_by_name(user)

    if mode is None or user is None:
        raise Exception("Either mode or user is not found.")
    with Session.begin() as s:
        s.query(User).filter(User.uid == User.uid).update(dict(mode_id=mode.mid))
    print(get_user_by_name(user.name))

@_ParseArgs
def create_mode(name: str, wallmsg: str):
    global Session
    with Session.begin() as s:
        mode = Mode(name=name, wallmsg=wallmsg)
        s.add(mode)
        mid = s.query(Mode).filter(Mode.name == name).first().mid
        return mid

@_ParseArgs
def delete_mode(mode: Union[str, int]):
    global Session
    if not isinstance(mode, (str, int)):
        raise TypeError("Type missmatch")
    with Session.begin() as s:
        return s.query(Mode).filter(Mode.mid == mode if isinstance(mode, int) else Mode.name == mode).delete(synchronize_session='evaluate')

@_ParseArgs
def getuser(user: Union[int, str]):
    global Session
    from pprint import pprint
    with Session.begin() as s:
        user_ = s.query(User).filter(User.uid == user if isinstance(user, int) else User.name == user).first()
        pprint((getpwnam(user) if isinstance(user, str) else getpwuid(user)) if user_ is None else user_)

@_ParseArgs
def adduser(user: Union[int, str]):
    if isinstance(user, int):
        return push_user_by_id(user)
    if isinstance(user, str):
        return push_user_by_name(user)

@_ParseArgs
def get_mode(mode: Union[str, int]):
    global Session
    with Session.begin() as s:
        mode_ = s.query(Mode).filter(Mode.mid == mode if isinstance(mode, int) else Mode.name == mode).first()
        if mode_ == None:
            return "Not Found"
        print(mode_)

if __name__ == '__main__':
    if _debug:
        engine, Session = init_db("sqlite://")
        push_user_by_id(500)
        create_mode("global.mode.PenilaianTengahSemester", "The user is on their tests.")
    else:
        if getuid() != 0:
            raise Exception("Only root can do this.")
        engine, Session = init_db("sqlite:///var/lib/userd/data.sqlite")
        try:
            push_user_by_id(500)
            create_mode("global.mode.PenilaianTengahSemester", "The user is on their tests.")
        except Exception:
            pass
    parser = ArghParser()
    parser.add_commands([delete_mode, create_mode, set_mode, getuser, adduser, get_mode])
    parser.dispatch()
