controllers.controller("home", ["msgModal", "$scope", "loading", "sysService", function (msgModal, $scope, loading, sysService) {
    $scope.countObj = {};
    $scope.reportList = [];
    $scope.taskList = [];

    $scope.taskReports = {
        data: "taskList",
        chart: {type: 'line'},
        title: {text: '每月历史巡检次数统计', enabled: true},
        xAxis: {
            categories: []
        },
        //提示框位置和显示内容
        tooltip: {
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            '<td style="padding:0"><b>{point.y:f}</b></td></tr>',
            headerFormat: ""
        }
    };


    sysService.get_count_obj({}, {}, function (res) {
        console.log(res);
        if (res.is_success) {
            $scope.countObj = res.data.count_list;
            $scope.taskList = res.data.task_list.data;
            $scope.taskReports.xAxis.categories = res.data.task_list.categories;
            $scope.reportList = res.data.report_list;
        }
    });

    $scope.openReportDetail = function (id) {
        window.open(site_url + "checkReport/#/serverDetail?report_id=" + id);
    }
}]);
