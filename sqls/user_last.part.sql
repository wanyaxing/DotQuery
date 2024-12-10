SELECT `id`
FROM user
WHERE 1=1
    /*[if target_day]>AND 1=1<![endif]*/
    /*[if !until_day]>AND 0=0<![endif]*/
    /*[elif gender[FEMALE,]]>AND `gender` = 'FEMALE'<![endif]*/
    /*[elif gender[MALE,]]>AND `gender` = 'MALE'<![endif]*/
ORDER BY `id` DESC
LIMIT 1
