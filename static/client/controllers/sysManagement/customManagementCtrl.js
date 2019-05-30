controllers.controller("customManagementCtrl", ["$scope", "$modal", "confirmModal", "sysService", "msgModal", "loading", "errorModal", function ($scope, $modal, confirmModal, sysService, msgModal, loading, errorModal) {
    $scope.args = {
        name: "",
    };

    $scope.ObjList = [];
    $scope.Pagingdata = [];
    $scope.totalSerItems = 0;
    $scope.pagingOptions = {
        pageSizes: [10, 50, 100],
        pageSize: "10",
        currentPage: 1
    };
    $scope.searchList = function () {
        loading.open();
        sysService.search_custom({}, $scope.args, function (res) {
            loading.close();
            if (res.result) {
                $scope.ObjList = res.data;
                $scope.pagingOptions.currentPage = 1;
                $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
            }
            else {
                errorModal.open(res.data);
            }
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

    $scope.searchList();

    $scope.addCustom = function () {
        var modalInstance = $modal.open({
            templateUrl: static_url + 'client/views/sysManagement/addCustom.html',
            windowClass: 'dialog_custom',
            controller: 'addCustomCtrl',
            backdrop: 'static'
        });
        modalInstance.result.then(function (res) {
            $scope.ObjList.unshift(res);
            $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
        })
    };


    $scope.deleteCustom = function (row) {
        var id = row.entity.id;
        confirmModal.open({
            text: "确认删除该自定义属性吗？",
            confirmClick: function () {
                sysService.delete_custom({id: id}, {}, function (res) {
                    if (res.result) {
                        $scope.ObjList.splice(row.rowIndex, 1);
                        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
                    }
                    else {
                        errorModal.open(res.data);
                    }
                })
            }
        })
    };


    $scope.gridOption = {
        data: 'Pagingdata',
        enablePaging: true,
        showFooter: true,
        pagingOptions: $scope.pagingOptions,
        totalServerItems: 'totalSerItems',
        columnDefs: [
            {field: 'cn_name', displayName: '显示名'},
            {field: 'name', displayName: '字段名'},
            {field: 'description', displayName: '备注'},
            {
                displayName: '操作', width: 180,
                cellTemplate: '<div style="width:100%;text-align: center;padding-top: 5px;z-index: 1">' +
                '<span ng-click="deleteCustom(row)" class="label label-danger" style="min-width:50px;margin-left: 5px;cursor:pointer;">删除</span>' +
                '</div>'
            }
        ]
    };
}]);