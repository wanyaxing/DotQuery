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

    # user_count.py同名函数直接调用
    user_count = dq.user_count("2024-12-07")
    # user_count.py同名函数再次调用
    user_count2 = dq.user_count("2024-12-08")
    # today_user.sql 也能调用，支持传参进行SQL处理替换（详见sqls/today_user.sql)
    today_user = dq.today_user({"target_day": "2024-12-10", "gender": "FEMALE"})
    # 也可以直接单参指定
    today_user2 = dq.today_user(target_day="2024-12-07")
    # 也可以URL参数形式
    today_user3 = dq.today_user("target_day=2024-12-07&gender=FEMALE")
    # 甚至多种参数集合(直接指定参数优先级最高，其他两种参数按先后顺序，后者覆盖)
    today_user4 = dq.today_user(
        {"target_day": "2024-12-10"}, "gender=MALE", gender="FEMALE"
    )

    print(f"最后注册时间:{user_count.最后注册时间}")
    print("新注册用户　　　:{:>10}".format(user_count2.新注册用户))
    print("新注册用户两倍数:{:>10}".format(user_count.新注册用户.times(2)))
    print(
        "男性用户占比　　:{:>10}".format(
            user_count2.男性用户.rateof(user_count2.新注册用户)
        )
    )
    print(
        "女性用户/男性用户:{:>10}".format(
            (user_count2.女性用户 / user_count2.男性用户).to_fixed(1)
        )
    )
    print(
        f"女性用户/(女性用户+男性用户):{(user_count2.女性用户/(user_count2.女性用户 + user_count2.男性用户)).times(100).to_fixed(1).suffix('%')}"
    )
    print("不存在用户　　　:{:>10}".format(user_count.不存在用户))
    print("不存在用户二　　:{:>10}".format(user_count.不存在用户二.vin("?")))
    print(
        "环比前日　　　　:{:>10}".format(
            user_count2.新注册用户.diffof(user_count.新注册用户)
        )
    )
    print("是否包含最新用户　　:{:>10}".format(user_count.是否包含最新用户))
    print(
        "男性用户/新注册用户　　:{}|{}({})".format(
            user_count2.男性用户.div(user_count2.新注册用户),
            user_count2.男性用户.div(user_count2.新注册用户),
            user_count2.男性用户.div(user_count2.新注册用户).diffof(
                user_count2.男性用户.div(user_count2.新注册用户)
            ),
        )
    )

    print("today_user2的数量:{}".format(len(today_user2)))

    print("支持对结果DotRes对象进行遍历")
    for tkey in today_user2:
        print(tkey)
    for tidx, tkey in enumerate(today_user2):
        print(tidx, type(tkey))
    for tkey, tuser in today_user2.items():
        print(tkey, type(tuser))

    print("也支持给子对象进行遍历")
    for tkey in today_user2[0]:
        print(tkey)
    for tidx, tkey in enumerate(today_user2[0]):
        print(tidx, type(tkey))
    for tkey, tuser in today_user2[0].items():
        print(tkey, type(tuser))

    print("打印数据")
    for tkey, tuser in today_user2.items():
        for key in tuser:
            print(key, tuser[key])
        for key, value in tuser.items():
            print(key, value)
