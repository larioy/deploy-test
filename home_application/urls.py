# -*- coding: utf-8 -*-

from django.conf.urls import patterns
import settings_views, check_views, report_detail_views, home_view

urlpatterns = patterns(
    'home_application.views',
    # 首页--your index
    (r'^$', 'home'),
    (r'^add_business_page', 'add_business_page'),
    (r'^checkReport', 'checkReport'),
    # 服务器主机查询功能
    (r'^search_business_servers$', 'search_business_servers'),
    (r'^search_business_topo$', 'search_business_topo'),
    (r'^search_module_servers/$', 'search_module_servers'),
    (r'^get_check_servers$', 'get_check_servers'),
    # 系统管理
    (r'^search_log$', 'search_log'),

    # check_views
    (r'^get_account$', check_views.get_account),
    (r'^create_check_task$', check_views.create_check_task),
    (r'^search_check_task$', check_views.search_check_task),
    (r'^delete_check_task$', check_views.delete_check_task),
    (r'^modify_check_task$', check_views.modify_check_task),
    (r'^start_task$', check_views.start_task),
    (r'^search_check_item$', check_views.search_check_item),
    (r'^modify_check_item$', check_views.modify_check_item),
    (r'^search_check_report$', check_views.search_check_report),
    (r'^get_modify_check_task$', check_views.get_modify_check_task),
    (r'^get_chart_list$', check_views.get_chart_list),
    (r'^get_ip_list$', check_views.get_ip_list),

    (r'^get_item_list', 'get_item_list'),
    (r'^create_custom_item', 'create_custom_item'),
    (r'^delete_custom_item', 'delete_custom_item'),
    (r'^modify_custom_item', 'modify_custom_item'),
    # sys_views
    # 邮箱管理
    (r'^add_mail$', 'add_mail'),
    (r'^delete_mail$', 'delete_mail'),
    (r'^search_mail$', 'search_mail'),
    (r'^update_url$', 'update_url'),
    (r'^get_all_mail$', 'get_all_mail'),
    # settings_views
    # 业务管理
    (r'^get_set_config$', settings_views.get_set_config),
    (r'^modify_set_config$', settings_views.modify_set_config),
    (r'^search_info_detail$', report_detail_views.search_info_detail),
    (r'^detail_total$', report_detail_views.detail_total),
    # home_view
    (r'^get_count_obj$', home_view.get_count_obj),
    # 模板管理
    (r'^get_module_item_list$', 'get_module_item_list'),
    (r'^search_module_list$', 'search_module_list'),
    (r'^get_module_list$', 'get_module_list'),
    (r'^create_module$', 'create_module'),
    (r'^modify_module$', 'modify_module'),
    (r'^delete_module$', 'delete_module'),
    (r'^get_task_option$', check_views.get_task_option),

)
