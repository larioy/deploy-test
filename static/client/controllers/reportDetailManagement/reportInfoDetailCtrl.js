controllers.controller("reportInfoDetailCtrl", ["$scope", "reportService", "loading", "errorModal", "$stateParams", function ($scope, reportService, loading, errorModal, $stateParams) {
    $scope.reportId = $stateParams.report_id;
    $scope.server = $stateParams.server;
    $scope.when_created = $stateParams.when_created;
    $scope.Search_info = function () {
        loading.open();
        reportService.detail_total({}, {"id": $scope.reportId, "server": $scope.server}, function (res) {
            loading.close();
            var info = res.data['details'][0]['info'];
            $scope.info_status = [];
            $scope.info_log = [];
            $scope.info_processor = [];
            $scope.errors = {
                sys_error: {"partition": "", "service": ""},
                log_error: {"syserr": "", "apperr": ""},
                performance_error: {"memory_performance": "", "cpu_performance": "", "disk_performance": ""}
            };
            for (var i = 0; i < info.length; i++) {
                if (info[i]['detail_type'] == "partition") {
                    $scope.errors.sys_error.partition = "磁盘空间不足"
                }
                if (info[i]['detail_type'] == "service") {
                    $scope.errors.sys_error.service = "发现系统异常服务"
                }
                if (info[i]['detail_type'] == "syserr") {
                    $scope.errors.log_error.syserr = "发现系统错误日志"
                }
                if (info[i]['detail_type'] == "apperr") {
                    $scope.errors.log_error.apperr = "发现应用程序错误日志"
                }
                if (info[i]['detail_type'] == "cpu_performance") {
                    $scope.errors.performance_error.cpu_performance = "CPU性能不足"
                }
                if (info[i]['detail_type'] == "disk_performance") {
                    $scope.errors.performance_error.disk_performance = "磁盘性能不足"
                }
                if (info[i]['detail_type'] == "memory_performance") {
                    $scope.errors.performance_error.memory_performance = "内存性能不足"
                }
            }
        })
    };
    $scope.Search_info();
    $scope.Search_info_detail = function () {
        loading.open();
        reportService.search_info_detail({}, {"id": $scope.reportId, "server": $scope.server}, function (res) {
            loading.close();
            for (var i = 0; i < res.data.length; i++) {
                if (res.data[i]['info_name'] == 'apperr') {
                    $scope.apperr = res.data[i]['data']
                }
                if (res.data[i]['info_name'] == 'syserr') {
                    $scope.syserr = res.data[i]['data']
                }
                if (res.data[i]['info_name'] == 'service') {
                    $scope.service = res.data[i]['data']
                }
                if (res.data[i]['info_name'] == 'partition') {
                    $scope.partition = res.data[i]['data']
                }
                if (res.data[i]['info_name'] == 'cpu_performance') {
                    $scope.cpu_performance = res.data[i]['data']
                }
                if (res.data[i]['info_name'] == 'memory_performance') {
                    $scope.memory_performance = res.data[i]['data']
                }
                if (res.data[i]['info_name'] == 'disk_performance') {
                    $scope.disk_performance = res.data[i]['data']
                }
            }
            console.log($scope.partition);
        })
    };
    $scope.Search_info_detail();


    $scope.show = function ($event) {
        if ($($event.target).next().hasClass('is_show')) {
            $($event.target).css({"borderBottom": 0});
            $($event.target).next().removeClass("is_show");
            $($event.target).children("i").css({"transform": "rotate(90deg)"})
        } else {
            $($event.target).css({"borderBottom": "1px solid #ccc"});
            $($event.target).next().addClass("is_show");
            $($event.target).children("i").css({"transform": "rotate(0deg)"})
        }
    }
}]);