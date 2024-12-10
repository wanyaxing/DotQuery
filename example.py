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
    
    # 如果不传参数，.sql中的@default中的默认参数就会生效
    today_user2 = dq.today_user()
    print("最后注册时间　　:{:>10}".format(today_user.最后注册时间))
    print("是否包含最新用户　　:{:>10}".format(today_user.是否包含最新用户))
