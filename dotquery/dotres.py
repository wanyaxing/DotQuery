from .dotval import DotVal


# 特殊的结果包装对象
# 支持list和dict进行初始化
# 支持多层嵌套的list或dict
class DotRes:
    _value = None
    _default = None
    _digits = None
    _isspecial = False

    def __init__(self, value):
        self._value = value

    def __str__(self):
        return f"{self._value}"

    def __getitem__(self, key):
        if key in self._value or (
            isinstance(self._value, list) and (key in range(len(self._value)) or isinstance(key,slice))
        ):
            value = self._value[key]
        else:
            # 特殊用法，当对list取键时，可以穿透取到list的第一个数据里的键
            if isinstance(self._value, list) and len(self._value) > 0 and key in self._value[0]:
                value = self._value[0][key]
            else:
                return (
                    DotVal(None)
                    .raise_if_none(f" '{key}' not found")
                )
        if isinstance(value, dict) or isinstance(value, list):
            return (
                DotRes(value)
                .val_if_none(self._default)
                .to_fixed(self._digits)
                .to_special(self._isspecial)
            )
        return (
            DotVal(value)
            .val_if_none(self._default)
            .to_fixed(self._digits)
            .to_special(self._isspecial)
        )

    def __getattr__(self, key):
        return self[key]

    def __len__(self):
        return len(self._value)

    # 支持遍历
    # 统一效果，仿dict，即list遍历默认也是出index
    def __iter__(self):
        return self.keys()

    # 可以出key,value队
    def items(self):
        if isinstance(self._value, list):
            for i in range(len(self._value)):
                yield i, self[i]
        elif isinstance(self._value, dict):
            for key in self._value:
                yield key, self[key]

    def keys(self):
        if isinstance(self._value, list):
            for i in range(len(self._value)):
                yield i
        elif isinstance(self._value, dict):
            for key in self._value:
                yield key

    def values(self):
        if isinstance(self._value, list):
            for i in range(len(self._value)):
                yield self[i]
        elif isinstance(self._value, dict):
            for key in self._value:
                yield self[key]

    # 给当前对象下的对象，都指定默认值（包括错误调用（不含当前调用）））
    # 指定vin值，当查询结果的DotRes被外界调用时，此处可以指定默认值
    def val_if_none(self, default):
        self._default = default
        return self

    # 打印数据时，将保留若干小数位，
    def to_fixed(self, digits=None):
        self._digits = digits
        return self

    # 打印数据时，将根据数值动态决定小数点（如果>99or<1则取1位，否则0位）
    def to_special(self, isspecial=True):
        self._isspecial = isspecial
        return self
