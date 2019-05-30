# -*- coding: utf-8 -*-
from celery import task
from celery.schedules import crontab
from celery.task import periodic_task

from esb.new_client import get_new_esb_client
from home_application.models import *
from home_application.helper_win import *
from common.log import logger
from esb.client import get_esb_client
import sys
import time
from enums import *
from django.db import connection

# """
# celery 任务示例
#
# 本地启动celery命令: python  manage.py  celery  worker  --settings=settings
# 周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings
# """


# @periodic_task(run_every=crontab(minute=0, hour=0))
# def delete_report():
#     pass

reload(sys)
sys.setdefaultencoding('utf-8')


#
# # 获取指定服务器执行脚本的帐号
# script_account = u'Administrator'


def get_user_name(request):
    return request.user.username


@task()
def run_check_task(user_name, task_id, celery_set_id, is_timing=True):
    celery_set = Celery_time_set.objects.get(id=celery_set_id)
    if celery_set.is_deleted and celery_set.set_type != RUN_TYPE.NOW:
        celery_set.delete()
        return
    check_task = Check_task.objects.get(id=task_id)
    celery_time = check_task.celery_time_set
    logger.info(u"开始执行巡检任务%s" % check_task.name)
    date_now = str(datetime.datetime.now()).split(".")[0]
    check_report = CheckReport.objects.create(check_task=check_task, when_created=date_now)
    all_success_len = 0
    server_len = len(eval(check_task.ip_list))
    try:
        all_success_len = get_check_success_count(check_task, user_name, check_report)
        logger.info(u"巡检任务执行完成！")
    except Exception, e:
        logger.error(u"任务“%s”执行失败" % check_task.name)
        logger.exception(e)
    check_report.report_info = u"总共巡检{0}台服务器，共完成{1}台".format(server_len, all_success_len)
    check_report.status = "COMPLETE"
    check_report.save()
    delete_report(user_name)
    finish_task(check_task, check_report, date_now, is_timing, celery_time, user_name)


def get_check_success_count(check_task, user_name, check_report):
    all_success_len = 0
    check_apps = set_check_apps(check_task.ip_list, check_task.app_id_list)
    item_list = CheckItemValue.objects.filter(check_module_id=check_task.check_module.id)
    task_instance_ids, custom_instance_id = run_check_script(check_apps, check_task, item_list, user_name)
    for x in task_instance_ids:
        check_server = x['check_server']
        all_success_len += get_check_result(x['taskInstanceId'], user_name, check_report, check_server, item_list)
    for u in custom_instance_id:
        success_len = format_custom_result(u, user_name, check_report)
        if not item_list:
            all_success_len += success_len
    return all_success_len


def run_check_script(check_apps, check_task, item_list, user_name):
    task_instance_ids = []
    custom_instance_id = []
    for i in check_apps:
        i['account'] = check_task.account
        logger.info(item_list)
        if item_list:
            result = check_winserver(user_name, i, item_list)
        else:
            result = {"result": True, "data": []}
        custom_result = get_check_custom_task_instance_id(user_name, i, check_task.check_module.id)
        if result["result"]:
            if result['data']:
                task_instance_ids.append(result['data'])
            if custom_result["result"]:
                custom_instance_id.append(custom_result["data"])
    return task_instance_ids, custom_instance_id


def finish_task(check_task, check_report, date_now, is_timing, celery_time, user_name):
    url = Settings.objects.get(key="url").value
    mail_content = u"亲爱的管理员，以下是本次巡检的结果概要报告，敬请查阅。<br />任务名称: %s <br />执行时间：%s <br />任务概况: %s <br />创建者：%s <br />详情请登录<a href='%s'>Windows巡检</a>查看" % (
        check_task.name, check_report.when_created, check_report.report_info, check_task.created_by, url + u"#/taskReportDetail?id=" + str(check_report.id))
    receivers = check_task.receivers
    title = u"Windows巡检报告-" + date_now
    new_send_email(receivers, title, mail_content)
    if is_timing and celery_time.set_type == RUN_TYPE.CYCLE:
        run_time = datetime.datetime.strptime(celery_time.run_time, "%Y-%m-%d %H:%M:%S")
        if celery_time.interval_type == INTERVAL_TYPE.DAY:
            run_time = run_time + datetime.timedelta(days=celery_time.time_interval)
        elif celery_time.interval_type == INTERVAL_TYPE.HOUR:
            run_time = run_time + datetime.timedelta(hours=celery_time.time_interval)
        celery_time.run_time = str(run_time).split(".")[0]
        celery_time.save()
        run_check_task.apply_async(args=[user_name, check_task.id, check_task.celery_time_set_id],
                                   eta=datetime.datetime.strptime(celery_time.run_time, "%Y-%m-%d %H:%M:%S"))


def delete_report(user_name):
    try:
        report_obj = CheckReport.objects.filter(status="COMPLETE", check_task__created_by=user_name).all()
        report_count = len(report_obj)
        set_obj = SetConfig.objects.filter(created_by=user_name)
        if not set_obj:
            report_num = Settings.objects.get(key='report_num').value
        else:
            report_num = set_obj.first().report_num
        if report_count > report_num > 0:
            ids = [i['id'] for i in report_obj.order_by("-when_created")[report_num:].values("id")]
            report_obj.filter(id__in=ids).delete()
            logger.info(u"删除过期报告成功")
        else:
            logger.info(u"报告数量正常")
    except Exception, e:
        logger.exception(e)


def get_check_server():
    app_ids = Business.objects.all().values("id")
    obj = ServerConfig.objects.exclude(check_server__host_name="").all()
    check_servers = []
    for app_id in app_ids:
        server = {
            'app_id': app_id['id'],
            'ip_list': []
        }
        for x in obj:
            if app_id['id'] == x.check_server.module.business.id:
                ips = {'ip': x.check_server.ip, 'source': x.check_server.source}
                server['ip_list'].append(ips)
        check_servers.append(server)
    return check_servers


def format_config_item(object_name, dict_content, server_config_id, order):
    try:
        info_contents = []
        for k, v in dict_content.items():
            item_name = object_name + "_" + k.lower()
            config_item = ConfigItem.objects.get(name=item_name)
            info_contents.append(ConfigDetail(
                server_config_id=server_config_id,
                config_item_id=config_item.id,
                value=v,
                detail_type=object_name,
                list_num=order
            ))
        ConfigDetail.objects.bulk_create(info_contents)
        date_now_str = str(datetime.datetime.now()).split('.')[0]
        ServerConfig.objects.filter(id=server_config_id).update(update_time=date_now_str)
    except Exception, e:
        logger.exception(e)


def set_check_apps(ip_list, app_id_list):
    servers = eval(ip_list)
    app_ids = app_id_list.split(";")
    app_ids.remove("")
    check_apps = []
    for app_id in app_ids:
        check_app = {"app_id": app_id, "ip_list": []}
        for server in servers:
            if str(server["app_id"]) == str(app_id):
                check_app["ip_list"].append({"ip": server["ip"], "source": server["source"]})
        if check_app["ip_list"]:
            check_apps.append(check_app)
    return check_apps


def get_check_custom_task_instance_id(username, check_server, check_module_id):
    custom_items = CustomItemValue.objects.filter(check_module_id=check_module_id)
    if not custom_items:
        return {"result": False}
    script_params = """

""".join([i.custom_item.script_content.replace("@echo off", "") for i in custom_items])
    script_content = """@echo off
{0}""".format(script_params)
    result = operate_server(username, check_server, script_content)
    return result


def get_check_result(task_instance_id, user_name, check_report, check_server, item_list):
    try:
        client = get_client_by_user(user_name)
        script_result = get_check_winserver_log_content(client, user_name, task_instance_id)
        if script_result["result"]:
            return format_all_server(script_result["data"], check_report, check_server["app_id"], item_list)
        servers_fail = []
        for i in check_server["ip_list"]:
            if not script_result["data"]:
                script_result["data"] = []
            servers_fail.append(CheckReportDetail(
                check_report_id=check_report.id,
                server=i["ip"],
                app_id=check_server["app_id"],
                source=i["source"],
                is_success=False,
                fail_result=script_result["data"],
                server_info=''
            ))
        CheckReportDetail.objects.bulk_create(servers_fail)
    except Exception, e:
        logger.exception(e)
    return 0


def format_custom_result(result, user_name, check_report):
    success_len = 0
    client = get_client_by_user(user_name)
    script_result = get_ip_log_content(client, user_name, result["taskInstanceId"])
    if not script_result["result"]:
        return 0
    for i in script_result["data"]:
        report_detail = CheckReportDetail.objects.get_or_create(check_report_id=check_report.id, server=i["ip"], source=i["source"], app_id=result["check_server"]["app_id"], defaults={"is_success": True})[0]
        if not i["result"]:
            continue
        log_contents = [u for u in i["logContent"].strip("\n").split("\n") if u]
        for u in log_contents:
            custom_item = CustomItem.objects.get(name=u.split("=")[0])
            compare_text = "'{2}'{1}'{0}'".format(custom_item.compare_value, custom_item.compare_way, u.split("=")[1].strip(" "))
            logger.info(compare_text)
            CustomReportDetail.objects.create(
                custom_item_id=custom_item.id,
                check_report_detail_id=report_detail.id,
                value=u.split("=")[1].strip(" "),
                is_success=eval(compare_text)
            )
        success_len += 1
    return success_len


def format_all_server(script_data, check_report, app_id, item_list):
    success_len = 0
    for i in script_data:
        if i['result']:
            report_detail = CheckReportDetail.objects.create(
                check_report_id=check_report.id,
                server=i["ip"],
                source=i["source"],
                app_id=app_id,
                is_success=True,
                server_info=''
            )
            format_one_server(i, report_detail, item_list)
            success_len += 1
        else:
            if not i['logContent']:
                i["logContent"] = ""
            CheckReportDetail.objects.create(
                check_report_id=check_report.id,
                server=i["ip"],
                source=i["source"],
                app_id=app_id,
                is_success=False,
                server_info="",
                fail_result=i['logContent']
            )
    return success_len


def format_one_server(log, report_detail, item_list):
    log_content = log['logContent']
    try:
        order = 1
        for i in log_content["services"]:
            format_check_item("service", i, report_detail.id, order, item_list)
            order += 1
        format_processor_item("performance", log_content["performance"], report_detail.id, 1, item_list)
        order = 1
        for i in log_content["applogerr"]:
            format_check_item("apperr", i, report_detail.id, order, item_list)
            order += 1
        order = 1
        for i in log_content["syslogerr"]:
            format_check_item("syserr", i, report_detail.id, order, item_list)
            order += 1
        order = 1
        for i in log_content["partitioninfo"]:
            format_check_item("partition", i, report_detail.id, order, item_list)
            order += 1
    except Exception, e:
        logger.exception(e)
        return 0


def format_check_item(object_name, dict_content, report_detail_id, order, item_list):
    info_contents = []
    for k, v in dict_content.items():
        if k == 'Caption':
            k = 'name'
        if k == 'Number':
            k = 'num'
        if k == 'TimeGenerated':
            k = 'time'
        if k == 'DeviceID':
            k = 'name'
        if k == 'TotalSize':
            k = 'size'
        if k == 'FreeSpace':
            k = 'free'
        item_name = object_name + "_" + k.lower()
        check_item_value = item_list.get(check_item__cn_name=item_name)
        is_warn = compare_item_value(check_item_value, v)
        if check_item_value.check_item.menu.id in (2, 3, 4):
            is_warn = True
        info_contents.append(InfoDetail(
            report_detail_id=report_detail_id,
            check_item_id=check_item_value.check_item.id,
            value=v,
            is_warn=is_warn,
            detail_type=object_name,
            list_num=order
        ))
    InfoDetail.objects.bulk_create(info_contents)


def format_processor_item(object_name, dict_content, report_detail_id, order, item_list):
    info_contents = []
    item_name = ""
    for k, v in dict_content.items():
        if k == "PercentProcessorTime":
            item_name = "processor_" + k.lower()
            object_name = 'cpu_performance'
        if k == "PercentInterruptTime":
            item_name = "processor_" + k.lower()
            object_name = 'cpu_performance'
        if k == "PercentDPCTime":
            item_name = "processor_" + k.lower()
            object_name = 'cpu_performance'
        if k == "ProcessorQueueLength":
            item_name = "system_" + k.lower()
            object_name = 'cpu_performance'
        if k == "ContextSwitchesPersec":
            item_name = "system_" + k.lower()
            object_name = 'cpu_performance'
        if k == "AvailableMBytes":
            item_name = "memory_" + k.lower()
            object_name = 'memory_performance'
        if k == "PagesPersec":
            item_name = "memory_" + k.lower()
            object_name = 'memory_performance'
        if k == "PercentCommittedBytesInUse":
            item_name = "memory_" + k.lower()
            object_name = 'memory_performance'
        if k == "PercentDiskTime":
            item_name = "physicaldisk_" + k.lower()
            object_name = 'disk_performance'
        if k == "AvgDiskQueueLength":
            item_name = "physicaldisk_" + k.lower()
            object_name = 'disk_performance'
        if k == "DiskReadsPersec":
            item_name = "physicaldisk_" + k.lower()
            object_name = 'disk_performance'
        if k == "DiskWritesPersec":
            item_name = "physicaldisk_" + k.lower()
            object_name = 'disk_performance'
        check_item = item_list.get(check_item__cn_name=item_name)
        is_warn = compare_item_value(check_item, v)
        info_contents.append(InfoDetail(
            report_detail_id=report_detail_id,
            check_item_id=check_item.check_item.id,
            value=v,
            is_warn=is_warn,
            detail_type=object_name,
            list_num=order
        ))
    InfoDetail.objects.bulk_create(info_contents)


def compare_item_value(check_item_value, v):
    try:
        is_normal = True
        if check_item_value.check_item.compare_way:
            try:
                v = float(v)
                compare_value = float(check_item_value.value)
            except:
                compare_value = check_item_value.value
            if check_item_value.check_item.compare_way == ">":
                is_normal = v > compare_value
            elif check_item_value.check_item.compare_way == ">=":
                is_normal = v >= compare_value
            elif check_item_value.check_item.compare_way == "<":
                is_normal = v < compare_value
            else:
                is_normal = v != compare_value
        return not is_normal
    except Exception, e:
        logger.exception(e)


def send_mail(to, subject, mail_content, content_type="HTML"):
    if not to:
        return
    client = get_esb_client()
    kwargs = {
        "to": to,
        "subject": subject,
        "content": mail_content,
        "content_type": content_type,
    }
    result = client.call("common", "send_email", kwargs)
    if result["result"]:
        logger.exception(u"邮件发送成功")
    else:
        logger.error(result["message"])


def new_send_email(receiver, title, content):
    try:
        logger.info(u"开始发送邮件")
        esb_client = get_new_esb_client()
        result = esb_client.call('cmsi', 'send_mail', receiver=receiver, title=title, content=content)
        if result["result"]:
            logger.info(u"邮件接口调用成功")
            return
        else:
            logger.info(u"邮件接口调用失败")
            logger.error(result["message"])
            return
    except Exception, e:
        logger.exception(e)
