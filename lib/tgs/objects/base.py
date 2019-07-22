import enum
import inspect
from ..utils.nvector import NVector


class Tgs:
    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def load(cls, lottiedict):
        raise NotImplementedError


class TgsEnum(Tgs, enum.Enum):
    def to_dict(self):
        return self.value

    @classmethod
    def load(cls, lottieint):
        return cls(lottieint)


class PseudoList:
    pass


class TgsConverter:
    def __init__(self, py, lottie, name=None):
        self.py = py
        self.lottie = lottie
        self.name = name or "%s but displayed as %s" % (self.py.__name__, self.lottie.__name__)

    def py_to_lottie(self, val):
        return self.lottie(val)

    def lottie_to_py(self, val):
        return self.py(val)

    @property
    def __name__(self):
        return self.name


PseudoBool = TgsConverter(bool, int, "0-1 int")


class TgsProp:
    def __init__(self, name, lottie, type=float, list=False, cond=None):
        self.name = name
        self.lottie = lottie
        self.type = type
        self.list = list
        self.cond = cond

    def get(self, obj):
        return getattr(obj, self.name)

    def set(self, obj, value):
        return setattr(obj, self.name, value)

    def load_from_parent(self, lottiedict):
        if self.lottie in lottiedict:
            return self.load(lottiedict[self.lottie])
        return None

    def load_into(self, lottiedict, obj):
        if self.cond and not self.cond(lottiedict):
            return
        self.set(obj, self.load_from_parent(lottiedict))

    def load(self, lottieval):
        if self.list is PseudoList and isinstance(lottieval, list):
            return self.load_scalar(lottieval[0])
        elif self.list is True:
            return [
                self.load_scalar(it)
                for it in lottieval
            ]
        return self.load_scalar(lottieval)

    def load_scalar(self, lottieval):
        if inspect.isclass(self.type) and issubclass(self.type, Tgs):
            return self.type.load(lottieval)
        elif isinstance(self.type, type) and isinstance(lottieval, self.type):
            return lottieval
        elif isinstance(self.type, TgsConverter):
            return self.type.lottie_to_py(lottieval)
        elif self.type is NVector:
            return NVector(*lottieval)
        return self.type(lottieval)

    def to_dict(self, obj):
        val = self.basic_to_dict(self.get(obj))
        if self.list is PseudoList:
            val = [val]
        elif isinstance(self.type, TgsConverter):
            val = self.basic_to_dict(self.type.py_to_lottie(val))
        return val

    def basic_to_dict(self, v):
        if isinstance(v, Tgs):
            return v.to_dict()
        elif isinstance(v, NVector):
            return list(map(self.basic_to_dict, v.components))
        elif isinstance(v, list):
            return list(map(self.basic_to_dict, v))
        elif isinstance(v, (int, str, bool)):
            return v
        elif isinstance(v, float):
            if v % 1 == 0:
                return int(v)
            return round(v, 3)
        else:
            raise Exception("Unknown value %r" % v)

    def __repr__(self):
        return "<TgsProp %s:%s>" % (self.name, self.lottie)


class TgsObject(Tgs):
    def to_dict(self):
        return {
            prop.lottie: prop.to_dict(self)
            for prop in self._props
            if prop.get(self) is not None
        }

    @classmethod
    def load(cls, lottiedict):
        obj = cls()
        for prop in cls._props:
            prop.load_into(lottiedict, obj)
        return obj

    def find(self, search, propname="name"):
        if getattr(self, propname, None) == search:
            return self
        for prop in self._props:
            v = prop.get(self)
            if isinstance(v, TgsObject):
                found = v.find(search, propname)
                if found:
                    return found
            elif isinstance(v, list) and v and isinstance(v[0], TgsObject):
                for obj in v:
                    found = obj.find(search, propname)
                    if found:
                        return found
        return None


class Index:
    def __init__(self):
            self._i = -1

    def __next__(self):
            self._i += 1
            return self._i


def todo_func(x):
    raise NotImplementedError()
