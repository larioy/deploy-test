# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations
from settings import CONFIG_ITEM_JSON_FILE
from home_application.models import ConfigItem


def initial_config_item(apps, schema_editor):
    try:
        ConfigItem.objects.all().delete()
        json_data = open(CONFIG_ITEM_JSON_FILE)
        check_content_obj = json.load(json_data)
        config_items = []
        for i in check_content_obj:
            config_items.append(ConfigItem(
                menu_name=i["menu_name"],
                object_name=i["object_name"],
                name=i["name"],
                cn_name=i["cn_name"],
                description=i["description"],
                is_show=i["is_show"]
            ))
        ConfigItem.objects.bulk_create(config_items)
        json_data.close()
    except Exception, e:
        print e


class Migration(migrations.Migration):
    dependencies = [
        ('home_application', '0003_initial_check_item'),
    ]

    operations = [
        migrations.RunPython(initial_config_item),
    ]
