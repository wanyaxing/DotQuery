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
