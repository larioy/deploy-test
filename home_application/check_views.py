# -*- coding: utf-8 -*-
from common.mymako import render_json
from home_application.models import *
from home_application.celery_tasks import run_check_task
from django.db.models.query import Q
from home_application.sys_view import insert_log
from home_application.helper_win import *


def get_account(request):
    account = Settings.objects.filter(key="account").get().value
    return render_json({'result': True, 'data': account})


def search_check_task(request):
    json_data = request.body
    dict_data = json.loads(json_data)
    try:
        name = dict_data["name"]
        time_set_type = dict_data['time_type']
        task_list = Check_task.objects.filter(
            name__icontains=name, is_deleted=False,
            celery_time_set__set_type__icontains=time_set_type
        )
        if not request.user.is_superuser:
            task_list = task_list.filter(created_by=request.user.username)
        return_data = [data.to_dic() for data in task_list.order_by("-when_created")]
        return render_json({"is_success": True, "data": return_data})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def get_modify_check_task(request):
    json_data = request.body
    dict_data = json.loads(json_data)
    try:
        user_name = request.user.username
        task_list = Check_task.objects.get(id=dict_data['id'])
        if (not request.user.is_superuser) and task_list.created_by != user_name:
            return render_json({"is_success": False, "message": u"您没有访问权限！"})
        return_data = task_list.to_dic()
        return render_json({"is_success": True, "data": return_data})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def create_check_task(request):
    try:
        data = json.loads(request.body)
        task_exist = Check_task.objects.filter(name=data["name"], created_by=request.user.username).exists()
        if task_exist:
            return render_json({"is_success": False, "data": [u"该任务名称已存在！"]})
        check_task, celery_time_set = create_check_task_and_celery(data, request.user.username)
        if data["time_type"] == "NOW":
            celery_time_set.is_deleted = True
            celery_time_set.save()
            run_check_task.delay(request.user.username, check_task.id, celery_time_set.id)
        else:
            run_check_task.apply_async(args=[request.user.username, check_task.id, celery_time_set.id],
                                       eta=datetime.datetime.strptime(celery_time_set.run_time, "%Y-%m-%d %H:%M:%S"))
        insert_log(request.user.username, u"巡检任务管理", u"新增巡检 : " + check_task.name)
        return render_json({"is_success": True})
    except Exception, e:
        error_msg = e.message if e.message else str(e)
        logger.exception(e)
        return render_json({"is_success": False, "message": error_msg})


def create_check_task_and_celery(data, user_name):
    day_long = data["day_long"]
    if day_long == '':
        day_long = 0
    date_now = str(datetime.datetime.now()).split(".")[0]
    celery_time_set = Celery_time_set.objects.create(
        first_time=data["time_set"], run_time=data["time_set"], time_interval=day_long,
        set_type=data["time_type"], interval_type=data["interval_type"]
    )
    check_task = Check_task.objects.create(
        name=data["name"], created_by=user_name, ip_list=data["servers"], modified_by=user_name,
        receivers=data["receivers"], celery_time_set=celery_time_set,
        when_created=date_now, check_module_id=data["check_module_id"],
        when_modified=date_now, app_id_list=data["app_id_list"], account=data["account"]
    )
    return check_task, celery_time_set


def modify_check_task(request):
    try:
        data = eval(request.body)
        task_exist = Check_task.objects.filter(name=data["name"], created_by=request.user.username).exclude(id=data["id"]).exists()
        if task_exist:
            return render_json({"is_success": False, "data": [u"该任务名称已存在！"]})
        old_task = update_old_task(data, request.user.username)
        time_type = data["time_type"]
        time_set = data["time_set"]
        interval_type = data["interval_type"]
        day_long = data["day_long"]
        if day_long == '':
            day_long = 0
        new_celery_time_set = Celery_time_set.objects.create(
            first_time=time_set, run_time=time_set, time_interval=day_long,
            set_type=time_type, interval_type=interval_type
        )
        old_task.celery_time_set = new_celery_time_set
        old_task.save()
        if time_type == "NOW":
            run_check_task.delay(request.user.username, old_task.id, new_celery_time_set.id)
        else:
            run_check_task.apply_async(
                args=[request.user.username, old_task.id, new_celery_time_set.id],
                eta=datetime.datetime.strptime(new_celery_time_set.run_time, "%Y-%m-%d %H:%M:%S")
            )
        insert_log(request.user.username, u"巡检任务管理", u"编辑修改任务 : " + old_task.name)
        return render_json({"is_success": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def update_old_task(data, username):
    task_id = data["id"]
    name = data["name"]
    receivers = data["receivers"]
    servers = data["servers"]
    app_id_list = data["app_id_list"]
    account = data["account"]
    date_now = str(datetime.datetime.now()).split(".")[0]
    old_task = Check_task.objects.get(id=task_id)
    old_task.name = name
    old_task.ip_list = servers
    old_task.modified_by = username
    old_task.receivers = receivers
    old_task.app_id_list = app_id_list
    old_task.when_modified = date_now
    old_task.account = account
    old_task.check_module_id = data["check_module_id"]
    old_task.save()
    old_celery_time_set = old_task.celery_time_set
    old_celery_time_set.is_deleted = True
    old_celery_time_set.save()
    return old_task


def delete_check_task(request):
    dict_data = json.loads(request.body)
    try:
        check_task = Check_task.objects.get(id=dict_data["id"])
        check_task.is_deleted = True
        celery = check_task.celery_time_set
        celery.is_deleted = True
        celery.save()
        check_task.save()
        operator = request.user.username
        insert_log(operator, u"巡检任务管理", u"删除任务 : " + check_task.name)
        return render_json({"is_success": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def start_task(request):
    dict_data = json.loads(request.body)
    try:
        task_id = dict_data["task_id"]
        old_task = Check_task.objects.get(id=task_id)
        user_name = request.user.username
        run_check_task.delay(user_name, old_task.id, old_task.celery_time_set.id, False)
        operated_type = u"巡检任务管理"
        operated_detail = u"开启扫描 : " + old_task.name
        insert_log(user_name, operated_type, operated_detail)
        return render_json({"is_success": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def search_check_item(request):
    try:
        menu_list = [{"menu_name": "磁盘分区信息", "id": [1]},
                     {"menu_name": "系统异常服务", "id": [2]},
                     {"menu_name": "近7天系统错误日志", "id": [3]},
                     {"menu_name": "近7天应用程序错误日志", "id": [4]}]
        for m in menu_list:
            m['is_show'] = CheckMenu.objects.get(id__in=m['id']).is_show
        menu_name = ["CPU性能", "内存性能", "磁盘性能"]
        for name in menu_name:
            ids = [x.id for x in CheckMenu.objects.filter(menu_name=name)]
            data = {"menu_name": name, "id": ids}
            menu_list.append(data)
        return_data = []
        for menus in menu_list:
            menus["item"] = list(CheckItem.objects.filter(menu_id__in=menus['id']).exclude(compare_way="").values("name", "id", "compare_way", "compare_value", "menu__is_show"))
            if menus['menu_name'] == "CPU性能" or menus['menu_name'] == "内存性能" or menus['menu_name'] == "磁盘性能":
                show_count = CheckMenu.objects.filter(menu_name=menus['menu_name'], is_show=False).count()
                menus["is_show"] = show_count <= 0
            return_data.insert(0, menus)
        return render_json({"is_success": True, "data": return_data})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def modify_check_item(request):
    dict_data = json.loads(request.body)
    try:
        details = dict_data["details"]
        for detail in details:
            CheckItem.objects.filter(id=detail['id']).update(compare_value=detail["compare_value"])
            menu_id = CheckItem.objects.filter(id=detail['id']).all().distinct().values("menu__id")[0]
            CheckMenu.objects.filter(id=menu_id['menu__id']).update(is_show=detail["menu__is_show"])
        menus = dict_data["menus"]
        for menu in menus:
            CheckMenu.objects.filter(id__in=menu['id']).update(is_show=menu['is_show'])
        operator = request.user.username
        operated_type = u"巡检标准配置"
        operated_detail = u"修改巡检标准配置"
        insert_log(operator, operated_type, operated_detail)
        return render_json({'is_success': True})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def search_check_report(request):
    dict_data = json.loads(request.body)
    try:
        name = dict_data["task_name"]
        result = dict_data["result"]
        if result == "ALL":
            result = ""
        check_reports = CheckReport.objects.filter(check_task__name__icontains=name, status__icontains=result).order_by("-id")
        if not request.user.is_superuser:
            check_reports = check_reports.filter(check_task__created_by=request.user.username).order_by("-id")
        return_data = [report.to_dic() for report in check_reports]
        return render_json({"data": return_data, "is_success": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


# 趋势报告
def get_ip_list(request):
    if request.user.is_superuser:
        ip_list = CheckReportDetail.objects.all().values("server", "source").distinct()
    else:
        ip_list = CheckReportDetail.objects.filter(check_report__check_task__created_by=request.user.username).values("server", "source").distinct()
    return_data = [{"id": i["server"] + "s" + str(i["source"]), 'text': u"{0}（区域ID：{1}）".format(i["server"], i["source"])} for i in ip_list]
    return render_json({'is_success': True, 'data': return_data})


def get_chart_list(request):
    user_name = request.user.username
    try:
        server_ips = request.GET['ip']
        ip = server_ips.split("s")[0]
        source = server_ips.split("s")[1]
        report_list = CheckReport.objects.filter(
            checkreportdetail__server=ip,
            checkreportdetail__source=source,
            checkreportdetail__is_success=True, status='COMPLETE',
        )
        if not request.user.is_superuser:
            report_list = report_list.filter(
                check_task__created_by__contains=user_name
            )
        perf_info = get_cpu_chart(ip, source, report_list.order_by("when_created").values("id").distinct())
        return render_json({"result": True, "data": perf_info})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员！"]})


def get_error_server_list(info_list, report_list):
    return_data = []
    for i in report_list:
        server_len = info_list.filter(report_detail__check_report_id=i["id"]).filter(
            Q(check_item__menu_id__in=[4, 5, 6]) | Q(is_warn=True)).values("report_detail__server").distinct().count()
        return_data.append(server_len)
    return return_data


def get_cpu_chart(server_ip, server_source, report_list):
    cpu_one_obj = {"name": 'Processor\ % Processor Time', "data": []}
    cpu_two_obj = {"name": 'System\ Processor Queue Length', "data": []}
    cpu_three_obj = {"name": 'Processor\ % DPC Time', "data": []}
    cpu_four_obj = {"name": 'System\ Processor Queue Length', "data": []}
    cpu_five_obj = {"name": 'System\ Context Switches/Sec', "data": []}
    mem_one_obj = {"name": 'Memory\ Available MBytes', "data": []}
    mem_two_obj = {"name": 'Memory\ % Committed Bytes In Use', "data": []}
    mem_three_obj = {"name": 'Memory\ Pages/sec', "data": []}
    disk_one_obj = {"name": 'PhysicalDisk\ % Disk Time', "data": []}
    disk_two_obj = {"name": 'PhysicalDisk\ Avg. Disk Queue Length', "data": []}
    disk_three_obj = {"name": 'PhysicalDisk\ Disk Reads/sec', "data": []}
    disk_space = {"name": '磁盘剩余空间比（%）', "data": []}
    for u in report_list:
        try:
            cpu_one_value = float(InfoDetail.objects.get(
                check_item__cn_name='processor_percentprocessortime',
                report_detail__server=server_ip,
                report_detail__source=server_source,
                report_detail__check_report_id=u["id"]).value)
            cpu_two_value = float(InfoDetail.objects.get(check_item__cn_name='system_processorqueuelength',
                                                         report_detail__server=server_ip,
                                                         report_detail__source=server_source,
                                                         report_detail__check_report_id=u["id"]).value)
            cpu_three_value = float(InfoDetail.objects.get(check_item__cn_name='processor_percentdpctime',
                                                           report_detail__server=server_ip,
                                                           report_detail__source=server_source,
                                                           report_detail__check_report_id=u["id"]).value)
            cpu_four_value = float(InfoDetail.objects.get(check_item__cn_name='system_processorqueuelength',
                                                          report_detail__server=server_ip,
                                                          report_detail__source=server_source,
                                                          report_detail__check_report_id=u["id"]).value)
            cpu_five_value = float(InfoDetail.objects.get(check_item__cn_name='system_contextswitchespersec',
                                                          report_detail__server=server_ip,
                                                          report_detail__source=server_source,
                                                          report_detail__check_report_id=u["id"]).value)
            mem_one_value = float(InfoDetail.objects.get(check_item__cn_name='memory_availablembytes', report_detail__server=server_ip,
                                                         report_detail__source=server_source,
                                                         report_detail__check_report_id=u["id"]).value)
            mem_two_value = float(InfoDetail.objects.get(check_item__cn_name='memory_percentcommittedbytesinuse',
                                                         report_detail__server=server_ip,
                                                         report_detail__source=server_source,
                                                         report_detail__check_report_id=u["id"]).value)
            mem_three_value = float(InfoDetail.objects.get(check_item__cn_name='memory_pagespersec',
                                                           report_detail__server=server_ip,
                                                           report_detail__source=server_source,
                                                           report_detail__check_report_id=u["id"]).value)
            disk_one_value = float(InfoDetail.objects.get(check_item__cn_name='physicaldisk_percentdisktime',
                                                          report_detail__server=server_ip,
                                                          report_detail__source=server_source,
                                                          report_detail__check_report_id=u["id"]).value)
            disk_two_value = float(InfoDetail.objects.get(check_item__cn_name='physicaldisk_avgdiskqueuelength',
                                                          report_detail__server=server_ip,
                                                          report_detail__source=server_source,
                                                          report_detail__check_report_id=u["id"]).value)
            disk_three_value = float(InfoDetail.objects.get(check_item__cn_name='physicaldisk_diskreadspersec',
                                                            report_detail__server=server_ip,
                                                            report_detail__source=server_source,
                                                            report_detail__check_report_id=u["id"]).value)
            free_items = InfoDetail.objects.filter(check_item__cn_name="partition_free", report_detail__server=server_ip,
                                                   report_detail__source=server_source,
                                                   report_detail__check_report_id=u["id"])
            disk_items = InfoDetail.objects.filter(check_item__cn_name="partition_size",
                                                   report_detail__source=server_source,
                                                   report_detail__server=server_ip, report_detail__check_report_id=u["id"])
            all_free_size = sum([float(d.value.replace("GB", "")) for d in free_items])
            all_size = sum([float(d.value.replace("GB", "")) for d in disk_items])
            disk_space_size = float("%.2f" % (all_free_size / all_size * 100))
        except:
            cpu_one_value = "null"
            cpu_two_value = "null"
            cpu_three_value = "null"
            cpu_four_value = "null"
            cpu_five_value = "null"
            mem_one_value = "null"
            mem_two_value = "null"
            mem_three_value = "null"
            disk_one_value = "null"
            disk_two_value = "null"
            disk_three_value = "null"
            disk_space_size = 'null'
        cpu_one_obj["data"].append(cpu_one_value)
        cpu_two_obj["data"].append(cpu_two_value)
        cpu_three_obj["data"].append(cpu_three_value)
        cpu_four_obj["data"].append(cpu_four_value)
        cpu_five_obj["data"].append(cpu_five_value)
        mem_one_obj["data"].append(mem_one_value)
        mem_two_obj["data"].append(mem_two_value)
        mem_three_obj["data"].append(mem_three_value)
        disk_one_obj["data"].append(disk_one_value)
        disk_two_obj["data"].append(disk_two_value)
        disk_three_obj["data"].append(disk_three_value)
        disk_space['data'].append(disk_space_size)
    return {
        "cpu_one": [cpu_one_obj, cpu_two_obj, cpu_three_obj, cpu_four_obj, cpu_five_obj],
        "mem_one": [mem_one_obj, mem_two_obj, mem_three_obj],
        "disk_one": [disk_one_obj, disk_two_obj, disk_three_obj],
        "disk_space": [disk_space]
    }


def get_task_option(request):
    try:
        if not request.user.is_superuser:
            mail_data = Mailboxes.objects.filter(created_by=request.user.username).values("mailbox").distinct()
        else:
            mail_data = Mailboxes.objects.all().values("mailbox").distinct()
        mail_list = [{"id": i["mailbox"], "text": i["mailbox"]} for i in mail_data]
        module_data = CheckModule.objects.filter(is_deleted=False)
        if not request.user.is_superuser:
            module_data = module_data.filter(Q(created_by=request.user.username) | Q(created_by="system"))
        module_list = [{"id": i.id, "text": i.name + "(" + i.created_by + ")"} for i in module_data]
        return render_json({"result": True, "mail_list": mail_list, "module_list": module_list})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员！"]})
