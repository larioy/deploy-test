# -*- coding: utf-8 -*-

from common.mymako import render_json
from common.log import logger
from home_application.models import *
from home_application.sys_view import insert_log
import json
from django.db.models import Q


def search_module_list(request):
    try:
        filter_obj = eval(request.body)
        module_list = CheckModule.objects.filter(name__icontains=filter_obj["name"], is_deleted=False)
        if not request.user.is_superuser:
            module_list = module_list.filter(Q(created_by=request.user.username) | Q(created_by="system"))
        return render_json({"result": True, "data": list(module_list.values())})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员！"]})


def get_module_list(request):
    try:
        module_list = CheckModule.objects.filter(is_deleted=False)
        if not request.user.is_superuser:
            module_list = module_list.filter(Q(created_by=request.user.username) | Q(created_by="system"))
        return render_json({"result": True, "data": [{"id": i.id, "text": i.name + "(" + i.created_by + ")"} for i in module_list]})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员！"]})


def get_module_item_list(request):
    try:
        module_id = request.GET["module_id"]
        value_list = CheckItemValue.objects.filter(check_module_id=module_id)
        return_data = []
        id_list = []
        for i in value_list:
            tmp = {
                "menu_one": i.check_item.menu.menu_name, "menu_two": i.check_item.menu.name,
                "name": i.check_item.name, "cn_name": i.check_item.cn_name, "value": i.value, "compare_way": i.check_item.compare_way,
                "can_modified": i.check_item.compare_way != "" and i.check_item.name != "top_sql", "is_checked": True, "check_item_id": i.check_item.id
            }
            id_list.append(i.check_item_id)
            return_data.append(tmp)
        custom_item_list = get_custom_item_list(module_id)
        no_check_item_list = CheckItemValue.objects.filter(check_module_id=1).exclude(check_item_id__in=id_list)
        return_data += [{
            "menu_one": i.check_item.menu.menu_name, "menu_two": i.check_item.menu.name,
            "name": i.check_item.name, "cn_name": i.check_item.cn_name, "value": i.value, "compare_way": i.check_item.compare_way,
            "can_modified": i.check_item.compare_way != "", "is_checked": False, "check_item_id": i.check_item.id
        } for i in no_check_item_list]
        return_data.sort(lambda x, y: cmp(x["check_item_id"], y["check_item_id"]))
        menus = CheckMenu.objects.all().values("menu_name").distinct()
        menu_list = []
        for i in menus:
            menu_two = CheckMenu.objects.filter(menu_name=i["menu_name"])
            menu_two_list = [{"name": u.name, "isShow": True, "is_checked": True} for u in menu_two]
            menu_list.append({"menu_one": i["menu_name"], "isShow": True, "is_checked": True, "menu_two": menu_two_list})
        return render_json({"result": True, "data": return_data, "menu_list": menu_list, "custom_item_list": custom_item_list})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员！"]})


def get_custom_item_list(module_id):
    custom_item_list = CustomItemValue.objects.filter(check_module_id=module_id)
    tmp = [{
        "name": i.custom_item.name, "cn_name": i.custom_item.cn_name, "value": i.value, "compare_way": i.custom_item.compare_way,
        "can_modified": True, "is_checked": True, "custom_item_id": i.custom_item.id
    } for i in custom_item_list]
    no_check_custom_item_list = CustomItemValue.objects.filter(check_module_id=1).exclude(custom_item_id__in=[i.custom_item_id for i in custom_item_list])
    tmp += [{
        "name": i.custom_item.name, "cn_name": i.custom_item.cn_name, "value": i.value, "compare_way": i.custom_item.compare_way,
        "can_modified": True, "is_checked": False, "custom_item_id": i.custom_item.id
    } for i in no_check_custom_item_list]
    tmp.sort(lambda x, y: cmp(x["custom_item_id"], y["custom_item_id"]))
    return tmp


def create_module(request):
    try:
        module_obj = json.loads(request.body)
        is_exist = CheckModule.objects.filter(is_deleted=False, name=module_obj["name"], created_by=request.user.username).exists()
        if is_exist:
            return render_json({"result": False, "data": [u"该模板名称已存在!"]})
        check_module = CheckModule()
        check_module.create_item(module_obj)
        item_value_list = create_check_item_value(module_obj, check_module)
        CheckItemValue.objects.bulk_create(item_value_list)
        custom_item_value = create_custom_item_value(module_obj, check_module)
        CustomItemValue.objects.bulk_create(custom_item_value)
        insert_log(request.user.username, "模板管理", "新增模板：%s" % module_obj["name"])
        return render_json({"result": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员！"]})


def modify_module(request):
    try:
        module_obj = json.loads(request.body)
        is_exist = CheckModule.objects.filter(is_deleted=False, name=module_obj["name"], created_by=request.user.username).exclude(id=module_obj["id"]).exists()
        if is_exist:
            return render_json({"result": False, "data": [u"该模板名称已存在!"]})
        check_module = CheckModule.objects.get(id=module_obj["id"])
        check_module.modify_item(module_obj)
        CheckItemValue.objects.filter(check_module_id=module_obj["id"]).delete()
        item_value_list = create_check_item_value(module_obj, check_module)
        CheckItemValue.objects.bulk_create(item_value_list)
        CustomItemValue.objects.filter(check_module_id=module_obj["id"]).delete()
        custom_item_value = create_custom_item_value(module_obj, check_module)
        CustomItemValue.objects.bulk_create(custom_item_value)
        insert_log(request.user.username, "模板管理", "修改模板：%s" % module_obj["name"])
        return render_json({"result": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员！"]})


def create_custom_item_value(module_obj, check_module):
    return_data = []
    for i in module_obj["custom_item_list"]:
        if not i["is_checked"]:
            continue
        return_data.append(CustomItemValue(
            custom_item_id=i["custom_item_id"], check_module_id=check_module.id, value=i["value"]
        ))
    return return_data


def create_check_item_value(module_obj, check_module):
    item_value_list = []
    for i in module_obj["check_item_list"]:
        if not i["is_checked"]:
            continue
        item_value_list.append(CheckItemValue(
            check_item_id=i["check_item_id"], check_module_id=check_module.id, value=i["value"]
        ))
    return item_value_list


def delete_module(request):
    try:
        module_obj = json.loads(request.body)
        CheckModule.objects.filter(id=module_obj["id"]).update(is_deleted=True)
        insert_log(request.user.username, "模板管理", "删除模板：%s" % module_obj["name"])
        return render_json({"result": True})
    except Exception, e:
        logger.exception(e)
        return render_json({"result": False, "data": [u"系统异常，请联系管理员！"]})
