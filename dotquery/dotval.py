import re
from . import dottool
import decimal


class DotVal:
    _value = None
    _default = None
    _raiseIfNone = None
    _digits = None
    _suffix = ""
    _prefix = None
    _isspecial = False

    def __init__(self, value):
        self._value = value

    # 自定义浅拷贝逻辑
    def copy(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    # 魔法方法，核心方法，当打印数据时调用此处
    def __str__(self):
        return f"{self}"

    # 魔法方法，核心方法，当格式化文本时调用此处
    def __format__(self, format_spec=None):
        _value = self.value()

        if dottool.is_numeric(_value) and not isinstance(_value,(int)):
            if self._digits is not None:
                rounded_num = round(float(_value), self._digits)
                _value = f"{rounded_num:.{self._digits}f}"
            elif self._isspecial:
                if 99 < abs(float(_value)) < 100 or 0 < abs(float(_value)) < 1:
                    rounded_num = round(float(_value), 1)
                    _value = f"{rounded_num:.1f}"
                else:
                    rounded_num = round(float(_value), 0)
                    _value = f"{rounded_num:.0f}"

        _value = f"{_value}{self._suffix}"

        if self._prefix is not None and _value[0:1] != "-":
            _value = f"{self._prefix}{_value}"

        return _value.__format__(format_spec)

    def value(self, default=None):
        if self._value is None:
            if default is not None:
                return default
            elif self._default is not None:
                return self._default
            elif self._raiseIfNone is not None:
                raise ValueError(self._raiseIfNone)
        return self._value

    def number(self, default=None):
        num = self.value()
        if not dottool.is_numeric(num):
            if num=='-':
                return 0
            else:
                raise ValueError('此处无法取到数字值')
        return num

    # ------------异常处理------------

    # 如果值为None则可以指定默认值
    def vin(self, default):
        self._default = default
        return self

    # 同上
    def val_if_none(self, default):
        return self.vin(default)

    # 如果值为None且没有默认值，则输出异常
    def rin(self, raiseIfNone):
        self._raiseIfNone = raiseIfNone
        return self

    # 同上
    def raise_if_none(self, raiseIfNone):
        return self.rin(raiseIfNone)

    # ------------值转化------------

    # 注意，以下数学计算不考虑值本身的类型，所以在使用时，请考虑这一点。
    # 比如，如果值为字符类型的话，再翻倍，就是字符重复效果了。

    # 加法
    def plus(self, num):
        if type(self.number())==type(num) or isinstance(num,int):
            self._value = self.number() + num
        elif isinstance(num,DotVal):
            self._value = self.number() + num.number()
        else:
            self._value = decimal.Decimal(f"{self.number()}") + decimal.Decimal(f"{num}")
        return self

    # 减法
    def minus(self, num):
        if type(self.number())==type(num) or isinstance(num,int):
            self._value = self.number() - num
        elif isinstance(num,DotVal):
            self._value = self.number() - num.number()
        else:
            self._value = decimal.Decimal(f"{self.number()}") - decimal.Decimal(f"{num}")
        return self

    # 乘法
    def times(self, num):
        if type(self.number())==type(num) or isinstance(num,int):
            self._value = self.number() * num
        elif isinstance(num,DotVal):
            self._value = self.number() * num.number()
        else:
            self._value = decimal.Decimal(f"{self.number()}") * decimal.Decimal(f"{num}")
        return self

    # 除法
    def div(self, num):
        if not dottool.is_numeric(num):
            self._value = None
            return self.raise_if_none("错误：分母非数字")
        elif float(f"{num}") == 0:
            self._value = None
            return self.raise_if_none("错误：分母不可为0")
        else:
            if type(self.number())==type(num) or isinstance(num,int):
                self._value = self.number() / num
            elif isinstance(num,DotVal):
                self._value = self.number() / num.number()
            else:
                self._value = decimal.Decimal(f"{self.number()}") / decimal.Decimal(f"{num}")
        return self

    # 取模
    def mod(self, num):
        if type(self.number())==type(num) or isinstance(num,int):
            self._value = self.number() % num
        elif isinstance(num,DotVal):
            self._value = self.number() % num.number()
        else:
            self._value = decimal.Decimal(f"{self.number()}") % decimal.Decimal(f"{num}")
        return self

    # 取幂
    def pow(self, num):
        if type(self.number())==type(num) or isinstance(num,int):
            self._value = self.number() ** num
        elif isinstance(num,DotVal):
            self._value = self.number() ** num.number()
        else:
            self._value = decimal.Decimal(f"{self.number()}") ** decimal.Decimal(f"{num}")
        return self

    # -------------魔术算数------------
    # 注意：魔术算数不会更改原本的值，会返回新的值

    # 加法
    def __add__(self, num):
        return self.copy().plus(num)

    # 减法
    def __sub__(self, num):
        return self.copy().minus(num)

    # 乘法
    def __mul__(self, num):
        return self.copy().times(num)

    # 除法
    def __truediv__(self, num):
        return self.copy().div(num)

    # 取模
    def __mod__(self, num):
        return self.copy().mod(num)

    # 取幂
    def __pow__(self, num):
        return self.copy().pow(num)

    # -------------值处理------------

    # 占比
    # CONCAT(ROUND(分子/分母*100,2),'%')
    def rateof(self, target, suffix="%"):
        if (
            target is None
            or not dottool.is_numeric(f"{target}")
            or float(f"{target}") == 0
        ):
            return DotVal("-")
        return self.copy().div(target).times(100).suffix(suffix)

    # 环比（差值占比）
    def diffof(self, target):
        return (self - target).rateof(target).prefix("+")

    # 字符截取
    # 注意，此处返回的是字符串
    def substr(self, start, length):
        self._value = f"${self._value}"[start : start + length]
        return self

    # -------------值判断------------
    # 注意，此处返回结果为终态，不可以继续点语法

    # 长度
    def length(self):
        return len(f"${self._value}")

    # 查找包含其他字符的位置
    def indexof(self, substring, start=0):
        return f"${self._value}".find(substring, start)

    # 比较 <
    def __lt__(self, num):
        return self._value < float(f"{num}")

    # 比较 <=
    def __le__(self, num):
        return self._value <= float(f"{num}")

    # 比较 >
    def __gt__(self, num):
        return self._value > float(f"{num}")

    # 比较 >=
    def __ge__(self, num):
        return self._value >= float(f"{num}")

    # 比较 ==
    def __eq__(self, num):
        return self._value == float(f"{num}")

    # 比较 !=
    def __ne__(self, num):
        return self._value != float(f"{num}")

    # -------------打印处理------------

    # 打印数据时，将保留若干小数位，
    def to_fixed(self, digits=None):
        self._isspecial = None
        self._digits = digits
        return self

    # 打印数据时，将根据数值动态决定小数点（如果>99or<1则取1位，否则0位）
    def to_special(self, isspecial=True):
        if isspecial:
            self._digits = None
        self._isspecial = isspecial
        return self

    # 打印数据时，追加后缀字符
    def suffix(self, suffix=""):
        self._suffix = f"{suffix}"
        return self

    # 打印数字时，如果数字非负数，则追加前缀字符
    def prefix(self, prefix=""):
        self._prefix = f"{prefix}"
        return self
