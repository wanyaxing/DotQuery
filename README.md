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


if __name__ == "__main__":
    dq = (
        DotQuery(
            host="127.0.0.1",
            user="root",
            passwd="123456",
            port=3306,
            db="test",
            charset="utf8",
            sqls_path=os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "./sqls/")
            ),
        )
        .val_if_none("-")
        .to_special()
    )

    user_count = dq.user_count("2024-12-07")

    print(f"最后注册时间:{user_count.最后注册时间}")
    print("新注册用户　　　:{:>10}".format(user_count.新注册用户))
    print("新注册用户两倍数:{:>10}".format(user_count.新注册用户.times(2)))
    print(
        "男性用户占比　　:{:>10}".format(
            user_count.男性用户.rateof(user_count.新注册用户)
        )
    )
    print(
        "女性用户/男性用户:{:>10}".format(
            (user_count.女性用户 / user_count.男性用户).to_fixed(1)
        )
    )
    print(
        f"女性用户/(女性用户+男性用户):{(user_count.女性用户/(user_count.女性用户 + user_count.男性用户)).times(100).to_fixed(1).suffix('%')}"
    )
    print("不存在用户　　　:{:>10}".format(user_count.不存在用户))
    print("不存在用户二　　:{:>10}".format(user_count.不存在用户二.vin("?")))

    user_count2 = dq.user_count("2024-12-08")
    print("最后注册时间　　:{:>10}".format(user_count2.最后注册时间))
    print(
        "环比前日　　　　:{:>10}".format(
            user_count2.新注册用户.diffof(user_count.新注册用户)
        )
    )

    # 支持.sql 以及支持传参进行替换（详见sqls/today_user.sql)
    today_user = dq.today_user({"target_day": "2024-12-10", "gender": "FEMALE"})
    print("最后注册时间　　:{:>10}".format(today_user.最后注册时间))
    print("是否包含最新用户　　:{:>10}".format(today_user.是否包含最新用户))

```

打印结果：
```
最后注册时间:2024-12-07 15:37:58
新注册用户　　　:         4
新注册用户两倍数:         8
男性用户占比　　:    75.00%
女性用户/男性用户:       0.3
女性用户/(女性用户+男性用户):25.0%
不存在用户　　　:         -
不存在用户二　　:         ?
最后注册时间　　:2024-12-08 15:37:58
环比前日　　　　:   +50.00%
最后注册时间　　:2024-12-10 14:45:05
是否包含最新用户　　:         1
```

文件布局：
```
----------
|-dotquery/
|  |-dotquery.py
|  |-...
|-sqls/
|  |-user_count.py
|  |-today_user.sql
|  |-user_last.part.sql
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

sqls/today_user.sql
```sql
SELECT COUNT(1) AS `新注册用户`,
    MAX(IF(ULAST.`id` IS NOT NULL,1,0)) AS `是否包含最新用户`,
    COUNT(IF(`gender` = 'MALE', 1, NULL)) AS `男性用户`,
    COUNT(IF(`gender` = 'FEMALE', 1, NULL)) AS `女性用户`,
    MAX(`create_time`) AS `最后注册时间`
FROM user
LEFT JOIN ($<user_last>) ULAST ON ULAST.`id`=user.`id`
WHERE `create_time` BETWEEN '${target_day}' AND '${target_day} 23:59:59'
    AND `create_time` <= DATE_ADD('$[CURRENT_DATE]', INTERVAL 1 DAY)
    /*[if target_day]>AND 1=1<![endif]*/
    /*[if !until_day]>AND 0=0<![endif]*/
    /*[elif gender[FEMALE,]]>AND `gender` = 'FEMALE'<![endif]*/
    /*[elif gender[MALE,]]>AND `gender` = 'MALE'<![endif]*/
```

> .part.sql是一个特殊的sql代码块，可以在其他sql中通过 $<filename> 来引入这部分代码，通常用于一些固定的临时表或条件语句等

> 注意：.part.sql并不需要完整SQL，可以是任意字符串，使用时为字符替换对应的$<filename>

sqls/user_last.part.sql
```sql
SELECT `id`
FROM user
WHERE 1=1
    /*[if target_day]>AND 1=1<![endif]*/
    /*[if !until_day]>AND 0=0<![endif]*/
    /*[elif gender[FEMALE,]]>AND `gender` = 'FEMALE'<![endif]*/
    /*[elif gender[MALE,]]>AND `gender` = 'MALE'<![endif]*/
ORDER BY `id` DESC
LIMIT 1
```

## 细节 
### DotQuery

| 初始化或方法 | 描述 |
| --: | :-- |
| DotQuery(host, user, passwd, port, db, charset="utf8", sqls_path=None) | 初始化一个dq实例，用于查询数据 |
|   |   |
| .example_method(arg1,arg2) | 可以请求sqls_path/下的example_method.py文件或example_method.sql文件中对应的SQL，返回值为DotRes实例 |
|   |   |
| :以下为穿透方法，会用于后续的DotVal实例，如果在此处指定值，后续就可以沿用了: |
| .val_if_none(default) |  |
| .to_fixed(digits=None) |  |
| .to_special(isspecial=True) |  |


### DotRes

| 初始化或方法 | 描述 |
| --: | :--: |
| DotRes(value=[]) | 初始化一个DotRes实例，通常用于包装list或dict类型的数据，DotRes实例的特性会接近dict |
|  |  |
| .items() | 同dict用法 |
| .keys() | 同dict用法 |
| .values() | 同dict用法 |
|  | :以下为穿透方法，会用于后续的DotVal实例，如果在此处指定值，后续就可以沿用了: |
| .val_if_none(default) |  |
| .to_fixed(digits=None) |  |
| .to_special(isspecial=True) |  |


### DotVal

| 初始化或方法 | 描述 |
| --: | :--: |
| DotVal(value=any) | 初始化一个DotVal实例，通常用于包装数字或字符的数据，之所以包装成DotVal是为了实现数据的二次或多次转化 |
|  |  |
| .items() | 同dict用法 |
| .keys() | 同dict用法 |
| .values() | 同dict用法 |
|  | :值处理: |
| .rateof(target) | 计算当前值与目标值的占比，相当于：分子/分母*100 |
| .diffof(target) | 计算当前值与目标值的环比，相当于：(self - target)/target*100 |
|  | :值计算: |
| .plus(num) | 在原值基础上-加法 |
| .minus(num) | 在原值基础上-减法 |
| .times(num) | 在原值基础上-乘法 |
| .div(num) | 在原值基础上-除法 |
| .mod(num) | 在原值基础上-取模 |
| .pow(num) | 在原值基础上-取幂 |
|  | :数学计算: |
| +、-、*、/、%、^ | 两个数之间进行数学计算，会产生一个新值 |
|  | :值判断: |
|  < 、<= 、> 、>= 、== 、!= | :值判断: |
|  .length() | 打印长度 |
|  .indexof(substring, start=0) | 寻找是否包含其他字符，返回对应的位置 |
|  | :打印时处理: |
| .val_if_none(default) | 如果value值为None则可以指定默认值 |
| .to_fixed(digits=None) | 打印数据时，将保留若干小数位， |
| .to_special(isspecial=True) | 打印数据时，将根据数值动态决定小数点（如果>99or<1则取1位，否则0位） |
| .suffix(suffix="") | 打印数据时，追加后缀字符 |
| .prefix(prefix="") | 打印数字时，如果数字且非负数，则追加前缀字符 |
| .raise_if_none(raiseIfNone='error') | 如果value值为None也没指定默认值，且指定了raiseIfNone则抛出异常 |




> 更多示例详见example.py或源代码


## todo

    √ 基础功能：实现自动关联执行sql脚本、支持查询结果对象的若干点语法（基础的数学计算、转换、判断能力以及more)
    ▣ 点语法：数学计算、数学符号、比较判断、字符匹配、前缀后缀、固定长度。。。
    √ 支持常量替换，如$[CURRENT_DATE]可以替换为当日日期等
    √ 支持变量替换，如${target_day}可以替换为参数的值
    √ 支持共用代码块替换，如$<user_last>可以替换为对应的代码块
    √ 支持.sql文件
    □ 支持请求API获得数据
    □ 支持多层嵌套的数据中进行路径搜索(通常用于API请求获得的JSON体)，如 result.find('order.price') 或 result.search('*.price')
    □ .sql文件支持变体，如神策请求
    □ 支持数据导出为csv/excel/html
    □ 支持数据流式查询和处理
    □ 支持写入数据
    □ 支持流式写入数据
    □ ...


## 其他说明
数据库操作类使用的是 pymysql


## License

MIT

