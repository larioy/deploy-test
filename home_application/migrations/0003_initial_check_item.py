# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations
from settings import CHECK_ITEM_JSON_FILE
from home_application.models import CheckItem


def initial_check_item(apps, schema_editor):
    try:
        CheckItem.objects.all().delete()
        json_data = open(CHECK_ITEM_JSON_FILE)
        check_content_obj = json.load(json_data)
        check_items = []
        for i in check_content_obj:
            check_items.append(CheckItem(
                id=i["id"],
                menu_id=i["menu_id"],
                name=i["name"],
                cn_name=i["cn_name"],
                compare_way=i["compare_way"],
                description=i["description"]
            ))
        CheckItem.objects.bulk_create(check_items)
        json_data.close()
    except Exception, e:
        print e


class Migration(migrations.Migration):
    dependencies = [
        ('home_application', '0002_initial_check_menu'),
    ]

    operations = [
        migrations.RunPython(initial_check_item),
    ]
