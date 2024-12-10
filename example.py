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
                ).val_if_none('-').to_special()

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
