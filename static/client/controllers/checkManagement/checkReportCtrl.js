/**
 * Created by Administrator on 2017/6/13.
 */
controllers.controller("checkReportCtrl", ["$scope", "checkService", "errorModal", "$interval", function ($scope, checkService, errorModal, $interval) {
    var dataSource = [];
    var height = auto_height(215);

    $(function () {
        var bkArr = [
            {id: 'ALL', text: '所有'},
            {id: 'DONE', text: '完成'},
            //{id: 'FAIL', text: '失败'},
            {id: 'RUNNING', text: '进行中'}
        ];
        $("#result_select .select2_box").select2({data: bkArr});
        $("#result_select .select2_box").select2("val", "ALL");
        $("#report_list").css("height", height);
    });

    $scope.ObjList = [];
    $scope.Pagingdata = [];
    $scope.totalSerItems = 0;

    $scope.pagingOptions = {
        pageSizes: [10, 50, 100],
        pageSize: "10",
        currentPage: 1
    };
    $scope.taskName = "";
    $scope.Result = "";
    $scope.searchObj = function () {
        var result = $(".select2-hidden-accessible").text();
        if (result == "进行中") {
            $scope.Result = "RUNNING";
        }
        if (result == "完成") {
            $scope.Result = "COMPLETE";
        }
        if (result == "所有") {
            $scope.Result = "";
        }
        checkService.search_check_report({}, {'task_name': $scope.taskName, 'result': $scope.Result}, function (res) {
            console.log(res);
            if (res.is_success) {
                $scope.ObjList = res.data;
                $scope.pagingOptions.currentPage = 1;
                $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
            }
            else {
                errorModal.open(res.data);
                return
            }
            var is_auto = [];
            for (var i = 0; i < res['data'].length; i++) {
                if (res['data'][i]['status'] === "RUNNING") {
                    is_auto.push(res['data'][i]['status']);
                }
            }
            if (is_auto.length > 0 && window.location.href.indexOf("/checkReport") > -1) {
                setTimeout($scope.searchObj, 3000);
            }
            $(window).unload(function () {
                return
            });
        })
    };

    $scope.getPagedDataAsync = function (pageSize, page) {
        $scope.setPagingData($scope.ObjList ? $scope.ObjList : [], pageSize, page);
    };

    $scope.setPagingData = function (data, pageSize, page) {
        $scope.Pagingdata = data.slice((page - 1) * pageSize, page * pageSize);
        $scope.totalSerItems = data.length;
        if (!$scope.$$phase) {
            $scope.$apply();
        }
    };

    $scope.$watch('pagingOptions', function (newVal, oldVal) {
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
    }, true);
    $scope.searchObj();

    $scope.gridOption = {
        data: "Pagingdata",
        enablePaging: true,
        showFooter: true,
        pagingOptions: $scope.pagingOptions,
        totalServerItems: 'totalSerItems',
        columnDefs: [
            {field: 'check_task.name', displayName: '任务名称', width: 400},
            {field: 'when_created', displayName: '执行时间', width: 200},
            {field: 'report_info', displayName: '概况'},
            {
                displayName: "状态", width: 150,
                cellTemplate: '<div style="width:100%;padding-top:5px;text-align: center">' +
                '<span  ng-if="row.entity.status == \'RUNNING\'">' +
                '<i  class="fa fa-spinner fa-pulse"></i>\
                进行中</span>\
                <span  ng-if="row.entity.status == \'COMPLETE\'" >\
                 <i class="fa fa-check color_green"></i>\
                 完成</span>' +
                '</div>'
            },
            {
                displayName: "操作", width: 100,
                cellTemplate: '<div style="width:100%;padding-top:5px;text-align: center">' +
                '<span ng-if="row.entity.status == \'COMPLETE\'" ui-sref="taskReportDetail({id:row.entity.id})" class="king-btn king-primary king-btn-mini" >查看报告</span>' +
                '<span ng-if="row.entity.status == \'RUNNING\'" style="box-shadow:none;opacity:0.65" class="king-btn king-primary king-btn-mini" >查看报告</span>' +
                '</div>'
            }
        ]
    };


}]);