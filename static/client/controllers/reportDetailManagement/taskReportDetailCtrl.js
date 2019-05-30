controllers.controller("taskReportDetailCtrl", ["$scope", "reportService", "loading", "errorModal", "$stateParams", "msgModalN", function ($scope, reportService, loading, errorModal, $stateParams, msgModalN) {
    $scope.ObjList = "";
    $scope.reportId = $stateParams.id;
    loading.open();
    $scope.Search = function () {
        reportService.detail_total({}, {"id": $scope.reportId, "server": ""}, function (res) {
            loading.close();
            if (res.is_success) {
                $scope.ObjList = res.data;
            } else {
                msgModalN.open(res.message)
            }
        })
    };
    $scope.Search();

    $scope.show_total = function ($event) {
        if ($($event.currentTarget).parent('.report_content_total').next('.report_content_error').hasClass('report_open')) {
            $($event.currentTarget).parent('.report_content_total').next('.report_content_error').removeClass('report_open');
            $($event.currentTarget).children(' .glyphicon').css({"transform": "rotate(180deg)"})
        } else {
            $($event.currentTarget).parent('.report_content_total').next('.report_content_error').addClass('report_open');
            $($event.currentTarget).children(' .glyphicon').css({"transform": "rotate(0deg)"})
        }
    };
    $scope.go_back = function () {
        $scope.info_show = true;
    };

    $scope.info_show = true;
    $scope.reportInfoDetail = function (row) {
        $scope.reportId = row.report_id;
        $scope.server = row.server;
        $scope.report_detail_id = row.report_detail_id;
        $scope.when_created = row.when_created;
        $scope.Search_info();
        $scope.Search_info_detail();
        $scope.info_show = false;
    };
    //详情页

    $scope.Search_info = function () {
        loading.open();
        reportService.detail_total({}, {"id": $scope.reportId, "server": $scope.server, "report_detail_id": $scope.report_detail_id}, function (res) {
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

    $scope.Search_info_detail = function () {
        loading.open();
        reportService.search_info_detail({report_detail_id: $scope.report_detail_id}, {}, function (res) {
            loading.close();
            $scope.apperr = res.data.apperr;
            $scope.syserr = res.data.syserr;
            $scope.service = res.data.service;
            $scope.partition = res.data.partition;
            $scope.cpu_performance = res.data.cpu_performance;
            $scope.memory_performance = res.data.memory_performance;
            $scope.disk_performance = res.data.disk_performance;
            $scope.custom_list = res.data.custom_list;
        })
    };

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