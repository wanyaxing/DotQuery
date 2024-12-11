-- @default target_day=$[CURRENT_DATE]
SELECT user.`id`,
    user.`gender` AS `性别`,
    IF(ULAST.`id` IS NOT NULL, 1, 0) AS `是否最新用户`,
    user.`create_time` AS `注册时间`
FROM user
    LEFT JOIN ($<user_last>) ULAST ON ULAST.`id` = user.`id`
WHERE `create_time` BETWEEN '${target_day}' AND '${target_day} 23:59:59'
    AND `create_time` <= DATE_ADD('$[CURRENT_DATE]', INTERVAL 1 DAY)
    /*[if target_day]>AND 1=1<![endif]*/
    /*[if !until_day]>AND 0=0<![endif]*/
    /*[elif gender[FEMALE,]]>AND `gender` = 'FEMALE'<![endif]*/
    /*[elif gender[MALE,]]>AND `gender` = 'MALE'<![endif]*/
