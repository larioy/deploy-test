var app = angular.module("myApp", ['myController', 'utilServices', 'myDirective', 'ui.bootstrap', 'ui.router', 'webApiService','cwLeftMenu','ngGrid']);
var controllers = angular.module("myController", []);
var directives = angular.module("myDirective", []);


app.config(["$stateProvider", "$urlRouterProvider", "$httpProvider", function ($stateProvider, $urlRouterProvider, $httpProvider) {
    $httpProvider.defaults.headers.post['X-CSRFToken'] = $("#csrf").val();
    $urlRouterProvider.otherwise("/home");//默认展示页面
    $stateProvider.state('home', {
        url: "/home",
        controller: "home",
        templateUrl: static_url + "client/views/home.html"
    })
    //巡检管理
    .state('checkSearch', {
        url: "/checkSearch",
        controller: "checkSearchCtrl",
        templateUrl: static_url + "client/views/checkManagement/checkSearch.html"
    })
    .state('checkAdd', {
        url: "/checkAdd",
        controller: "checkAddCtrl",
        templateUrl: static_url + "client/views/checkManagement/checkAdd.html"
    })
    .state('checkModify', {
        url: "/checkModify?id",
        controller: "checkModifyCtrl",
        templateUrl: static_url + "client/views/checkManagement/checkModify.html"
    })
    .state('checkItem', {
        url: "/checkItem",
        controller: "checkItemCtrl",
        templateUrl: static_url + "client/views/checkManagement/checkItem.html"
    }).state('checkTotalReport', {
        url: "/checkTotalReport",
        controller: "checkTotalReportCtrl",
        templateUrl: static_url + "client/views/checkManagement/checkTotalReport.html"
    })
    .state('checkReport', {
        url: "/checkReport",
        controller: "checkReportCtrl",
        templateUrl: static_url + "client/views/checkManagement/checkReport.html"
    })
    .state('moduleAdd', {
        url: "/moduleAdd",
        controller: "moduleAddCtrl",
        templateUrl: static_url + "client/views/moduleManagement/moduleAdd.html"
    })
    .state('moduleList', {
        url: "/moduleList",
        controller: "moduleListCtrl",
        templateUrl: static_url + "client/views/moduleManagement/moduleList.html"
    })
    .state('customItem', {
        url: "/customItem",
        controller: "customItemCtrl",
        templateUrl: static_url + "client/views/checkManagement/customItem.html"
    })
    // //配置管理
    //  .state('newConfig', {
    //     url: "/newConfig",
    //     controller: "newConfigCtrl",
    //     templateUrl: static_url + "client/views/configManagement/newConfig.html"
    // })
    //系统设置
    .state('operationLog', {
        url: "/operationLog",
        controller: "operationLogCtrl",
        templateUrl: static_url + "client/views/sysManagement/operationLog.html"
    })
    // .state('customManagement', {
    //     url: "/customManagement",
    //     controller: "customManagementCtrl",
    //     templateUrl: static_url + "client/views/sysManagement/customManagement.html"
    // })
    .state('mailManagement', {
        url: "/mailManagement",
        controller: "mailManagementCtrl",
        templateUrl: static_url + "client/views/sysManagement/mailManagement.html"
    })
    // .state('application', {
    //     url: "/application",
    //     controller: "applicationCtrl",
    //     templateUrl: static_url + "client/views/settingsManagement/application.html"
    // })
    .state('setConfig', {
        url: "/setConfig",
        controller: "setConfigCtrl",
        templateUrl: static_url + "client/views/settingsManagement/setConfig.html"
    })
     .state('taskReportDetail', {
        url: "/taskReportDetail?id",
        controller: "taskReportDetailCtrl",
        templateUrl: static_url + "client/views/reportDetailManagement/taskReportDetail.html"
    }).state('reportInfoDetail', {
        url: "/reportInfoDetail?report_id&server&when_created",
        controller: "reportInfoDetailCtrl",
        templateUrl: static_url + "client/views/reportDetailManagement/reportInfoDetail.html"
    })
}]);
