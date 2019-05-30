# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations
from settings import SETTINGS_JSON_FILE
from home_application.models import Settings


def initial_settings(apps, schema_editor):
    try:
        Settings.objects.all().delete()
        json_data = open(SETTINGS_JSON_FILE)
        check_content_obj = json.load(json_data)
        settings = []
        for i in check_content_obj:
            settings.append(Settings(
                key=i['key'],
                value=i['value']
            ))
        Settings.objects.bulk_create(settings)
        json_data.close()
    except Exception, e:
        print e


class Migration(migrations.Migration):
    dependencies = [
        ('home_application', '0004_initial_config_item'),
    ]

    operations = [
        migrations.RunPython(initial_settings),
    ]
