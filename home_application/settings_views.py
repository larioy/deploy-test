# -*- coding: utf-8 -*-
from common.mymako import render_json
from home_application.celery_tasks import *
import json
from home_application.sys_view import insert_log


def get_set_config(request):
    try:
        user_name = request.user.username
        set_obj = SetConfig.objects.filter(created_by=user_name).first()
        if set_obj:
            config_account = set_obj.config_account
            report_num = set_obj.report_num
            created_by = set_obj.created_by
        else:
            config_account = Settings.objects.get(key='config_account').value
            report_num = Settings.objects.get(key='report_num').value
            created_by = user_name
        return_data = {'config_account': config_account, 'report_num': report_num, 'created_by': created_by}
        return render_json({"is_success": True, "data": return_data})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": e.message})


def modify_set_config(request):
    json_data = request.body
    dict_data = json.loads(json_data)
    try:
        user_name = request.user.username
        config_account = dict_data['config_account']
        report_num = dict_data['report_num']
        created_by = user_name
        set_obj = SetConfig.objects.filter(created_by=user_name)
        if set_obj:
            set_obj.update(config_account=config_account, report_num=report_num)
        else:
            date_now_str = str(datetime.datetime.now()).split('.')[0]
            SetConfig.objects.create(config_account=config_account, report_num=report_num, created_by=created_by, when_created=date_now_str)
        SetConfig.objects.all().update(config_account=config_account)
        operator = user_name
        operated_type = u"系统设置-全局配置"
        operated_detail = u"修改全局配置"
        insert_log(operator, operated_type, operated_detail)
        return render_json({'is_success': True})
    except Exception, e:
        logger.exception(e)
        return render_json({"is_success": False, "message": ['修改失败！']})
