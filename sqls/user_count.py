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
