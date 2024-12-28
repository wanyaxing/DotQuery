import os
import importlib.util
import pymysql
from .dotexec import DotExec


# 用于动态加载当前包下其他文件代码中的query方法
class DotQuery:
    _conn = None
    _sqls_path = None
    _default = None
    _digits = None
    _isspecial = False

    # 初始化时，需要初始化pymysql连接以及指定一个.py的根目录
    # 然后就可以使用.xxx(a,b)的方式执行同名.py下的同名方法获取SQL并查询返回结果了
    # 举例: dq=DotQuery(....);print(dq.user_count('shanghai').C新增.toFixed(2))
    def __init__(self, host, user, passwd, port, db, charset="utf8", sqls_path=None):
        if not os.path.exists(sqls_path):
            raise ValueError(f"sqls_path not found.")
        self._sqls_path = sqls_path

        self._conn = pymysql.connect(
            host=host, user=user, passwd=passwd, port=port, db=db, charset=charset
        )

    # 自定义浅拷贝逻辑
    def copy(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result


    def __getattr__(self, method_name):
        print('开始处理：{:<30}'.format(method_name), end="", flush=True)
        if os.path.exists(f"{self._sqls_path}/{method_name}.py"):
            return self._get_model_method(method_name)
        elif os.path.exists(f"{self._sqls_path}/{method_name}.sql"):
            return self._get_sql_method(method_name)
        elif os.path.isdir(f"{self._sqls_path}/{method_name}"):
            return self._get_dir_method(method_name)
        else:
            raise ValueError(f"{method_name} 无法识别.")

    def _get_model_method(self, method_name):
        # 动态导入文件.py模块
        try:
            spec = importlib.util.spec_from_file_location(
                method_name, f"{self._sqls_path}/{method_name}.py"
            )
            target_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(target_module)
        except ImportError:
            raise ValueError(f"Module '{method_name}' not found in '{self._sqls_path}'")

        # 取出文件中的同名方法
        try:
            target_method = getattr(target_module, method_name)
        except AttributeError:
            raise ValueError(
                f"Method '{method_name}' not found in '{self._sqls_path}/{method_name}.py'"
            )

        # 包装成DotExec对象的run方法（注意，不是run()，所以当执行时，等同于执行run)
        return (
            DotExec(self._conn, target_method, self._sqls_path)
            .val_if_none(self._default)
            .to_fixed(self._digits)
            .to_special(self._isspecial)
            .run
        )

    def _get_sql_method(self, method_name):
        # 包装成DotExec对象的run方法（注意，不是run()，所以当执行时，等同于执行run)
        return (
            DotExec(self._conn, f"{self._sqls_path}/{method_name}.sql", self._sqls_path)
            .val_if_none(self._default)
            .to_fixed(self._digits)
            .to_special(self._isspecial)
            .run
        )

    def _get_dir_method(self, method_name):
        # 包装成DotExec对象的run方法（注意，不是run()，所以当执行时，等同于执行run)
        newdq = self.copy()
        newdq._sqls_path = f"{self._sqls_path}/{method_name}"
        return newdq

    # 指定vin值，当查询结果的DotDict被外界调用时，此处可以指定默认值
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
