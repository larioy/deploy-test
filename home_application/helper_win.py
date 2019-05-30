# -*-coding:utf-8-*-

from blueking.component.shortcuts import get_client_by_user
from conf.default import APP_ID, APP_TOKEN, BK_PAAS_HOST
import base64
import time
import datetime
import copy
from common.log import logger
import httplib2
import requests
import json


# 操作服务器
def operate_server(username, server, script_content):
    client = get_client_by_user(username)
    kwargs = {
        "app_code": APP_ID,
        "app_secret": APP_TOKEN,
        "app_id": server["app_id"],
        "username": username,
        "content": base64.b64encode(script_content),
        "ip_list": server["ip_list"],
        "type": 2,
        "account": server["account"],
        "script_timeout": 3600
    }
    result = client.job.fast_execute_script(kwargs)
    if result["result"]:
        task_instance_id = result["data"]["taskInstanceId"]
        time.sleep(2)
        return {"result": True, "data": {'taskInstanceId': task_instance_id, 'check_server': server}}
    else:
        return {"result": False, "data": result["message"]}


def operate_server_srv(username, server, script_content, script_timeout=600):
    client = get_client_by_user(username)
    kwargs = {
        "app_code": APP_ID,
        "app_secret": APP_TOKEN,
        "app_id": server["app_id"],
        "username": username,
        "content": base64.b64encode(script_content),
        "ip_list": server["ip_list"],
        "type": 2,
        "account": server["account"],
        "script_timeout": script_timeout
    }
    result = client.job.fast_execute_script(kwargs)
    if result["result"]:
        task_id = result["data"]["taskInstanceId"]
        time.sleep(2)
        return get_ip_log_content(client, username, task_id)
    else:
        return {"result": False, "data": result["message"]}


# 获取脚本任务Log
def get_ip_log_content(client, username, task_id, i=1):
    kwargs = {
        "app_code": APP_ID,
        "app_secret": APP_TOKEN,
        "username": username,
        "task_instance_id": task_id
    }
    result = client.job.get_task_ip_log(kwargs)
    if result["result"]:
        if not result["data"][0]["isFinished"]:
            time.sleep(5)
            return get_ip_log_content(client, username, task_id)
        ip_log_content = []
        for i in result["data"][0]["stepAnalyseResult"]:
            if i["resultType"] == 9:
                ip_log_content.extend([{"result": True, "ip": str(j["ip"]), "logContent": j["logContent"], "source": j["source"]} for j in i["ipLogContent"]])
            else:
                ip_log_content.extend([{"result": False, "ip": str(j["ip"]), "logContent": i["resultTypeText"], "source": j["source"]} for j in i["ipLogContent"]])
        return {"result": True, "data": ip_log_content}
    i += 1
    if i < 5:
        time.sleep(5)
        return get_ip_log_content(client, username, task_id, i)
    err_msg = "get_logContent_timeout;task_id:{0};err_msg:{1}".format(task_id, result["message"])
    return {"result": False, "data": err_msg}


def check_winserver(username, server, item_list, log_days=7):
    if not item_list:
        return {"result": True, "data": {}}
    logdaybegin = str(datetime.datetime.now() - datetime.timedelta(log_days)).split(" ")[0].replace("-", "") + "160000.000000-000"
    script_content = r"""@echo off
"""
    if item_list.filter(check_item__cn_name__icontains="partition_").exists():
        script_content += """::partition
echo partition
echo @#@#
wmic path Win32_LogicalDisk where MediaType=12 get 'DeviceID','Size','FreeSpace' /value 2>nul
echo @@@@@@@@@@
"""
    if item_list.filter(check_item__cn_name__icontains="service_").exists():
        script_content += """::service
echo service
echo @#@#
wmic service where "(StartMode='Auto' and State!='Running') or Status!='OK'" get 'Caption','StartMode','State','Status' /value 2>nul
echo @@@@@@@@@@
"""
    if item_list.filter(check_item__menu__menu_name__icontains=u"性能").exists():
        script_content += """::perf
echo perf
echo @#@#
for %%i in (1,2,3,4,5,6) do (
    echo @@@@@
    wmic path Win32_PerfFormattedData_PerfOS_Processor where Name='_Total' get 'PercentProcessorTime','PercentDPCTime','PercentInterruptTime' /value 2>nul
    wmic path Win32_PerfFormattedData_PerfOS_System get 'ContextSwitchesPerSec','ProcessorQueueLength' /value 2>nul
    wmic path Win32_PerfFormattedData_PerfOS_Memory get 'AvailableMBytes','PagesPerSec','PercentCommittedBytesInUse' /value 2>nul
    wmic path Win32_PerfFormattedData_PerfDisk_PhysicalDisk where Name='_Total' get 'AvgDiskQueueLength','PercentDiskTime','DiskWritesPerSec','DiskReadsPerSec' /value 2>nul
    CHOICE /T 10 /C ync /CS /D y /n >nul)
echo @@@@@@@@@@
"""
    if item_list.filter(check_item__cn_name__icontains="err_").exists():
        error_param = ""
        if item_list.filter(check_item__cn_name__icontains="syserr").exists():
            error_param += """::syslog
echo syslog
echo @#@#
cscript.exe //Nologo -e:vbs "%tmpvbs%" System
echo @@@@@@@@@@
"""
        if item_list.filter(check_item__cn_name__icontains="apperr").exists():
            error_param += """::applog
echo applog
echo @#@#
cscript.exe //Nologo -e:vbs "%tmpvbs%" Application
echo @@@@@@@@@@
"""
        script_content += format_error_script(error_param, logdaybegin)
    result = operate_server(username, server, script_content)
    logger.exception(result)
    return result


def format_error_script(error_param, logdaybegin):
    script_content = """::vbs
set tmpvbs=tmpvbs
more +50 "%~f0">"%tmpvbs%"
{0}
del tmpvbs /F /Q 2>nul
goto :eof
\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n
on error resume next
dim a,objDict,key,wql
Set objArgs = WScript.Arguments
Set objDict = WSH.CreateObject("Scripting.Dictionary")
strComputer = "."
Set objSWbemLocator = CreateObject("WbemScripting.SWbemLocator")
Set objSWbemServices = objSWbemLocator.ConnectServer
wql="Select * from Win32_NTLogEvent where TimeGenerated>'{1}' and (EventType='1' or EventType='2') and Logfile='" & objArgs(0) &"'"
Set colItems = objSWbemServices.ExecQuery(wql)
For Each colItem In colItems
    a=0
    For Each Item In colItems
        if Item.EventCode=colItem.EventCode and Item.SourceName=colItem.SourceName then
            a=a+1
        end if
    next
    key="EventCode" & colItem.EventCode & "SourceName" & colItem.SourceName & "EventType" & colItem.EventType
    If not objDict.Exists(key) Then
        objDict.add key ,a
        WScript.Echo
        WScript.Echo "SourceName:" & colItem.SourceName
        WScript.Echo "EventCode:" & colItem.EventCode
        WScript.Echo "EventType:" & colItem.EventType
        WScript.Echo "Number:" & a
        WScript.Echo "TimeGenerated:" & colItem.TimeGenerated
        WScript.Echo
    end if
Next
    """.format(error_param, logdaybegin)
    return script_content


def get_check_winserver_log_content(client, user_name, task_instance_id):
    result = get_ip_log_content(client, user_name, task_instance_id)
    if not result["result"]:
        return result
    return_data = []
    for i in result["data"]:
        if not i["result"]:
            return_data.append(i)
            continue
        one_obj = format_check_log_content(i)
        return_data.append(one_obj)
    return {"result": True, "data": return_data}


def format_check_log_content(i):
    try:
        logcontent = i["logContent"].split("@@@@@@@@@@")
        tmp = {"partitioninfo": [], "services": [], "performance": {}, "syslogerr": [], "applogerr": []}
        for x in logcontent:
            item = x.split("@#@#")
            if "partition" in item[0]:
                tmp["partitioninfo"] = format_partition(item[1].strip("\n"))
            elif "service" in item[0]:
                tmp["services"] = format_log_content(item[1].strip("\n"))
            elif "perf" in item[0]:
                tmp["performance"] = format_performance(item[1].strip("\n"))
            elif "syslog" in item[0]:
                tmp["syslogerr"] = format_log(item[1].strip("\n"))
            elif "applog" in item[0]:
                tmp["applogerr"] = format_log(item[1].strip("\n"))
        i["logContent"] = tmp
    except Exception, e:
        logger.error(i["ip"])
        logger.exception(e)
        i["result"] = False
        i["logContent"] = u"执行失败"
    return i


def format_log_content(log_content, little_str="\n\n", big_str="\n\n\n\n"):
    log_list = [j.strip("\n") for j in log_content.split(big_str) if j]
    info = []
    for d in log_list:
        if d:
            dinfo = {}
            for s in d.split(little_str):
                if s:
                    dinfo[str(s).split("=")[0]] = str(s).split("=")[1]
            info.append(dinfo)
    return info


def format_log(log_content):
    log_list = [j.strip("\n") for j in log_content.split("\n\n") if j]
    logs = []
    for d in log_list:
        if not d:
            continue
        dinfo = {}
        for s in d.split("\n"):
            if s:
                dinfo[str(s).split(":")[0]] = str(s).split(":")[1]
        if dinfo["EventType"] == "1":
            dinfo["EventType"] = "error"
        if dinfo["EventType"] == "2":
            dinfo["EventType"] = "warning"
        time_generated = dinfo["TimeGenerated"].split(".")[0]
        dinfo["TimeGenerated"] = str(datetime.datetime.strptime(time_generated, "%Y%m%d%H%M%S") + datetime.timedelta(hours=8))
        logs.append(dinfo)
    return logs


def format_partition(log_content):
    partinfos = format_log_content(log_content)
    f_partinfo = []
    for i in partinfos:
        obj = {}
        obj["Freeper"] = "%.1f" % (float(i["FreeSpace"]) / float(i["Size"]) * 100)
        obj["FreeSpace"] = str("%.2f" % (float(i["FreeSpace"]) / 1024 / 1024 / 1024)) + "GB"
        obj["TotalSize"] = str("%.2f" % (float(i["Size"]) / 1024 / 1024 / 1024)) + "GB"
        obj["DeviceID"] = i["DeviceID"]
        f_partinfo.append(obj)
    return f_partinfo


def format_performance(log_content):
    perfdata = log_content.split("\n@@@@@")
    info = []
    for perf in perfdata:
        if not perf:
            continue
        try:
            p = [j.strip("\n") for j in perf.split("\n\n") if j]
            dinfo = {}
            for i in p:
                if i:
                    dinfo[str(i).split("=")[0]] = str(i).split("=")[1]
            info.append(dinfo)
        except Exception, e:
            logger.error(perf)
            logger.exception(e)
    f_perf = {}
    for key in info[0].keys():
        f_p = 0
        try:
            for i in info:
                f_p += int(i[key])
            f_perf[key] = f_p / len(info)
        except Exception, e:
            logger.exception(e)
    return f_perf


# 通过http调用API接口
def call_api_by_http(api_path, kwargs, username, is_issue=True, request_way='POST'):
    """
    :param 是否已在ESB注册:
    :param http请求方式（如："POST","GET"）:
    :return:
    """
    # if is_issue:
    #     base_path = BK_PAAS_HOST
    #     headers = {'Content-type': 'application/json'}
    # else:
    #     base_path = CMDB_PATH
    #     headers = {'Content-type': 'application/json', 'BK_USER': username, 'HTTP_BlUEKING_SUPPLIER_ID': '0'}
    base_path = BK_PAAS_HOST
    headers = {'Content-type': 'application/json'}
    api_path = api_path.strip('/')
    url = "%s/%s" % (base_path, api_path)
    if request_way == 'GET':
        res = requests.get(url, params=json.dumps(kwargs), headers=headers)
    else:
        res = requests.post(url, data=json.dumps(kwargs), headers=headers)
    if res.status_code == 200:
        content = json.loads(res.content)
        if content["result"]:
            return {"result": True, "data": content["data"]}
        else:
            return {"result": False, "data": content["message"]}
    else:
        return {"result": False, "data": res.status_code}


# 获取用户业务信息
# 只获取具备运维人员权限的业务
def get_business_by_user(username):
    kwargs = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": username
    }
    res = call_api_by_http("/api/c/compapi/v2/cc/search_business/", kwargs, username)
    if res["result"]:
        user_business_list = [{"bk_biz_id": i["bk_biz_id"], "bk_biz_maintainer": i["bk_biz_maintainer"],
                               "bk_biz_name": i["bk_biz_name"]} for i in res["data"]["info"]
                              if username in i["bk_biz_maintainer"].split(",")
                              ]
        return {"result": True, "data": user_business_list}
    else:
        return {"result": False, "data": res["data"]}


# 获取业务的“空闲机池”集群（空闲机、故障机模块）
def get_business_idle(business_id, username):
    url = "/api/c/compapi/v2/cc/search_set"
    kwargs = {
        'app_code': APP_ID,
        'app_secret': APP_TOKEN,
        'bk_biz_id': business_id,
        'bk_username': username,
        'condition': {"bk_set_name": u"空闲机池"},
        'fields': ["bk_set_id"],
        'page': {'limit': 1, 'sort': 'bk_set_name', 'start': 0}
    }
    res = call_api_by_http(url, kwargs, username, True, "POST")
    if not res["result"]:
        return {"result": False, "data": res["data"]}
    return get_idle_modules(res["data"]["info"][0], business_id, username)


def get_idle_modules(set_obj, app_id, username):
    url = "/api/c/compapi/v2/cc/search_module"
    kwargs = {
        'app_code': APP_ID,
        'app_secret': APP_TOKEN,
        'bk_biz_id': app_id,
        'bk_set_id': set_obj["bk_set_id"],
        'bk_username': username,
        'condition': {'bk_module_name': u'空闲机'},
        'fields': ['bk_module_id', 'bk_module_name'],
        'page': {'limit': 10, 'sort': 'bk_module_name', 'start': 0}
    }
    res = call_api_by_http(url, kwargs, username, True, "POST")
    if not res["result"]:
        return {"result": False, "data": u"获取空闲机异常"}
    return_data = {
        "bk_inst_id": set_obj["bk_set_id"], "bk_inst_name": u'空闲机池', 'bk_biz_id': app_id,
        "bk_obj_id": "set", "bk_obj_name": u"空闲机池", 'open': False,
        'child': [{
            "bk_inst_id": i["bk_module_id"], 'bk_biz_id': app_id, "bk_inst_name": i["bk_module_name"],
            "bk_obj_id": "module", "bk_obj_name": u"模块", "child": [], "default": 0, "isParent": True, 'open': False
        } for i in res['data']['info']]
    }
    return {"result": True, "data": return_data}


# 获取业务的拓扑结构
def get_business_topo(business_id, username, level=-1):
    api_path = "/api/c/compapi/v2/cc/search_biz_inst_topo/"
    kwargs = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": username,
        "bk_biz_id": business_id,
        "level": level
    }
    res = call_api_by_http(api_path, kwargs, username)
    if res["result"]:
        return_data = format_business_topo(res["data"], business_id)
        idle_result = get_business_idle(business_id, username)
        if idle_result["result"]:
            return_data[0]["child"].append(idle_result['data'])
        return {"result": True, "data": return_data}
    else:
        return {"result": False, "data": res["data"]}


def format_business_topo(data, bk_biz_id):
    return_data = []
    for i in data:
        tmp = dict(i, **{"isParent": True, 'bk_biz_id': bk_biz_id, 'open': False})
        tmp["child"] = format_business_topo(tmp["child"], bk_biz_id)
        if not tmp["child"]:
            tmp["isParent"] = False
        return_data.append(tmp)
    return return_data


# 获取业务、模块下的主机（windows、linux）
def get_hosts_by_business_module(business_id, module_id, username, host_type):
    business_filter = [{"field": "bk_biz_id", "operator": "$eq", "value": int(business_id)}] if business_id else []
    module_filter = [{"field": "bk_module_id", "operator": "$eq", "value": int(module_id)}] if module_id else []
    host_filter = [{"field": "bk_os_type", "operator": "$eq", "value": host_type}] if host_type == "1" or host_type == "2" else []
    kwargs = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": username,
        "condition": [
            {
                "bk_obj_id": "biz",
                "fields": [],
                "condition": business_filter
            },
            {
                "bk_obj_id": "host",
                "fields": [],
                "condition": host_filter
            },
            {
                "bk_obj_id": "module",
                "fields": [],
                "condition": module_filter
            }
        ]
    }
    return search_host(kwargs, username)


def get_hosts_by_apps(app_ids, username, host_type):
    business_filter = [{"field": "bk_biz_id", "operator": "$in", "value": app_ids}] if app_ids else []
    host_filter = [{"field": "bk_os_type", "operator": "$eq", "value": host_type}] if host_type == "1" or host_type == "2" else []
    kwargs = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": username,
        "condition": [
            {
                "bk_obj_id": "biz",
                "fields": [],
                "condition": business_filter
            },
            {
                "bk_obj_id": "host",
                "fields": [],
                "condition": host_filter
            },
            {
                "bk_obj_id": "module",
                "fields": [],
                "condition": []
            }
        ]
    }
    return search_host(kwargs, username)


def search_host(kwargs, username):
    res = call_api_by_http("/api/c/compapi/v2/cc/search_host/", kwargs, username)
    if not res["result"]:
        return {"result": False, "data": res["data"]}
    data = []
    for i in res['data']['info']:
        one_obj = i['host']
        if "2003" in one_obj["bk_os_name"]:
            continue
        os_name = format_win_os_name(one_obj["bk_os_name"])
        if not os_name:
            continue
        one_obj["bk_os_name"] = os_name
        one_obj["app_id"] = i["biz"][0]["bk_biz_id"]
        one_obj['bk_biz_id'] = i["biz"][0]["bk_biz_id"]
        one_obj["is_checked"] = False
        data.append(one_obj)
    return_data = filter_no_agent(data, username)
    return {"result": True, "data": return_data}


def filter_no_agent(data, username):
    kwargs = {
        "bk_app_code": APP_ID,
        "bk_app_secret": APP_TOKEN,
        "bk_username": username,
        "bk_supplier_id": 0,
        "hosts": [
            {
                "ip": i['bk_host_innerip'],
                "bk_cloud_id": i['bk_cloud_id'][0]["bk_inst_id"]
            } for i in data
        ]
    }
    res = call_api_by_http("/api/c/compapi/v2/gse/get_agent_status/", kwargs, username)
    if not res["result"]:
        return []
    return_data = []
    for i in data:
        key = u"{0}:{1}".format(i['bk_cloud_id'][0]["bk_inst_id"], i["bk_host_innerip"])
        if res["data"][key]["bk_agent_alive"]:
            return_data.append(i)
    return return_data


def format_win_os_name(os_name):
    if '2019' in os_name:
        return "Windows Server 2019"
    elif '2016' in os_name:
        return 'Windows Server 2016'
    elif '2012' in os_name:
        if 'R2' in os_name:
            return 'Windows Server 2012 R2'
        else:
            return 'Windows Server 2012'
    elif '2008' in os_name:
        if 'R2' in os_name:
            return 'Windows Server 2008 R2'
        else:
            return 'Windows Server 2008'
    return ''


# 获取用户业务、object、集群、模块拓扑
def get_business_topo_by_user(username):
    bus_result = get_business_by_user(username)
    if not bus_result["result"]:
        return {"result": False, "data": "get business info error"}
    return_data = []
    for bus_obj in bus_result["data"]:
        topo_result = get_business_topo(bus_obj["bk_biz_id"], username)
        if not topo_result["result"]:
            return {"result": False, "data": "get business topo info error"}
        return_data.append(topo_result["data"][0])
    return {"result": True, "data": return_data}
