import os
from .dotres import DotRes
from . import dottool
import time


class DotExec:
    _conn = None
    _method = None
    _sqls_path = None
    _default = None
    _digits = None
    _isspecial = False

    def __init__(self, conn, method, sqls_path):
        self._conn = conn
        self._method = method
        self._sqls_path = sqls_path

    # 执行方法获得SQL并查询结果
    def run(self, *args, **kwargs):
        if type(self._method) is str:
            _result = self._sql_prepare(*args, **kwargs)
            # print(_result) # debug of sql
        else:
            try:
                print("({:<30})".format(f'{args}'+f'{kwargs}'), end="", flush=True)
                _result = self._method(*args, **kwargs)
            except ImportError:
                raise ValueError(f"DotExec: try to run method failed.")
        if type(_result) is tuple:
            return self.query(_result[0], _result[1])
        else:
            return self.query(_result)

    # SQL可以进行二次处理
    def _sql_prepare(self, *args, **kwargs):
        if os.path.exists(self._method):
            with open(self._method, "r", encoding="utf-8") as f:
                sql = f.read()
        else:
            sql = self._method

        params = {}
        defaultstr = dottool.paramat_get(sql, "default")
        if defaultstr is not None:
            params = {
                item.split("=")[0]: item.split("=")[1] for item in defaultstr.split("&")
            }

        for arg in args:
            if type(arg) is dict:
                params.update(arg)
            elif type(arg) is str:
                params.update(
                    {item.split("=")[0]: item.split("=")[1] for item in arg.split("&")}
                )
        params.update(kwargs)

        print("({:<30})".format(f'{params}'), end="", flush=True)

        return dottool.replace_and_tuple(sql, params, self._sqls_path)

    # 返回的结果中，取第一条
    def query_single(self, sql):
        res = self.query(sql)
        if len(res) > 0:
            return res[0]
        return None

    # 将查询的结果包装成DotRes的数组
    def query(self, sql, params=None):
        start_time = time.time()
        print(" ... ", end="", flush=True)
        cursor = self._conn.cursor()
        cursor.execute(sql, params)
        column_names = [description[0] for description in cursor.description]
        res = []
        for row in cursor.fetchall():
            row_dict = dict(zip(column_names, row))
            # res.append(DotRes(row_dict).val_if_none(self._default))
            res.append(row_dict)
        cursor.close()
        print("耗时:{:.2f}秒".format(time.time() - start_time))
        return (
            DotRes(res)
            .val_if_none(self._default)
            .to_fixed(self._digits)
            .to_special(self._isspecial)
        )

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
