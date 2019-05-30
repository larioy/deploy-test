# -*- coding: utf-8 -*-
from common.mymako import render_json
from common.log import logger
from home_application.models import *
import datetime


def get_count_obj(request):
    try:
        user_name = request.user.username
        count_list = get_count_list(user_name, request.user.is_superuser)
        task_list = get_task_list_chart(user_name, request.user.is_superuser)
        report_list = get_report_list_chart(user_name, request.user.is_superuser)
        return_data = {"count_list": count_list, "task_list": task_list, "report_list": report_list}
        return render_json({"is_success": True, "data": return_data})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统出错，请联系管理员！"]})


def get_count_list(user_name, is_superuser):
    report_details = CheckReportDetail.objects.all()
    report_list = CheckReport.objects.filter(status="COMPLETE")
    if not is_superuser:
        report_details = report_details.filter(check_report__check_task__created_by=user_name)
        report_list = report_list.filter(check_task__created_by__contains=user_name)
    app_count = report_details.values("app_id").distinct().count()
    server_count = report_details.values("server", "source").distinct().count()
    report_count = report_list.count()
    error_count = report_details.filter(infodetail__is_warn=1).values("server", "source").distinct().count()
    count_list = {"app_count": app_count, "server_count": server_count, "report_count": report_count, "error_server": error_count}
    return count_list


def get_report_list_chart(user_name, is_superuser):
    reports = CheckReport.objects.filter(status="COMPLETE")
    if not is_superuser:
        reports = reports.filter(check_task__created_by__contains=user_name)
    report_list = [{"text": x['when_created'] + " 完成了一次巡检", "id": x["id"]} for x in reports.values("id", "when_created").order_by("-when_created")][0:4]
    return list(report_list)


def get_task_list_chart(user_name, is_superuser):
    install_list = [{"name": u"本月巡检次数", "data": get_check_list(user_name, is_superuser)}]
    months = get_month_in_year()
    return {"data": install_list, "categories": [str(i) + "月" for i in months]}


def get_month_in_year():
    u = 0
    months = []
    m = datetime.datetime.now().month
    for i in xrange(1, 13):
        if i > m:
            months.insert(u, i)
            u += 1
        else:
            months.append(i)
    return months


def get_check_list(user_name, is_superuser):
    date_now = datetime.datetime.now()
    return_data = []
    check_report = CheckReport.objects.filter(status="COMPLETE")
    if not is_superuser:
        check_report = check_report.filter(check_task__created_by=user_name)
    for i in xrange(12):
        time_start = str(date_now.year) + "-" + "%02d" % date_now.month + "-01 00:00:00"
        time_end = str(date_now.year) + "-" + "%02d" % date_now.month + "-32 00:00:00"
        one_date = check_report.filter(when_created__range=(time_start, time_end)).count()
        return_data.insert(0, one_date)
        date_delay = get_1st_of_last_month(date_now)
        date_now = date_delay
    return return_data


def get_1st_of_last_month(today):
    year = today.year
    month = today.month
    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    res = datetime.datetime(year, month, 1)
    return res
