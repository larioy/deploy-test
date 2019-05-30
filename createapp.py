# -*-coding:utf-8-*-
import pymysql
import uuid
import datetime
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

# path="D:/Desktop/cer-mgmt"
# APPID="test111"
# APPTOKEN="testwqdewdqwefdqwerfdqwerfdew"
# BKHOST="http://paas.blueking.com"
# paasdbinfo = {
#     "host": "192.168.165.51",
#     "port": 3306,
#     "user": "root",
#     "password": "bk@321",
#     "db": "open_paas",
#     "charset": "utf8",
#     "cursorclass": pymysql.cursors.DictCursor
# }


#
# appinfo = {
#     "appid": "test",
#     "appname": "测试",
#     "introduction": "测试",
#     "creater": "iven",
#     "language": "python",
#     "app_token": str(uuid.uuid1()),
#     "tags_id": "1",
#     "nowtime": str(datetime.datetime.now()).split(".")[0],
#     "vcs_type": "1",
#     "vcs_url": "http://192.168.165.250/svn/iven/test1",
#     "vcs_username": "iven",
#     "vcs_password": "1qw2#ER$",
# }


def execute_mysql_sql(sql, mysql_server):
    connection = pymysql.connect(**mysql_server)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    connection.close()
    return result


def create_app(appinfo, paasdbinfo):
    try:
        sqlstr1 = """INSERT INTO `open_paas`.`paas_app` (`name`, `code`, `introduction`, `creater`, `created_date`, `state`, `is_already_test`, `is_already_online`, `first_test_time`, `first_online_time`, `language`, `auth_token`, `tags_id`, `deploy_token`, `is_use_celery`, `is_use_celery_beat`, `is_saas`, `logo`) VALUES ('%s', '%s', '%s', '%s', '%s', '1', '0', '0', NULL, NULL, '%s', '%s', NULL, '', '0', '0', '0', '')""" % (
            appinfo["appname"], appinfo["appid"], appinfo["introduction"], appinfo["creater"], appinfo["nowtime"], appinfo["language"], appinfo["app_token"])
        sqlstr2 = """INSERT INTO `open_paas`.`engine_apps` (`name`, `logo`, `app_code`, `app_lang`, `app_type`, `is_active`, `created_at`, `updated_at`) VALUES ('%s', '', '%s', '%s', '', '1', '%s', '%s')""" % (
            appinfo["appname"], appinfo["appid"], appinfo["language"], appinfo["nowtime"], appinfo["nowtime"])
        sqlstr3 = """INSERT INTO `open_paas`.`paas_app_secureinfo` (`app_code`, `vcs_type`, `vcs_url`, `vcs_username`, `vcs_password`, `db_type`, `db_host`, `db_port`, `db_name`, `db_username`, `db_password`) VALUES ('%s', '%s', '%s', '%s', '%s', 'mysql', NULL, '3306', NULL, NULL, NULL)""" % (
            appinfo["appid"], appinfo["vcs_type"], appinfo["vcs_url"], appinfo["vcs_username"], appinfo["vcs_password"])
        sqlstr4 = """select id from engine_apps where app_code = '%s'""" % appinfo["appid"]
        execute_mysql_sql(sqlstr1, paasdbinfo)
        execute_mysql_sql(sqlstr2, paasdbinfo)
        execute_mysql_sql(sqlstr3, paasdbinfo)
        engineappid = execute_mysql_sql(sqlstr4, paasdbinfo)[0]["id"]
        sqlstr5 = """INSERT INTO `open_paas`.`engine_app_tokens` (`key`, `created_at`, `updated_at`, `bk_app_id`) VALUES ('%s', '%s', '%s', '%s')""" % (appinfo["app_token"].replace("-", ""), appinfo["nowtime"], appinfo["nowtime"], str(engineappid))
        execute_mysql_sql(sqlstr5, paasdbinfo)
        print "app create success"
    except Exception, e:
        e_str = e.message if e.message else str(e)
        print e_str


def get_linenum(str_line, flines):
    for i in xrange(len(flines)):
        if flines[i].startswith(str_line):
            return i


def mod_default(path, APPID, APPTOKEN, BKHOST):
    try:
        real_path = str(path).replace("\\", "/").strip("/") + "/conf/default.py"
        fr = open(real_path, "r")
        flines = fr.readlines()
        fr.close()
        IDnum = get_linenum("APP_ID", flines)
        TOKENnum = get_linenum("APP_TOKEN", flines)
        HOSTnum = get_linenum("BK_PAAS_HOST", flines)
        flines[IDnum] = """APP_ID = '%s'\n""" % APPID
        flines[TOKENnum] = """APP_TOKEN = '%s' # pass ƽ̨token\n""" % APPTOKEN
        flines[HOSTnum] = """BK_PAAS_HOST = '%s'\n""" % BKHOST
        fw = open(real_path, "w+")
        fw.writelines(flines)
        fw.close()
        print "default file modify success"
    except Exception, e:
        e_str = e.message if e.message else str(e)
        print e_str


def mod_dbconfig(path):
    try:
        real_path_t = str(path).replace("\\", "/").strip("/") + "/conf/settings_testing.py"
        real_path_p = str(path).replace("\\", "/").strip("/") + "/conf/settings_production.py"
        frt = open("./settings_testing.py", "r")
        frtlines = frt.readlines()
        frt.close()
        frp = open("./settings_production.py", "r")
        frplines = frp.readlines()
        frp.close()
        fwt = open(real_path_t, "w+")
        fwt.writelines(frtlines)
        fwt.close()
        fwp = open(real_path_p, "w+")
        fwp.writelines(frplines)
        fwp.close()
        print "dbconfig file modify success"
    except Exception, e:
        e_str = e.message if e.message else str(e)
        print e_str


if __name__ == "__main__":
    paasdbinfo = {
        "host": str(sys.argv[1]),
        "port": 3306,
        "user": str(sys.argv[2]),
        "password": str(sys.argv[3]),
        "db": "open_paas",
        "charset": "utf8",
        "cursorclass": pymysql.cursors.DictCursor
    }
    appinfo = {
        "appid": str(sys.argv[4]),
        "appname": str(sys.argv[5]).decode("gbk").encode("utf8"),
        "introduction": str(sys.argv[6]).decode("gbk").encode("utf8"),
        "creater": str(sys.argv[7]),
        "language": "python",
        "app_token": str(uuid.uuid1()),
        "tags_id": "1",
        "nowtime": str(datetime.datetime.now()).split(".")[0],
        "vcs_type": "1",
        "vcs_url": str(sys.argv[8]),
        "vcs_username": str(sys.argv[9]),
        "vcs_password": str(sys.argv[10]),
        "bk_host": str(sys.argv[11]),
        "localpath": str(sys.argv[12])
    }
    create_app(appinfo, paasdbinfo)
    mod_default(appinfo["localpath"], appinfo["appid"], appinfo["app_token"], appinfo["bk_host"])
    mod_dbconfig(appinfo["localpath"])
