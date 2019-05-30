# -*- coding: utf-8 -*-
from common.mymako import render_json
from home_application.celery_tasks import *
import json
from blueking.component.shortcuts import get_client_by_request
import datetime

ERROR_MSG = {
    "result": False,
    "data": [u"系统异常，请联系管理员！"]
}


def insert_log(operator, operated_type, detail):
    date_now_str = str(datetime.datetime.now()).split('.')[0]
    Logs.objects.create(operated_type=operated_type, when_created=date_now_str, operator=operator, content=detail)


def add_mail(request):
    args = eval(request.body)
    arr = []
    try:
        now = str(datetime.datetime.now()).split('.')[0]
        for i in args:
            mail_obj, is_add = Mailboxes.objects.get_or_create(
                username=i["user_name"], mailbox=i["email"],
                created_by=request.user.username,
                defaults={
                    "when_created": now
                })
            if is_add:
                insert_log(request.user.username, u"邮箱管理", u"新增邮箱：%s" % i["email"])
                arr.append(mail_obj.to_dic())
        return render_json({'result': True, "data": arr})
    except Exception, e:
        logger.exception(e)
        return render_json(ERROR_MSG)


def delete_mail(request):
    mail_id = request.GET["id"]
    try:
        mail_delete = Mailboxes.objects.get(id=mail_id)
        insert_log(request.user.username, u"邮箱管理", u"删除邮箱：%s" % mail_delete.mailbox)
        mail_delete.delete()
        return render_json({'result': True})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员"]})


def search_mail(request):
    args = eval(request.body)
    try:
        result = Mailboxes.objects.filter(username__icontains=args["username"], mailbox__icontains=args["mailbox"])
        if not request.user.is_superuser:
            result = result.filter(created_by=request.user.username)
        return_data = [i.to_dic() for i in result.order_by("-when_created")]
        return render_json({"result": True, "data": return_data})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员"]})


def search_log(request):
    filter_obj = json.loads(request.body)
    logs = Logs.objects.filter(
        when_created__range=(str(filter_obj["whenStart"]) + " 00:00:00", str(filter_obj["whenEnd"]) + " 23:59:59"),
        operated_type__icontains=filter_obj["operateType"],
        operator__icontains=filter_obj["operator"]).order_by("-id")
    return render_json({"result": True, "data": [i.to_dic() for i in logs]})


def update_url(request):
    try:
        window_url = request.GET["app_path"]
        sys_config = Settings.objects.filter(key="url")
        if sys_config:
            sys_config.update(value=window_url)
        else:
            Settings.objects.create(key="url", value=window_url)
        return render_json({"result": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False})


# 获取用户所有业务下的全部主机列表
def search_business_servers(request):
    try:
        username = request.user.username
        user_business = get_business_by_user(username)
        if not user_business["result"]:
            logger.error("获取用户业务信息失败：%s" % user_business["data"])
            return render_json({"result": False, "data": [u"获取用户业务信息失败，请联系管理员"]})
        app_ids = [bus_obj["bk_biz_id"] for bus_obj in user_business["data"]]
        bus_hosts = get_hosts_by_apps(app_ids, username, "2")
        if not bus_hosts["result"]:
            logger.error("获取业务主机信息失败：%s" % (bus_hosts["data"]))
            return render_json({"result": True, "data": []})
        return_servers = format_host_list(bus_hosts["data"])
        return render_json({"result": True, "data": return_servers})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统出错，请联系管理员"]})


# 获取用户所有业务的拓扑
def search_business_topo(request):
    try:
        username = request.user.username
        return_data = get_business_topo_by_user(username)
        if not return_data["result"]:
            logger.error("获取用户业务拓扑失败：%s" % return_data["data"])
            return render_json({"result": False, "data": [u"获取用户拓扑失败，请联系管理员"]})
        return render_json({"result": True, "data": return_data["data"]})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统出错，请联系管理员"]})


# 获取模块下的主机列表
def search_module_servers(request):
    try:
        username = request.user.username
        module_id = request.GET["bk_inst_id"]
        if str(module_id) == '-1':
            return render_json([])
        return_data = get_hosts_by_business_module("", module_id, username, "2")
        if not return_data["result"]:
            logger.error("获取模块下主机列表失败：%s" % return_data["data"])
            return render_json([])
        host_list = format_host_list(return_data["data"])
        return render_json(host_list)
    except Exception, e:
        logger.exception(e)
        return render_json([])


def format_host_list(host_list, is_checked=False):
    return_data = []
    for i in host_list:
        for x in i['bk_cloud_id']:
            one_obj = {
                'app_id': i["app_id"], 'bk_biz_id': i["app_id"], 'source_name': x["bk_inst_name"],
                'bk_inst_id': -1, 'bk_host_id': i['bk_host_id'], 'bk_obj_id': "IP",
                'bk_obj_name': 'IP', 'child': [], "checked": is_checked,
                "bk_inst_name": i["bk_host_innerip"] + u"(" + x["bk_inst_name"] + u")",
                "bk_host_innerip": i["bk_host_innerip"], 'ip': i['bk_host_innerip'],
                'source': x['bk_inst_id'], 'bk_os_name': i['bk_os_name'], 'isParent': False
            }
            if one_obj not in return_data:
                return_data.append(one_obj)
    return return_data


def get_check_servers(request):
    try:
        obj = json.loads(request.body)
        return_data = get_check_servers_children(obj, request.user.username)
        return render_json({"result": True, "data": return_data})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, 'data': []})


def get_check_servers_children(obj, username):
    return_data = []
    if "child" not in obj:
        return []
    for i in obj["child"]:
        one_obj = i
        one_obj["checked"] = True
        one_obj["open"] = True
        one_obj["is_open_all"] = True
        if one_obj["bk_obj_name"] != "IP":
            one_obj['child'] = get_check_servers_children(i, username)
            if not one_obj["child"]:
                one_obj["isParent"] = False
        return_data.append(one_obj)
    if not obj["child"]:
        if obj["bk_obj_id"] != "module":
            return []
        servers = get_hosts_by_business_module("", obj['bk_inst_id'], username, "2")
        if not servers["result"]:
            logger.error("获取模块下主机列表失败：%s" % servers["data"])
            return []
        return_data = format_host_list(servers["data"], True)
    return return_data


def get_all_mail(request):
    url = "{0}/api/c/compapi/v2/bk_login/get_all_users/".format(BK_PAAS_HOST)
    headers = {"Accept": "application/json"}
    params = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": request.user.username,
    }
    res = requests.get(url, params=params, headers=headers)
    result = json.loads(res.content)
    mail_list = []
    for i, j in enumerate(result['data']):
        if not result['data'][i]['email']:
            del result['data'][i]
    for i in result['data']:
        mail_list.append({"user_name": i["bk_username"], "email": i["email"]})
    return render_json({"result": True, "data": mail_list})
