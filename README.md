## DotQuery

python下的数据查询高效工具，通过包装sql查询结果对象，支持点语法进行数据键值的快速查询和输出，提高数据查询和开发效率。

通常用于单脚本场景的数据查询，不建议用于公开对外的业务场景。

简单的说，就是化身sql boy，无脑写SQL即可。

## 安装与使用
1. 直接将本包`dotquery`置于python项目下，在脚本中import
2. 通过DotQuery方法初始化数据库连接以及指定sqls所在目录
3. 在sqls目录中根据业务场景进行sql编写，并保存为函数同名文件
4. 在脚本中，通过dq.xxx(参数)执行对应数据查询，获得查询结果
5. 根据业务需求，直接通过 `result.字段` 的方式使用目标字段，

> 注1：也可以支持`result.字段一.plus(result.字段二)`这样的更多预置的 .方法 来进行数字或字符的二次处理。

> 注2：是的，根据自己的喜好，字段名可以直接是中文。


## 示例

example.py
```python
import os
from dotquery import DotQuery


if __name__ == '__main__':
    dq = DotQuery(
                 host='127.0.0.1'
                ,user='root'
                ,passwd='123456'
                ,port=3306
                ,db='test'
                ,charset='utf8'
                ,sqls_path=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./sqls/"))
                ).val_if_none('-') # 在后续使用过程中，如果调用到不存在的字段，则使用默认值-

    user_count=dq.user_count('2024-12-07')

    print(f"最后注册时间:{user_count.最后注册时间}")
    print(f"新注册用户:{user_count.新注册用户}")
    print(f"新注册用户两倍数:{user_count.新注册用户.times(2)}")
    print(f"男性用户:{user_count.男性用户}")
    print(f"男性用户占比:{user_count.男性用户.rateof(user_count.新注册用户)}")
    print(f"女性用户:{user_count.女性用户}")
    print(f"女性用户/男性用户:{(user_count.女性用户 / user_count.男性用户).to_fixed(1)}")
    print(f"女性用户/(女性用户+男性用户):{(user_count.女性用户/(user_count.女性用户 + user_count.男性用户)).times(100).to_fixed(1).suffix('%')}")
    print(f"不存在用户:{user_count.不存在用户}")
    print(f"不存在用户二:{user_count.不存在用户二.vin('?')}")

    user_count2=dq.user_count('2024-12-08')
    print(f"最后注册时间:{user_count2.最后注册时间}")
    print(f"环比前日:{user_count2.新注册用户.minus(user_count.新注册用户).prefix('+').to_fixed(0)}")
```

打印结果：
```
最后注册时间:2024-12-07 15:37:58
新注册用户:4
新注册用户两倍数:8.0
男性用户:3
男性用户占比:75.00%
女性用户:1
女性用户/男性用户:0.3
女性用户/(女性用户+男性用户):25.0%
不存在用户:-
不存在用户二:?
最后注册时间:2024-12-08 15:37:58
环比前日:+2
```

文件布局：
```
----------
|-dotquery/
|  |-dotquery.py
|  |-...
|-sqls/
|  |-user_count.py
|-example.py
```

sql举例：
sqls/user_count.py
```python
# 使用与.py文件同名的函数，返回结果为sql字符 用于直接查询数据 或 sql,params 用于参数化查询
# 示例中使用字符拼接的方式获得SQL，是存在注入隐患的，请根据业务场景自行合理实现。
def user_count(target_day):
    return f"""
SELECT
     COUNT(1) AS `新注册用户`
    ,COUNT(IF(`gender`='MALE',1,NULL)) AS `男性用户`
    ,COUNT(IF(`gender`='FEMALE',1,NULL)) AS `女性用户`
    ,MAX(`create_time`) AS `最后注册时间`
FROM user
WHERE `create_time` BETWEEN '{target_day}' AND '{target_day} 23:59:59'
"""
```


> 更多示例详见example.py或源代码


## todo

    √ 基础功能：实现自动关联执行sql脚本、支持查询结果对象的若干点语法（基础的数学计算、转换、判断能力
    □ 支持数据导出为csv/excel/html
    □ 支持数据流式查询和处理
    □ ...


## 其他说明
数据库操作类使用的是 pymysql


## License

MIT

