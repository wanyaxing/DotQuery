import os
import re
import datetime


def paramat_getall(s, key, default=[]):
    pattern = re.compile(f"--\s*?@{key}\s+(.*)")
    matches = re.findall(pattern, s)
    if len(matches) > 0:
        return matches
    return default


def paramat_get(s, key="", default=None):
    matches = paramat_getall(s, key, [])
    if len(matches) > 0:
        return matches[0]
    return default


def replace_and_tuple(sql, params={}, sqls_path=None):
    new_sql = str(sql)
    new_sql = _params_replace(new_sql, params)

    if sqls_path is not None:
        new_sql = _part_replace(new_sql, sqls_path)

    new_sql = _params_replace(new_sql, params)

    new_sql = _constant_replace(new_sql)

    # 反向释放注释
    new_sql = re.sub(
        "/\*\[if ![^>]*?\]>(((?!\[if)[\s\S])*?)<\!\[endif\]\*/", "\g<1>", new_sql
    )
    # 移除其他注释
    new_sql = re.sub(
        "/\*\[if [^>]*?\]>(((?!\[if)[\s\S])*?)<\!\[endif\]\*/", "", new_sql
    )
    new_sql = re.sub(
        "/\*\[if [^>]*?\]>(((?!\[if)[\s\S])*?)<\!\[endif\]\*/", "", new_sql
    )
    new_sql = re.sub(
        "/\*\[if [^>]*?\]>(((?!\[if)[\s\S])*?)<\!\[endif\]\*/", "", new_sql
    )
    new_sql = re.sub(
        "/\*\[elif [^>]*?\]>(((?!\[if)[\s\S])*?)<\!\[endif\]\*/", "", new_sql
    )

    return new_sql
    # pattern = r"\$\{(.*?)\}"
    # matches = re.findall(pattern, sql)
    # if not matches:
    #     return sql, ()

    # new_sql = sql
    # args = []
    # for match in matches:
    #     if match in params:
    #       new_sql = new_sql.replace(f"${{{match}}}", "%s")
    #       args.append(params[match])
    # return new_sql, tuple(args)


def _part_replace(sql, sqls_path):
    if not os.path.exists(sqls_path):
        raise ValueError(f"sqls_path not found.")

    pattern = r"\$<(.*?)>"
    matches = re.findall(pattern, sql)
    if not matches:
        return sql

    new_sql = sql
    args = []
    for match in matches:
        part_path = f"{sqls_path}/{match}.part.sql"
        if os.path.exists(part_path):
            with open(part_path, "r", encoding="utf-8") as f:
                part = f.read()
                new_sql = new_sql.replace(f"$<{match}>", part)
    return new_sql


def _params_replace(sql, params={}):
    new_sql = sql
    for key, value in params.items():
        value = _constant_replace(str(value))
        new_sql = new_sql.replace(f"${{{key}}}", value)
        if f"{value}" != "0":
            new_sql = re.sub(
                f"/\*\[if {key}\]>(((?!\[if)[\s\S])*?)<\!\[endif\]\*/",
                "\g<1>",
                new_sql,
            )
            new_sql = re.sub(
                f"/\*\[if !{key}\]>(((?!\[if)[\s\S])*?)<\!\[endif\]\*/", "", new_sql
            )

            def callback(match):
                is_valid = True
                if match.group(1) == "(":
                    if is_valid and (
                        not match.group(2)
                        or match.group(2) == "-∞"
                        or (
                            is_numeric(value, match.group(2))
                            and float(f"{value}") > float(match.group(2))
                        )
                    ):
                        is_valid = True
                    else:
                        is_valid = False
                elif match.group(1) == "[":
                    if is_valid and (
                        not match.group(2)
                        or match.group(2) == "-∞"
                        or (
                            is_numeric(value, match.group(2))
                            and float(f"{value}") > float(match.group(2))
                        )
                        or f"{value}" == match.group(2)
                    ):
                        is_valid = True
                    else:
                        is_valid = False
                if match.group(4) == ")":
                    if is_valid and (
                        not match.group(3)
                        or match.group(3) == "-∞"
                        or (
                            is_numeric(value, match.group(3))
                            and float(f"{value}") < float(match.group(3))
                        )
                    ):
                        is_valid = True
                    else:
                        is_valid = False
                elif match.group(1) == "]":
                    if is_valid and (
                        not match.group(3)
                        or match.group(3) == "-∞"
                        or (
                            is_numeric(value, match.group(3))
                            and float(f"{value}") < float(match.group(3))
                        )
                        or f"{value}" == match.group(3)
                    ):
                        is_valid = True
                    else:
                        return False
                if is_valid:
                    return match.group(5)
                else:
                    return ""

            new_sql = re.sub(
                f"/\*\[elif {key}([\[\(])(.*?),(.*?)([\]\)])\]>(((?!\[if)[\s\S])*?)<\!\[endif\]\*/",
                callback,
                new_sql,
            )
    return new_sql


def _constant_replace(sql):
    if not re.search("\$\[.*\]", sql):
        return sql

    new_sql = sql

    today = datetime.datetime.now()
    new_sql = new_sql.replace("$[CURRENT_DATE]", today.strftime("%Y-%m-%d"))

    yesterday = today - datetime.timedelta(days=1)
    new_sql = new_sql.replace("$[YESTERDAY]", yesterday.strftime("%Y-%m-%d"))

    offset = 6 - today.weekday()
    sunday = today + datetime.timedelta(days=offset)
    new_sql = new_sql.replace("$[CURRENT_SUNDAY]", sunday.strftime("%Y-%m-%d"))

    year, month = today.year, today.month + 1
    if month > 12:
        year += 1
        month = 1
    next_month_first_day = datetime.date(year, month, 1)
    last_day_this_month = next_month_first_day - datetime.timedelta(days=1)
    new_sql = new_sql.replace(
        "$[CURRENT_MONTHENDDAY]", last_day_this_month.strftime("%Y-%m-%d")
    )

    return new_sql


def is_numeric(*args):
    for s in args:
        # 判断是否只包含数字、小数点和负号
        if not re.match(r"^[-+]?\d*\.?\d+$", f"{s}"):
            return False
    return True
