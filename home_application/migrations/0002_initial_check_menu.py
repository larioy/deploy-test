# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations
from settings import CHECK_MENU_JSON_FILE
from home_application.models import CheckMenu


def initial_check_menu(apps, schema_editor):
    try:
        CheckMenu.objects.all().delete()
        json_data = open(CHECK_MENU_JSON_FILE)
        check_content_obj = json.load(json_data)
        check_menus = []
        for i in check_content_obj:
            check_menus.append(CheckMenu(
                menu_name=i["menu_name"],
                name=i["name"],
                is_show=i["is_show"]
            ))
        CheckMenu.objects.bulk_create(check_menus)
        json_data.close()
    except Exception, e:
        print e


class Migration(migrations.Migration):
    dependencies = [
        ('home_application', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_check_menu),
    ]
