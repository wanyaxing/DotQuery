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
                    .val_if_none(self._default)
                    .to_fixed(self._digits)
                    .to_special(self._isspecial)
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

    # 支持遍历,仿list(即dict也是默认返回值集合，方便遍历，和dict本身行为不一样哦)
    def __iter__(self):
        return self.values()
        # if isinstance(self._value, list):
            # return self.values()
        # elif isinstance(self._value, dict):
        #     return self.keys()

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


    # 仿dict.update,但此处需要指定key，且只有key对应的值一致才会更新
    def update(self, values=[],key='id'):
        if isinstance(values, DotRes):
            values=values._value
        if isinstance(values, list):
            return self._update_with_key(values,key)
        elif isinstance(values, dict):
            return self._update_with_key([values],key)


    def _update_with_key(self, values=[],key='id'):
        for val in values:
            # if not isinstance(val, list):
            #     raise ValueError('此处只接受字典用于合并数据')
            # if key not in val:
            #     raise ValueError('未在待合并字典中找到对应的key')
            if isinstance(self._value, list):
                isupdated = False
                for i in range(len(self._value)):
                    if key in self._value[i] and self._value[i][key]==val[key]:
                        isupdated=True
                        self._value[i].update(val)
                if not isupdated:
                    self._value.append(val)
                    # todo 此处需考虑字段合并
            elif isinstance(self._value, dict):
                if self[key]==val[key]:
                    self._value.update(val)

    # 当值为数组时，指定其中的字典值进行排序
    def sort(self, key='id', reverse=False):
        if isinstance(self._value, list):
            self._value=sorted(self._value, key=lambda x: x[key] if key in x else 0, reverse=reverse)
            return self
        elif isinstance(self._value, dict):
            raise ValueError('此处只接受数组结果进行排序')

    # 将字典中的key值重命名，可以用 .rename('from','to') 或 .rename({'f1':'t1','f2':'t2'})
    def rename(self, *args):
        keylist = {}
        if len(args)==2 and isinstance(args[0], str) and isinstance(args[1], str):
            keylist[args[0]]=args[1]
        else:
            for arg in args:
                if type(arg) is dict:
                    keylist.update(arg)
        if isinstance(self._value, list):
            for i in range(len(self._value)):
                self._value[i]={keylist[old_key] if old_key in keylist else old_key: value for old_key, value in self._value[i].items()}
        elif isinstance(self._value, dict):
            self._value={keylist[old_key] if old_key in keylist else old_key: value for old_key, value in self._value.items()}
        return self


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
