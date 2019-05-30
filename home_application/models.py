# -*- coding: utf-8 -*-

from django.db import models
import datetime


#  巡检类别
class CheckMenu(models.Model):
    menu_name = models.CharField(max_length=100)  # 类别
    name = models.CharField(max_length=100)
    is_show = models.BooleanField(default=True)  # 报告是否展示


# 巡检项
class CheckItem(models.Model):
    menu = models.ForeignKey(CheckMenu)
    name = models.CharField(max_length=100)  # 巡检项
    cn_name = models.CharField(max_length=100)  # 巡检名称
    compare_way = models.CharField(max_length=10, null=True, default="")  # 比较方式
    # compare_value = models.CharField(max_length=100, null=True, default="")  # 标准值
    description = models.TextField(null=True, default="")  # 备注
    can_modify = models.BooleanField(default=False)  # 是否允许修改标准值

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])


class CheckModule(models.Model):
    name = models.CharField(max_length=100)
    when_created = models.CharField(max_length=30)
    created_by = models.CharField(max_length=100)
    modified_by = models.CharField(max_length=100, default="")
    when_modified = models.CharField(max_length=30, default="")
    base_module_id = models.IntegerField(default=0)
    is_build_in = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    description = models.TextField(default="")

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])

    def create_item(self, dict_item):
        self.name = dict_item["name"]
        self.created_by = dict_item["created_by"]
        self.base_module_id = dict_item["base_module_id"]
        self.when_created = str(datetime.datetime.now()).split(".")[0]
        self.description = dict_item["description"]
        self.save()

    def modify_item(self, dict_item):
        self.name = dict_item["name"]
        self.base_module_id = dict_item["base_module_id"]
        self.when_modified = str(datetime.datetime.now()).split(".")[0]
        self.modified_by = dict_item["modified_by"]
        self.description = dict_item["description"]
        self.save()


class CheckItemValue(models.Model):
    check_item = models.ForeignKey(CheckItem)
    check_module = models.ForeignKey(CheckModule)
    value = models.TextField()


# Celery 任务时间设置
class Celery_time_set(models.Model):
    first_time = models.CharField(max_length=100)
    run_time = models.CharField(max_length=100)
    time_interval = models.IntegerField(default=0)
    set_type = models.CharField(max_length=10)
    interval_type = models.CharField(max_length=10, default=0)
    is_deleted = models.BooleanField(default=False)

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])


# 巡检任务
class Check_task(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.CharField(max_length=100)
    ip_list = models.TextField()
    is_deleted = models.BooleanField(default=False)
    modified_by = models.CharField(max_length=100)
    receivers = models.TextField()
    app_id_list = models.TextField(null=True)
    celery_time_set = models.OneToOneField(Celery_time_set)
    when_created = models.CharField(max_length=100)
    when_modified = models.CharField(max_length=100)
    account = models.CharField(max_length=50, default=u"Administrator")
    check_module = models.ForeignKey(CheckModule)

    def to_dic(self):
        temp_dict = dict(
            [(attr, getattr(self, attr))
             for attr in [f.name for f in self._meta.fields if f.name != "celery_time_set" and f.name != "check_module"]])
        temp_dict["celery_time_set"] = self.celery_time_set.to_dic()
        temp_dict["check_module"] = self.check_module.to_dic()
        temp_dict["check_module_id"] = self.check_module_id
        try:
            temp_dict["servers"] = eval(self.ip_list)
        except:
            temp_dict["server"] = []
        return temp_dict


# 巡检报告
class CheckReport(models.Model):
    check_task = models.ForeignKey(Check_task)
    when_created = models.CharField(max_length=100)
    report_info = models.CharField(max_length=200, null=True)  # 报告的概要：执行多少台服务器的巡检，完成几台
    status = models.CharField(max_length=100, null=True, default="RUNNING")  # 完成 COMPLETE，正在执行 RUNNING

    def to_dic(self):
        temp_dict = dict(
            [(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields if f.name != "check_task"]])
        temp_dict["check_task"] = self.check_task.to_dic()
        return temp_dict


class CheckReportDetail(models.Model):
    check_report = models.ForeignKey(CheckReport)
    server = models.CharField(max_length=100)
    source = models.IntegerField(default=1)
    app_id = models.IntegerField(default=1)
    server_info = models.TextField()
    is_success = models.BooleanField(default=True)
    fail_result = models.TextField(null=True, default="")

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])


class InfoDetail(models.Model):
    report_detail = models.ForeignKey(CheckReportDetail)
    is_show = models.BooleanField(default=True)
    check_item = models.ForeignKey(CheckItem)
    value = models.TextField()  # 巡检真实值
    is_warn = models.BooleanField(default=False)  # 巡检是否存在问题
    detail_type = models.CharField(max_length=100)  # 大项
    list_num = models.IntegerField(default=0)

    def to_dic(self):
        return {
            "report_detail": self.report_detail.to_dic(),
            "check_item": self.check_item.to_dic(),
            "value": self.value, "is_warn": self.is_warn, "detail_type": self.detail_type, "list_num": self.list_num
        }


class Logs(models.Model):
    operated_type = models.CharField(max_length=50)
    content = models.TextField()
    when_created = models.CharField(max_length=30)
    operator = models.CharField(max_length=50)

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])


# 业务
class Business(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    created_by = models.CharField(max_length=100)
    when_created = models.CharField(max_length=100)

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])


# 模块
class Module(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    business = models.ForeignKey(Business)

    def to_dic(self):
        temp_dict = dict(
            [(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields if f.name != 'business']])
        temp_dict["business"] = self.business.to_dic() if self.business else {}
        return temp_dict


# 服务器
class CheckServers(models.Model):
    module = models.ForeignKey(Module, null=True)
    ip = models.CharField(max_length=100)
    host_name = models.CharField(max_length=100)
    operation_system = models.CharField(max_length=200)
    source = models.CharField(max_length=100, null=True)
    is_deleted = models.BooleanField(default=False)

    def to_dic(self):
        temp_dict = dict(
            [(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields if f.name != 'module']])
        temp_dict["module"] = self.module.to_dic()
        return temp_dict


# 配置项
class ConfigItem(models.Model):
    menu_name = models.CharField(max_length=100)  # 类别
    object_name = models.CharField(max_length=100)  # 大项
    name = models.CharField(max_length=100)  # 巡检名称
    cn_name = models.CharField(max_length=100)  # 巡检项
    description = models.TextField(null=True, default="")
    is_show = models.BooleanField(default=False)
    is_build_in = models.BooleanField(default=True)

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])


# 服务器配置项
class ServerConfig(models.Model):
    # check_task  =models.ForeignKey(Check_task)
    check_server = models.ForeignKey(CheckServers)
    when_created = models.CharField(max_length=20)
    update_time = models.CharField(max_length=20, default="")


class CustomDetail(models.Model):
    check_server = models.ForeignKey(CheckServers)
    value = models.TextField()
    config_item = models.ForeignKey(ConfigItem)


# 配置项详情信息
class ConfigDetail(models.Model):
    server_config = models.ForeignKey(ServerConfig)
    config_item = models.ForeignKey(ConfigItem)
    value = models.TextField()
    detail_type = models.CharField(max_length=100)  # 大项
    list_num = models.IntegerField(default=0)  # 列表序号

    def to_dic(self):
        return {
            "server_config": self.server_config.to_dic(),
            "config_item": self.config_item.to_dic(),
            "value": self.value, "detail_type": self.detail_type, "list_num": self.list_num
        }


class Mailboxes(models.Model):
    username = models.CharField(max_length=50)
    mailbox = models.CharField(max_length=100)
    when_created = models.CharField(max_length=30)
    created_by = models.CharField(max_length=100, default="")

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])


class Settings(models.Model):
    key = models.CharField(max_length=50)
    value = models.TextField()
    description = models.CharField(max_length=100, null=True)

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])


class SetConfig(models.Model):
    created_by = models.CharField(max_length=100, default='')
    config_account = models.CharField(max_length=100, default="Administrator")
    report_num = models.IntegerField(default=0)
    sync_day = models.IntegerField(default=1)
    when_created = models.CharField(max_length=50, null=True, default='')


class CustomItem(models.Model):
    name = models.CharField(max_length=100)
    cn_name = models.CharField(max_length=100)
    description = models.TextField(default="", null=True)
    script_content = models.TextField()
    created_by = models.CharField(max_length=100)
    when_created = models.CharField(max_length=30)
    when_modified = models.CharField(max_length=30, default="")
    compare_way = models.CharField(max_length=10)
    compare_value = models.TextField()

    def to_dic(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])

    def create_item(self, dict_item):
        self.name = dict_item["name"]
        self.cn_name = dict_item["cn_name"]
        self.description = dict_item["description"]
        self.script_content = dict_item["script_content"]
        self.created_by = dict_item["created_by"]
        self.compare_way = dict_item["compare_way"]
        self.compare_value = dict_item["compare_value"]
        self.when_created = str(datetime.datetime.now()).split(".")[0]
        self.save()

    def modify_item(self, dict_item):
        self.name = dict_item["name"]
        self.cn_name = dict_item["cn_name"]
        self.description = dict_item["description"]
        self.script_content = dict_item["script_content"]
        self.when_modified = str(datetime.datetime.now()).split(".")[0]
        self.compare_way = dict_item["compare_way"]
        self.compare_value = dict_item["compare_value"]
        self.save()


class CustomItemValue(models.Model):
    custom_item = models.ForeignKey(CustomItem)
    check_module = models.ForeignKey(CheckModule)
    value = models.TextField()


# 巡检报告详情
class CustomReportDetail(models.Model):
    custom_item = models.ForeignKey(CustomItem)
    check_report_detail = models.ForeignKey(CheckReportDetail)
    value = models.TextField()
    is_success = models.BooleanField(default=True)

    def to_dic(self):
        temp_dict = dict(
            [(attr, getattr(self, attr)) for attr in
             [f.name for f in self._meta.fields if f.name != "custom_item" and f.name != "check_report_detail"]])
        temp_dict["custom_item"] = self.custom_item.to_dic()
        temp_dict["check_report_detail"] = self.check_report_detail.to_dic()
        return temp_dict
