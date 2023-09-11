# -*- coding: UTF-8 -*-
from time import sleep

import requests
import pymysql

mysql_host = "localhost"
mysql_user = "mywkyd"
mysql_password = "mywkyd"
mysql_database = "myWKYD"

# 这里的salt和sign要通过https://github.com/xmexg/wkyd_after/blob/main/apkmd5code/apkmd5code.jar计算得到
url = "http://sports.wfust.edu.cn/api/run/getRunInfo?salt=a42ccebb&sign=82d6a94c2239e73c4c23becdf43d1c04"
HEADERS = {"X-Re-Os": "android", "X-Re-Version": "13", "X-Re-Device": "Xiaomi M2023",
           "Content-Type": "application/json; charset=UTF-8", "Accept-Encoding": "gzip", "User-Agent": "okhttp/4.5.0"}


# 下载学校运动数据库
def request_sqlData(data_id):
    body = {"id": data_id}
    while True:
        try:
            response = requests.post(url, json=body, headers=HEADERS)
            return response.json()
        except requests.exceptions.ChunkedEncodingError:
            # 重新请求
            print(" ! 连接中断,5秒后重试")
            sleep(5)


# 当start_id为None时,从数据库中获取最大id,表clone_data,列data_id
def up_start_id(db):
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute() 方法执行 SQL
    cursor.execute("SELECT data_id FROM clone_data WHERE id = (SELECT MAX(id) FROM clone_data);")
    # 使用 fetchone() 方法获取单条数据.
    data = cursor.fetchone()
    # 当数据库中没有数据时,设置默认值
    if data is None:
        return 1881641
    return data[0] + 1


# 当数据库不存在时创建数据库
def create_table():
    # 打开数据库连接
    db = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database,
                         charset="utf8")
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # 使用 execute() 方法执行 SQL，如果表不存在则创建
    cursor.execute("create table if not exists `clone_data`(`id` INT UNSIGNED AUTO_INCREMENT, `res_code` varchar(4), "
                   "`data_id` MEDIUMINT, `data_userId` MEDIUMINT, `data_userCode` text, `data_semesterId` tinyint, "
                   "`data_campus` tinyint, `data_beginTime` varchar(20), `data_endTime` varchar(20), "
                   "`data_totalLength` MEDIUMINT, `data_trueLength` MEDIUMINT, `data_totalTime` MEDIUMINT, "
                   "`data_markList` LONGTEXT, `data_phoneInfo` TINYTEXT, `data_createTime` varchar(20), "
                   "`data_pageSize` tinytext, `data_pageNo` tinytext, `data_pageBegin` tinytext, primary key("
                   "`id`))ENGINE=InnoDB DEFAULT CHARSET=utf8;")


# 打开数据库连接,避免每次开启并关闭造成的资源浪费
def open_mysql():
    db = pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database,
                         charset="utf8")
    return db


def close_mysql(db):
    db.close()


# 连接本地数据库,并保存通过request_sqlData()拿到的数据,使用myWKYD数据库,clone_data表,mywkyd用户名,mywkyd密码
# 没有数据库则创建,表结构为展开后的json数据
def save_to_mysql(sql_data, db):
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # SQL 插入语句
    sql = "INSERT INTO clone_data(res_code, data_id, data_userId, data_userCode, data_semesterId, data_campus, " \
          "data_beginTime, data_endTime, data_totalLength, data_trueLength, data_totalTime, data_markList, " \
          "data_phoneInfo, data_createTime, data_pageSize, data_pageNo, data_pageBegin) VALUES (%s, %s, %s, %s, %s, " \
          "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    if sql_data["data"] is None:
        return -1
    # 执行sql语句
    cursor.execute(sql, (
        sql_data["code"], sql_data["data"]["id"], sql_data["data"]["userId"], sql_data["data"]["userCode"],
        sql_data["data"]["semesterId"], sql_data["data"]["campus"], sql_data["data"]["beginTime"],
        sql_data["data"]["endTime"], sql_data["data"]["totalLength"], sql_data["data"]["trueLength"],
        sql_data["data"]["totalTime"], sql_data["data"]["markList"], sql_data["data"]["phoneInfo"],
        sql_data["data"]["createTime"], sql_data["data"]["pageSize"], sql_data["data"]["pageNo"],
        sql_data["data"]["pageBegin"]))
    # 提交到数据库执行
    db.commit()
    return 0
