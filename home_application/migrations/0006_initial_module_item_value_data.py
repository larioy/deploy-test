# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations
from settings import MODULE_ITEM_VALUE_FILE
from home_application.models import CheckItemValue, CheckModule
import datetime


def initial_module_item_value_data(apps, schema_editor):
    try:
        CheckItemValue.objects.all().delete()
        json_data = open(MODULE_ITEM_VALUE_FILE)
        items = json.load(json_data)
        CheckModule.objects.all().delete()
        CheckModule.objects.create(
            id=1,
            name="系统模板",
            base_module_id=0,
            is_build_in=True,
            when_created=str(datetime.datetime.now()).split(".")[0],
            created_by="system",
            description="系统内置模板，请勿对其进行修改和删除"
        )
        item_list = [CheckItemValue(
            check_item_id=i["check_item_id"],
            check_module_id=i["check_module_id"],
            value=i["value"],
        ) for i in items]
        CheckItemValue.objects.bulk_create(item_list)
        json_data.close()
    except Exception, e:
        print e


class Migration(migrations.Migration):
    dependencies = [
        ('home_application', '0005_initial_settings'),
    ]

    operations = [
        migrations.RunPython(initial_module_item_value_data),
    ]
