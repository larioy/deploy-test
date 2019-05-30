# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('created_by', models.CharField(max_length=100)),
                ('when_created', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Celery_time_set',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_time', models.CharField(max_length=100)),
                ('run_time', models.CharField(max_length=100)),
                ('time_interval', models.IntegerField(default=0)),
                ('set_type', models.CharField(max_length=10)),
                ('interval_type', models.CharField(default=0, max_length=10)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Check_task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('created_by', models.CharField(max_length=100)),
                ('ip_list', models.TextField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('modified_by', models.CharField(max_length=100)),
                ('receivers', models.TextField()),
                ('app_id_list', models.TextField(null=True)),
                ('when_created', models.CharField(max_length=100)),
                ('when_modified', models.CharField(max_length=100)),
                ('account', models.CharField(default='Administrator', max_length=50)),
                ('celery_time_set', models.OneToOneField(to='home_application.Celery_time_set')),
            ],
        ),
        migrations.CreateModel(
            name='CheckItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('cn_name', models.CharField(max_length=100)),
                ('compare_way', models.CharField(default=b'', max_length=10, null=True)),
                ('description', models.TextField(default=b'', null=True)),
                ('can_modify', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CheckItemValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
                ('check_item', models.ForeignKey(to='home_application.CheckItem')),
            ],
        ),
        migrations.CreateModel(
            name='CheckMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('menu_name', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('is_show', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CheckModule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('when_created', models.CharField(max_length=30)),
                ('created_by', models.CharField(max_length=100)),
                ('modified_by', models.CharField(default=b'', max_length=100)),
                ('when_modified', models.CharField(default=b'', max_length=30)),
                ('base_module_id', models.IntegerField(default=0)),
                ('is_build_in', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('description', models.TextField(default=b'')),
            ],
        ),
        migrations.CreateModel(
            name='CheckReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when_created', models.CharField(max_length=100)),
                ('report_info', models.CharField(max_length=200, null=True)),
                ('status', models.CharField(default=b'RUNNING', max_length=100, null=True)),
                ('check_task', models.ForeignKey(to='home_application.Check_task')),
            ],
        ),
        migrations.CreateModel(
            name='CheckReportDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server', models.CharField(max_length=100)),
                ('source', models.IntegerField(default=1)),
                ('app_id', models.IntegerField(default=1)),
                ('server_info', models.TextField()),
                ('is_success', models.BooleanField(default=True)),
                ('fail_result', models.TextField(default=b'', null=True)),
                ('check_report', models.ForeignKey(to='home_application.CheckReport')),
            ],
        ),
        migrations.CreateModel(
            name='CheckServers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=100)),
                ('host_name', models.CharField(max_length=100)),
                ('operation_system', models.CharField(max_length=200)),
                ('source', models.CharField(max_length=100, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ConfigDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
                ('detail_type', models.CharField(max_length=100)),
                ('list_num', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ConfigItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('menu_name', models.CharField(max_length=100)),
                ('object_name', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('cn_name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'', null=True)),
                ('is_show', models.BooleanField(default=False)),
                ('is_build_in', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
                ('check_server', models.ForeignKey(to='home_application.CheckServers')),
                ('config_item', models.ForeignKey(to='home_application.ConfigItem')),
            ],
        ),
        migrations.CreateModel(
            name='CustomItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('cn_name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'', null=True)),
                ('script_content', models.TextField()),
                ('created_by', models.CharField(max_length=100)),
                ('when_created', models.CharField(max_length=30)),
                ('when_modified', models.CharField(default=b'', max_length=30)),
                ('compare_way', models.CharField(max_length=10)),
                ('compare_value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CustomItemValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
                ('check_module', models.ForeignKey(to='home_application.CheckModule')),
                ('custom_item', models.ForeignKey(to='home_application.CustomItem')),
            ],
        ),
        migrations.CreateModel(
            name='CustomReportDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
                ('is_success', models.BooleanField(default=True)),
                ('check_report_detail', models.ForeignKey(to='home_application.CheckReportDetail')),
                ('custom_item', models.ForeignKey(to='home_application.CustomItem')),
            ],
        ),
        migrations.CreateModel(
            name='InfoDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_show', models.BooleanField(default=True)),
                ('value', models.TextField()),
                ('is_warn', models.BooleanField(default=False)),
                ('detail_type', models.CharField(max_length=100)),
                ('list_num', models.IntegerField(default=0)),
                ('check_item', models.ForeignKey(to='home_application.CheckItem')),
                ('report_detail', models.ForeignKey(to='home_application.CheckReportDetail')),
            ],
        ),
        migrations.CreateModel(
            name='Logs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operated_type', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('when_created', models.CharField(max_length=30)),
                ('operator', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Mailboxes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=50)),
                ('mailbox', models.CharField(max_length=100)),
                ('when_created', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('business', models.ForeignKey(to='home_application.Business')),
            ],
        ),
        migrations.CreateModel(
            name='ServerConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when_created', models.CharField(max_length=20)),
                ('update_time', models.CharField(default=b'', max_length=20)),
                ('check_server', models.ForeignKey(to='home_application.CheckServers')),
            ],
        ),
        migrations.CreateModel(
            name='SetConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_by', models.CharField(default=b'', max_length=100)),
                ('config_account', models.CharField(default=b'Administrator', max_length=100)),
                ('report_num', models.IntegerField(default=0)),
                ('sync_day', models.IntegerField(default=1)),
                ('when_created', models.CharField(default=b'', max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50)),
                ('value', models.TextField()),
                ('description', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='configdetail',
            name='config_item',
            field=models.ForeignKey(to='home_application.ConfigItem'),
        ),
        migrations.AddField(
            model_name='configdetail',
            name='server_config',
            field=models.ForeignKey(to='home_application.ServerConfig'),
        ),
        migrations.AddField(
            model_name='checkservers',
            name='module',
            field=models.ForeignKey(to='home_application.Module', null=True),
        ),
        migrations.AddField(
            model_name='checkitemvalue',
            name='check_module',
            field=models.ForeignKey(to='home_application.CheckModule'),
        ),
        migrations.AddField(
            model_name='checkitem',
            name='menu',
            field=models.ForeignKey(to='home_application.CheckMenu'),
        ),
        migrations.AddField(
            model_name='check_task',
            name='check_module',
            field=models.ForeignKey(to='home_application.CheckModule'),
        ),
    ]
