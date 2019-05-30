controllers.controller("site", ["$scope", "sysService", function ($scope, sysService) {
    $scope.menuList = [
        {
            displayName: "首页", iconClass: "fa fa-home fa-lg", url: "#/home"
        },
        {
            displayName: "模板管理", iconClass: "fa fa-th-large fa-lg",
            children: [
                {displayName: "新增模板", url: "#/moduleAdd"},
                {displayName: "模板列表", url: "#/moduleList"}
            ]
        },
        {
            displayName: "巡检管理", iconClass: "fa fa-fw fa-stethoscope",
            children: [
                {displayName: "巡检任务管理", url: "#/checkSearch"},
                // {displayName: "巡检标准管理", url: "#/checkItem"}
            ]
        },
        {
            displayName: "报告中心", iconClass: "fa fa-fw fa-file-text",
            children: [
                {displayName: "巡检报告", url: "#/taskReportDetail"},
                {displayName: "历史报告", url: "#/checkReport"},
                {displayName: "趋势报告", url: "#/checkTotalReport"},
            ]
        },
        // {
        //     displayName: "配置管理", iconClass: "fa fa-shield fa-lg",
        //     children: [
        //         {displayName: "服务器配置", url: "#/newConfig"},
        //     ]
        // },
        {
            displayName: "系统设置", iconClass: "fa fa-cog fa-lg",
            children: [
                // {displayName: "业务管理", url: "#/application"},
                // {displayName: "全局配置", url: "#/setConfig"},
                // {displayName: "自定义属性", url: "#/customManagement"},
                {displayName: "自定义巡检项", url: "#/customItem"},
                {displayName: "邮箱管理", url: "#/mailManagement"},
                {displayName: "操作日志", url: "#/operationLog"}
            ]
        }

    ];


    $scope.menuOption = {
        data: 'menuList',
        locationPlaceHolder: '#locationPlaceHolder',
        adaptBodyHeight: CWApp.HeaderHeight + CWApp.FooterHeight
    };

    sysService.update_url({
        app_path: app_path
    }, {}, function (res) {

    })

}]);