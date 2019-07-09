import enum
import inspect


def _to_dict(v):
    if isinstance(v, Tgs):
        return v.to_dict()
    elif isinstance(v, bool):
        return int(v)
    elif isinstance(v, list):
        return list(map(_to_dict, v))
    elif isinstance(v, (int, float, str)):
        return v
    else:
        raise Exception("Unknown value %r" % v)


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
        if self.list:
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
        return self.type(lottieval)


class TgsObject(Tgs):
    def to_dict(self):
        return {
            prop.lottie: _to_dict(prop.get(self))
            for prop in self._props
            if prop.get(self) is not None
        }

    @classmethod
    def load(cls, lottiedict):
        obj = cls()
        for prop in cls._props:
            prop.load_into(lottiedict, obj)
        return obj


class Index:
    def __init__(self):
            self._i = -1

    def __next__(self):
            self._i += 1
            return self._i


def todo_func(x):
    raise NotImplementedError()