# -*- coding: utf-8 -*-

from common.mymako import render_json
from common.log import logger
from home_application.models import *
from home_application.sys_view import insert_log
import json
from django.db.models import Q


def get_item_list(request):
    try:
        filter_obj = eval(request.body)
        custom_items = CustomItem.objects.filter(cn_name__icontains=filter_obj["name"]).order_by("-id").values()
        return render_json({"result": True, "data": list(custom_items)})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员！"]})


def create_custom_item(request):
    try:
        custom_item = eval(request.body)
        is_exist = CustomItem.objects.filter(name=custom_item["name"]).exists()
        if is_exist:
            return render_json({"result": False, "data": u"巡检字段名已存在！"})
        is_exist = CustomItem.objects.filter(cn_name=custom_item["cn_name"]).exists()
        if is_exist:
            return render_json({"result": False, "data": u"巡检名称已存在！"})
        item = CustomItem()
        item.create_item(custom_item)
        CustomItemValue.objects.create(check_module_id=1, custom_item_id=item.id, value=item.compare_value)
        insert_log(request.user.username, "自定义巡检项管理", "新增自定义巡检项 %s" % custom_item["cn_name"])
        return render_json({"result": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": u"系统异常，请联系管理员！"})


def modify_custom_item(request):
    try:
        custom_item = eval(request.body)
        is_exist = CustomItem.objects.filter(name=custom_item["name"]).exclude(id=custom_item["id"]).exists()
        if is_exist:
            return render_json({"result": False, "data": u"巡检字段名已存在！"})
        is_exist = CustomItem.objects.filter(cn_name=custom_item["cn_name"]).exclude(id=custom_item["id"]).exists()
        if is_exist:
            return render_json({"result": False, "data": u"巡检名称已存在！"})
        item = CustomItem.objects.get(id=custom_item["id"])
        if item.cn_name == custom_item["cn_name"]:
            item_name = item.cn_name
        else:
            item_name = "%s ==> %s" % (item.cn_name, custom_item["cn_name"])
        item.modify_item(custom_item)
        CustomItemValue.objects.create(check_module_id=1, custom_item_id=item.id, value=item.compare_value)
        insert_log(request.user.username, "自定义巡检项管理", "修改自定义巡检项 %s" % item_name)
        return render_json({"result": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": u"系统异常，请联系管理员！"})


def delete_custom_item(request):
    try:
        item_obj = eval(request.body)
        CustomItem.objects.filter(id=item_obj["id"]).delete()
        insert_log(request.user.username, "自定义巡检项管理", "删除自定义巡检项 %s" % item_obj["cn_name"])
        return render_json({"result": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": u"系统异常，请联系管理员！"})
