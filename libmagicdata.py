from types import SimpleNamespace

class MagicalNamespace(SimpleNamespace):
    _id = {}
    def __new__(cls, getattr_f, setattr_f, *args, **kwargs):
        cls = object().__new__(cls)
        cls.__init__(*args, **kwargs)
        cls.__getattr__ = getattr_f
        cls.__setattr__ = setattr_f
        return cls
