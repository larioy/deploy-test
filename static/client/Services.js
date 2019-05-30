services = angular.module('webApiService', ['ngResource', 'utilServices']);

//生产代码
var POST = "POST";
var GET = "GET";

//测试代码
//var sourceRoute = "./Client/MockData";
//var fileType = ".html";
//var POST = "GET";
//var GET = "GET";
services.factory('sysService', ['$resource', function ($resource) {
    return $resource(site_url + ':actionName/', {},
        {
            search_log: {method: POST, params: {actionName: 'search_log'}, isArray: false},
            modify_mail: {method: POST, params: {actionName: 'modify_mail'}, isArray: false},
            delete_mail: {method: POST, params: {actionName: 'delete_mail'}, isArray: false},
            search_mail: {method: POST, params: {actionName: 'search_mail'}, isArray: false},
            add_mail: {method: POST, params: {actionName: 'add_mail'}, isArray: false},
            update_url: {method: POST, params: {actionName: 'update_url'}, isArray: false},
            get_count_obj: {method: POST, params: {actionName: 'get_count_obj'}, isArray: false},
            search_custom: {method: POST, params: {actionName: 'search_custom'}, isArray: false},
            add_custom: {method: POST, params: {actionName: 'add_custom'}, isArray: false},
            delete_custom: {method: POST, params: {actionName: 'delete_custom'}, isArray: false},
            search_business_servers: {method: POST, params: {actionName: 'search_business_servers'}, isArray: false},
            search_business_topo: {method: POST, params: {actionName: 'search_business_topo'}, isArray: false},
            search_module_servers: {method: POST, params: {actionName: 'search_module_servers'}, isArray: false},
            get_check_servers: {method: POST, params: {actionName: 'get_check_servers'}, isArray: false},
            get_all_mail: {method: POST, params: {actionName: 'get_all_mail'}, isArray: false},

        });
}])
.factory('taskService', ['$resource', function ($resource) {
    return $resource(site_url + ':actionName/', {}, {
        search_task: {method: POST, params: {actionName: 'search_task'}, isArray: false},
        set_task: {method: POST, params: {actionName: 'set_task'}, isArray: false},
        run_task: {method: POST, params: {actionName: 'run_task'}, isArray: false},
        set_check_content: {method: POST, params: {actionName: 'set_check_content'}, isArray: false},
        search_check_content: {method: POST, params: {actionName: 'search_check_content'}, isArray: false},
    });
}])
.factory('reportService', ['$resource', function ($resource) {
    return $resource(site_url + ':actionName/', {}, {
        // search_report: {method: POST, params: {actionName: 'search_report'}, isArray: false},
        // get_check_server: {method: POST, params: {actionName: 'get_check_server'}, isArray: false},
        // get_status_info: {method: POST, params: {actionName: 'get_status_info'}, isArray: false},
        // get_check_logs: {method: POST, params: {actionName: 'get_check_logs'}, isArray: false},
        detail_total: {method: POST, params: {actionName: 'detail_total'}, isArray: false},
        search_info_detail: {method: POST, params: {actionName: 'search_info_detail'}, isArray: false},
    });
}])
.factory('checkService', ['$resource', function ($resource) {
    return $resource(site_url + ':actionName/', {}, {
        get_account: {method: POST, params: {actionName: 'get_account'}, isArray: false},
        get_sys_tree: {method: POST, params: {actionName: 'get_sys_tree'}, isArray: false},
        get_module_server: {method: POST, params: {actionName: 'get_module_server'}, isArray: false},
        get_server_by_module_id: {method: POST, params: {actionName: 'get_server_by_module_id'}, isArray: false},
        get_module_by_app_id: {method: POST, params: {actionName: 'get_module_by_app_id'}, isArray: false},
        search_servers: {method: POST, params: {actionName: 'search_servers'}, isArray: false},
        search_check_task: {method: POST, params: {actionName: 'search_check_task'}, isArray: false},
        modify_check_task: {method: POST, params: {actionName: 'modify_check_task'}, isArray: false},
        delete_check_task: {method: POST, params: {actionName: 'delete_check_task'}, isArray: false},
        start_task: {method: POST, params: {actionName: 'start_task'}, isArray: false},
        search_check_item: {method: POST, params: {actionName: 'search_check_item'}, isArray: false},
        modify_check_item: {method: POST, params: {actionName: 'modify_check_item'}, isArray: false},
        search_check_report: {method: POST, params: {actionName: 'search_check_report'}, isArray: false},
        get_modify_check_task: {method: POST, params: {actionName: 'get_modify_check_task'}, isArray: false},
        get_chart_list: {method: POST, params: {actionName: 'get_chart_list'}, isArray: false},
        get_ip_list: {method: POST, params: {actionName: 'get_ip_list'}, isArray: false},
        get_servers_by_appid: {method: POST, params: {actionName: 'get_servers_by_appid'}, isArray: false},
        get_item_list: {method: POST, params: {actionName: 'get_item_list'}, isArray: false},
        create_custom_item: {method: POST, params: {actionName: 'create_custom_item'}, isArray: false},
        delete_custom_item: {method: POST, params: {actionName: 'delete_custom_item'}, isArray: false},
        modify_custom_item: {method: POST, params: {actionName: 'modify_custom_item'}, isArray: false},
        get_task_option: {method: POST, params: {actionName: 'get_task_option'}, isArray: false},
        create_check_task: {method: POST, params: {actionName: 'create_check_task'}, isArray: false},

    });
}])
.factory('moduleService', ['$resource', function ($resource) {
    return $resource(site_url + ':actionName/', {}, {
        get_module_list: {method: POST, params: {actionName: 'get_module_list'}, isArray: false},
        get_module_item_list: {method: POST, params: {actionName: 'get_module_item_list'}, isArray: false},
        create_module: {method: POST, params: {actionName: 'create_module'}, isArray: false},
        modify_module: {method: POST, params: {actionName: 'modify_module'}, isArray: false},
        delete_module: {method: POST, params: {actionName: 'delete_module'}, isArray: false},
        search_module_list: {method: POST, params: {actionName: 'search_module_list'}, isArray: false},
    });
}])
.factory('settingsService', ['$resource', function ($resource) {
    return $resource(site_url + ':actionName/', {}, {
        get_business_list: {method: POST, params: {actionName: 'get_business_list'}, isArray: false},
        sync_business: {method: POST, params: {actionName: 'sync_business'}, isArray: false},
        delete_business: {method: POST, params: {actionName: 'delete_business'}, isArray: false},
        add_server_config: {method: POST, params: {actionName: 'add_server_config'}, isArray: false},
        search_server_config: {method: POST, params: {actionName: 'search_server_config'}, isArray: false},
        delete_server_config: {method: POST, params: {actionName: 'delete_server_config'}, isArray: false},
        search_server_config_detail: {method: POST, params: {actionName: 'search_server_config_detail'}, isArray: false},
        get_set_config: {method: POST, params: {actionName: 'get_set_config'}, isArray: false},
        modify_set_config: {method: POST, params: {actionName: 'modify_set_config'}, isArray: false},
        start_sync_business: {method: POST, params: {actionName: 'start_sync_business'}, isArray: false},
        modify_custom_detail: {method: POST, params: {actionName: 'modify_custom_detail'}, isArray: false},
    });
}])
;//这是结束符，请勿删除