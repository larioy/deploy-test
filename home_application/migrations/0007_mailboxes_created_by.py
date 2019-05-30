# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0006_initial_module_item_value_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailboxes',
            name='created_by',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
