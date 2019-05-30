controllers.controller("moduleListCtrl", function ($scope, confirmModal, moduleService, loading, msgModal, errorModal, $modal) {
    $scope.args = {
        name: ""
    };
    $scope.moduleList = [];
    $scope.PagingData = [];
    $scope.totalSerItems = 0;

    $scope.pagingOptions = {
        pageSizes: [10, 50, 100],
        pageSize: "10",
        currentPage: 1
    };

    $scope.searchList = function () {
        loading.open();
        moduleService.search_module_list({}, $scope.args, function (res) {
            loading.close();
            if (res.result) {
                $scope.taskList = res.data;
                $scope.pagingOptions.currentPage = 1;
                $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
            }
            else {
                errorModal.open(res.data);
            }
        })
    };

    $scope.getPagedDataAsync = function (pageSize, page) {
        $scope.setPagingData($scope.taskList ? $scope.taskList : [], pageSize, page);
    };
    $scope.setPagingData = function (data, pageSize, page) {
        $scope.PagingData = data.slice((page - 1) * pageSize, page * pageSize);
        $scope.totalSerItems = data.length;
        if (!$scope.$$phase) {
            $scope.$apply();
        }
    };

    $scope.$watch('pagingOptions', function (newVal, oldVal) {
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
    }, true);


    $scope.searchList();
    $scope.gridOption = {
        data: "PagingData",
        enablePaging: true,
        showFooter: true,
        pagingOptions: $scope.pagingOptions,
        totalServerItems: 'totalSerItems',
        columnDefs: [
            {field: "name", displayName: "模板名", width: 200},
            {field: "created_by", displayName: "创建者", width: 200},
            {field: "when_created", displayName: "创建时间", width: 150},
            {field: "description", displayName: "说明"},
            {
                displayName: "操作", width: 180,
                cellTemplate: '<div style="padding-top:5px;text-align: center;">' +
                '<span  ng-if="row.entity.is_build_in" class="label label-sm label-info label-btn" ng-click="checkModule(row.entity)">查看</span>' +
                '<span  ng-if="!row.entity.is_build_in" class="label label-sm label-info label-btn" ng-click="modifyModule(row.entity)">修改</span>' +
                '<span class="label label-sm label-danger label-btn" style="margin-left: 5px;" ng-if="!row.entity.is_build_in" ng-click="deleteModule(row)">删除</span>' +
                '</div>'
            }
        ]
    };

    $scope.modifyModule = function (rowEntity) {
        var modalInstance = $modal.open({
            templateUrl: static_url + 'client/views/moduleManagement/moduleModify.html',
            windowClass: 'dialog_module',
            controller: 'moduleModifyCtrl',
            backdrop: 'static',
            resolve: {
                itemObj: function () {
                    return angular.copy(rowEntity);
                }
            }
        });
        modalInstance.result.then(function () {
            $scope.searchList();

        })
    };

      $scope.checkModule = function (rowEntity) {
        var modalInstance = $modal.open({
            templateUrl: static_url + 'client/views/moduleManagement/moduleCheck.html',
            windowClass: 'dialog_module',
            controller: 'moduleModifyCtrl',
            backdrop: 'static',
            resolve: {
                itemObj: function () {
                    return rowEntity;
                }
            }
        });
    };


    $scope.deleteModule = function (row) {
        confirmModal.open({
            text: "是否要删除该模板",
            confirmClick: function () {
                loading.open();
                moduleService.delete_module({}, row.entity, function (res) {
                    loading.close();
                    if (res.result) {
                        msgModal.open("success", "删除成功");
                        $scope.searchList();
                    }
                    else {
                        errorModal.open(res.data);
                    }
                })
            }
        })
    };
});