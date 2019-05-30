# -*- coding: utf-8 -*-
from common.mymako import render_json
import json
from home_application.models import *
from common.log import logger
from home_application.enums import ErrorText


def detail_total(request):
    dict_data = json.loads(request.body)
    try:
        username = request.user.username
        check_report_id = dict_data["id"]
        if not check_report_id:
            report_list = CheckReport.objects.filter(status="COMPLETE")
            if not request.user.is_superuser:
                report_list = report_list.filter(check_task__created_by=username)
            report_obj = report_list.order_by("-when_created").first()
            if not report_obj:
                return render_json({"is_success": True, "data": -1})
            check_report_id = report_obj.id
        check_report = CheckReport.objects.get(id=check_report_id)
        if (not request.user.is_superuser) and check_report.check_task.created_by != username:
            return render_json({"is_success": False, "message": u"你没有访问权限"})
        report_detail_obj = CheckReportDetail.objects.filter(check_report_id=check_report_id)
        if dict_data['server']:
            report_detail_obj = report_detail_obj.filter(server=dict_data['server'])
        task_server = eval(check_report.check_task.ip_list)
        return_data = {"report_id": check_report.id, "when_created": check_report.when_created, "task_name": check_report.check_task.name, "details": []}
        for report_detail in report_detail_obj:
            details = get_report_details(report_detail, task_server, dict_data)
            return_data['details'].append(details)
        return render_json({"is_success": True, "data": return_data})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def get_report_details(report_detail, task_server, dict_data):
    info_obj = InfoDetail.objects.filter(report_detail_id=report_detail.id, is_warn=True, check_item__menu__is_show=True).order_by("-detail_type")
    if dict_data['server']:
        info_obj = info_obj.filter(report_detail__server=dict_data['server']).order_by("-detail_type")
    del_t = []
    des_l = []
    error = ""
    if not report_detail.is_success:
        fail_result = report_detail.fail_result
        if not fail_result:
            fail_result = u"未知异常"
        error = {"fail_result": fail_result}
    for x in info_obj:
        if (not x.check_item.description) or (x.detail_type in del_t):
            continue
        des = {"description": ErrorText.get(x.detail_type, ''), "detail_type": x.detail_type, "is_show": x.check_item.menu.is_show}
        del_t.append(x.detail_type)
        des_l.append(des)
    ip_obj = [s for s in task_server if s["ip"] == report_detail.server and s["source"] == report_detail.source][0]
    details = {
        "report_detail_id": report_detail.id,
        "ip": report_detail.server,
        "source": report_detail.source,
        "source_name": ip_obj["source_name"],
        "app_id": report_detail.app_id,
        "info": des_l,
        "error_count": len(des_l),
        "error": error}
    return details


def search_info_detail(request):
    report_detail_id = request.GET["report_detail_id"]
    try:
        info_details = InfoDetail.objects.filter(report_detail_id=report_detail_id, check_item__menu__is_show=True)
        detail_type = InfoDetail.objects.values("detail_type").distinct().order_by("detail_type")
        return_data = {}
        for i in detail_type:
            isks = get_check_info(info_details, i['detail_type'])
            return_data[i['detail_type']] = isks
        return_data["custom_list"] = get_custom_check_detail(report_detail_id)
        return render_json({"data": return_data, "is_success": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def get_custom_check_detail(report_detail_id):
    custom_details = CustomReportDetail.objects.filter(check_report_detail_id=report_detail_id)
    return_data = []
    for i in custom_details:
        one_obj = {
            "cn_name": i.custom_item.cn_name,
            "value": i.value,
            "compare_way": i.custom_item.compare_way,
            "compare_value": i.custom_item.compare_value,
            "is_success": i.is_success
        }
        return_data.append(one_obj)
    return return_data


def get_check_info(details, detail_type):
    list_nums = details.filter(detail_type=detail_type).values("detail_type", "list_num").distinct().order_by("list_num")
    return_data = []
    for u in list_nums:
        one_obj = details.filter(detail_type=detail_type, list_num=u["list_num"])
        one_items = []
        for i in one_obj:
            real_v = i.value
            one_items.append({"cn_name": i.check_item.name, "value": real_v, "is_warn": i.is_warn, "order": i.check_item.id, "description": i.check_item.description})
        one_items.sort(lambda x, y: cmp(x["order"], y["order"]))
        return_data.append({"data": one_items, "list_num": u["list_num"]})
    return return_data
