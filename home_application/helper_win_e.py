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
        "script_timeout": 1200
    }
    result = client.job.fast_execute_script(kwargs)
    if result["result"]:
        taskInstanceId = result["data"]["taskInstanceId"]
        time.sleep(2)
        return {"result": True, "data": {'taskInstanceId': taskInstanceId, 'check_server': server}}
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
        if result["data"][0]["isFinished"]:
            ip_log_content = []
            for i in result["data"][0]["stepAnalyseResult"]:
                if i["resultType"] == 9:
                    ip_log_content.extend([{"result": True, "ip": str(j["ip"]), "logContent": j["logContent"]} for j in i["ipLogContent"]])
                else:
                    ip_log_content.extend([{"result": False, "ip": str(j["ip"]), "logContent": i["resultTypeText"]} for j in i["ipLogContent"]])
            return {"result": True, "data": ip_log_content}
        else:
            time.sleep(5)
            return get_ip_log_content(client, username, task_id)
    else:
        i += 1
        if i < 5:
            time.sleep(5)
            return get_ip_log_content(client, username, task_id, i)
        else:
            err_msg = "get_logContent_timeout;task_id:%s;err_msg:%s" % (task_id, result["message"])
            return {"result": False, "data": err_msg}


# script_account = "Administrator"
# app_id = 3
# ip_list = [{"source": "1", "ip": "192.168.2.32"}, {"source": "1", "ip": "192.168.2.34"}]
# winserver = {"app_id": app_id, "ip_list": ip_list, "account": script_account}


def check_winserver(username, server, log_days=7):
    logdaybegin = str(datetime.datetime.now() - datetime.timedelta(log_days)).split(" ")[0].replace("-", "") + "160000.000000-000"
    script_content = r"""@echo off
::partition
wmic path Win32_LogicalDisk where MediaType=12 get 'DeviceID','Size','FreeSpace' /value 2>nul
::service
echo @@@@@@@@@@
wmic service where "(StartMode='Auto' and State!='Running') or Status!='OK'" get 'Caption','StartMode','State','Status' /value 2>nul
::perf
echo @@@@@@@@@@
for %%i in (1,2,3,4,5,6) do (
    echo @@@@@
    wmic path Win32_PerfFormattedData_PerfOS_Processor where Name='_Total' get 'PercentProcessorTime','PercentDPCTime','PercentInterruptTime' /value 2>nul
    wmic path Win32_PerfFormattedData_PerfOS_System get 'ContextSwitchesPerSec','ProcessorQueueLength' /value 2>nul
    wmic path Win32_PerfFormattedData_PerfOS_Memory get 'AvailableMBytes','PagesPerSec','PercentCommittedBytesInUse' /value 2>nul
    wmic path Win32_PerfFormattedData_PerfDisk_PhysicalDisk where Name='_Total' get 'AvgDiskQueueLength','PercentDiskTime','DiskWritesPerSec','DiskReadsPerSec' /value 2>nul
    CHOICE /T 10 /C ync /CS /D y /n >nul)
::vbs
set tmpvbs=tmpvbs
more +27 "%~f0">"%tmpvbs%"
::syslog
echo @@@@@@@@@@
cscript.exe //Nologo -e:vbs "%tmpvbs%" System
::applog
echo @@@@@@@@@@
cscript.exe //Nologo -e:vbs "%tmpvbs%" Application
del tmpvbs /F /Q 2>nul
goto :eof

on error resume next
dim a,objDict,key,wql
Set objArgs = WScript.Arguments
Set objDict = WSH.CreateObject("Scripting.Dictionary")
strComputer = "."
Set objSWbemLocator = CreateObject("WbemScripting.SWbemLocator")
Set objSWbemServices = objSWbemLocator.ConnectServer
wql="Select * from Win32_NTLogEvent where TimeGenerated>'{0}' and (EventType='1' or EventType='2') and Logfile='" & objArgs(0) &"'"
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
""".format(logdaybegin)
    result = operate_server(username, server, script_content)
    return result


def get_check_winserver_log_content(client, user_name, taskInstanceId):
    result = get_ip_log_content(client, user_name, taskInstanceId)
    if result["result"]:
        data = result["data"]
        return_data = []
        for i in data:
            if i["result"]:
                try:
                    logcontent = i["logContent"].replace("\r", "").split("@@@@@@@@@@")
                    partitioninfo = format_partition(logcontent[0])
                    services = format_log_content(logcontent[1])
                    performance = format_performance(logcontent[2])
                    syslogerr = format_log(logcontent[3])
                    applogerr = format_log(logcontent[4])
                    i["logContent"] = {
                        "partitioninfo": partitioninfo, "performance": performance, "services": services,
                        "syslogerr": syslogerr, "applogerr": applogerr}
                    return_data.append(i)
                except Exception, e:
                    logger.error(i["ip"])
                    logger.exception(e)
                    i["result"] = False
                    i["logContent"] = u"执行失败"
                    return_data.append(i)
            else:
                return_data.append(i)
        return {"result": True, "data": return_data}
    else:
        return result


def format_log_content(log_content, little_str="\n", big_str="\n\n\n"):
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
    log_list = [j.strip("\n") for j in log_content.split("\n\n\n") if j]
    logs = []
    for d in log_list:
        if d:
            dinfo = {}
            for s in d.split("\n"):
                if s:
                    dinfo[str(s).split(":")[0]] = str(s).split(":")[1]
            if dinfo["EventType"] == "1":
                dinfo["EventType"] = "error"
            if dinfo["EventType"] == "2":
                dinfo["EventType"] = "warning"
            TimeGenerated = dinfo["TimeGenerated"].split(".")[0]
            dinfo["TimeGenerated"] = str(datetime.datetime.strptime(TimeGenerated, "%Y%m%d%H%M%S") + datetime.timedelta(hours=8))
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
        try:
            if perf:
                p = [j.strip("\n") for j in perf.split("\n") if j]
                dinfo = {}
                for i in p:
                    if i:
                        dinfo[str(i).split("=")[0]] = str(i).split("=")[1]
                info.append(dinfo)
        except Exception, e:
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


def check_srv_conf(username, server):
    script_content = r"""@echo off
::os
wmic os get 'CSName','LastBootUpTime','InstallDate','Caption','Version' /value 2>nul
wmic path win32_timezone get 'Caption' /value 2>nul
::cpu
echo @@@@@@@@@@
wmic CPU get 'Name','NumberOfCores' /value 2>nul
::mem
echo @@@@@@@@@@
wmic MEMORYCHIP get 'Capacity' /value 2>nul
::disk
echo @@@@@@@@@@
wmic DISKDRIVE get 'Model','Size' /value 2>nul
::nic
echo @@@@@@@@@@
wmic nic where 'PhysicalAdapter=TRUE and NetEnabled=TRUE' get 'MACAddress' /value 2>nul
::model
echo @@@@@@@@@@
wmic path Win32_ComputerSystem get 'Model' /value
"""
    result = operate_server_srv(username, server, script_content)
    if result["result"]:
        data = result["data"]
        return_data = []
        for i in data:
            if i["result"]:
                try:
                    logcontent = i["logContent"].replace("\r", "").split("@@@@@@@@@@")
                    basicinfo = format_basic(logcontent[0])
                    cpuinfo = format_cpu(logcontent[1])
                    meminfo = format_mem(logcontent[2])
                    diskinfo = format_disk(logcontent[3])
                    macinfo = format_mac(logcontent[4])
                    hostmodel = "虚拟机" if "Virtual" in format_log_content(logcontent[5])[0]["Model"] else "物理机"
                    i["logContent"] = {"basicinfo": basicinfo, "cpuinfo": cpuinfo, "meminfo": meminfo, "diskinfo": diskinfo, "macinfo": macinfo, "hostmodel": hostmodel}
                    return_data.append(i)
                except Exception, e:
                    logger.error(i["ip"])
                    logger.exception(e)
                    i["result"] = False
                    i["logContent"] = u"执行失败"
                    return_data.append(i)
            else:
                return_data.append(i)
        return {"result": True, "data": return_data}
    else:
        return result


def format_basic(log_content):
    log_list = [j.strip("\n") for j in log_content.split("\n") if j]
    basicinfo = {}
    basicinfo["hostname"] = str(log_list[1]).split("=")[1]
    basicinfo["timezone"] = str(log_list[5]).split("=")[1]
    basicinfo["InstallDate"] = str(datetime.datetime.strptime(str(str(log_list[2]).split("=")[1].split(".")[0]), "%Y%m%d%H%M%S")).split(".")[0]
    boottime = datetime.datetime.strptime(str(str(log_list[3]).split("=")[1].split(".")[0]), "%Y%m%d%H%M%S")
    basicinfo["uptime"] = str((datetime.datetime.now() - boottime).days) + "Days"
    basicinfo["Version"] = str(log_list[4]).split("=")[1]
    basicinfo["os"] = str(log_list[0]).split("=")[1]
    return basicinfo


def format_cpu(log_content):
    cpu = format_log_content(log_content)
    f_cpu = {}
    f_cpu["num"] = len(cpu)
    s = ""
    for i in cpu:
        if str(i["Name"]) not in s:
            s += str(i["Name"]) + ";"
    f_cpu["Model"] = s.strip(";")
    return f_cpu


def format_mem(log_content):
    mem = format_log_content(log_content)
    f_mem = {}
    f_mem["num"] = len(mem)
    s = 0
    for i in mem:
        s += int(i["Capacity"])
    f_mem["size"] = str(s / 1024 / 1024 / 1024) + "GB"
    return f_mem


def format_disk(log_content):
    disks = format_log_content(log_content)
    f_disk = {}
    f_disk["num"] = len(disks)
    s = 0
    for disk in disks:
        s += int(disk["Size"])
    f_disk["Size"] = str("%.2f" % (float(s) / 1024 / 1024 / 1024)) + "GB"
    return f_disk


def format_mac(log_content):
    mac = format_log_content(log_content)
    f_mac = ""
    for i in mac:
        f_mac += str(i["MACAddress"]) + ";"
    return f_mac.strip(";")


def get_app_by_user(username):
    client = get_client_by_user(username)
    kwargs = {
        "app_code": APP_ID,
        "app_secret": APP_TOKEN,
        "username": username,
    }
    result = client.cc.get_app_by_user(kwargs)
    if result["result"]:
        app_list = [{"id": i["ApplicationID"], "text": i["ApplicationName"]} for i in result["data"] if
                    i["ApplicationName"] != u"资源池"]
        return {"result": True, "data": app_list}
    else:
        return {"result": False, "data": [result["message"]]}


def get_host_list_by_business(business_id, username):
    http = httplib2.Http()
    url = "%s:80/api/c/self-service-api/Host_config/get_hostlist_by_business/" % BK_PAAS_HOST
    headers = {"Accept": "application/json"}
    params = {
        "app_code": APP_ID,
        "app_secret": APP_TOKEN,
        "username": username,
        "business_id": business_id,
        "sys_type": "windows"
    }
    res = requests.get(url, params=params, headers=headers)
    result = json.loads(res.content)
    return result


def get_host_list_by_ip(ip, username):
    url = "%s:80/api/c/self-service-api/Host_config/get_host_list_by_ip/" % BK_PAAS_HOST
    headers = {"Accept": "application/json"}
    params = {
        "app_code": APP_ID,
        "app_secret": APP_TOKEN,
        "username": username,
        "ip": ip,
        "sys_type": "windows"
    }
    res = requests.get(url, params=params, headers=headers)
    result = json.loads(res.content)
    return result
