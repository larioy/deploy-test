controllers.controller("customItemCtrl", function ($scope, $modal, loading, errorModal, checkService, msgModal,confirmModal) {
    $scope.filterObj = {
        name: ""
    };

    $scope.Pagingdata = [];
    $scope.totalSerItems = 0;

    $scope.pagingOptions = {
        pageSizes: [10, 50, 100],
        pageSize: "10",
        currentPage: 1
    };
    $scope.itemList = [];
    $scope.searchObj = function () {
        checkService.get_item_list({},$scope.filterObj, function (res) {
            console.log(res);
            if (res.result) {
                $scope.itemList = res.data;
                $scope.pagingOptions.currentPage = 1;
                $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);

            }
            else {
                errorModal.open(res.data);
            }
        })
    };

    $scope.getPagedDataAsync = function (pageSize, page) {
        $scope.setPagingData($scope.itemList ? $scope.itemList : [], pageSize, page);
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

    $scope.addItem = function () {
        var modalInstance = $modal.open({
            templateUrl: static_url + 'client/views/checkManagement/customItemAdd.html',
            windowClass: 'dialog_custom_item',
            controller: 'customItemAddCtrl',
            backdrop: 'static'
        });
        modalInstance.result.then(function () {
            $scope.searchObj();
        })
    };

    // $scope.modifyItem = function (rowEntity) {
    //     var modalInstance = $modal.open({
    //         templateUrl: static_url + 'client/views/checkManagement/customItemAdd.html',
    //         windowClass: 'dialog_custom_item',
    //         controller: 'customItemModifyCtrl',
    //         backdrop: 'static',
    //         resolve: {
    //             itemObj: function () {
    //                 return rowEntity;
    //             }
    //         }
    //     });
    //     modalInstance.result.then(function () {
    //       $scope.searchObj();
    //
    //     })
    // };

    $scope.gridOption = {
        data: "Pagingdata",
        enablePaging: true,
        showFooter: true,
        pagingOptions: $scope.pagingOptions,
        totalServerItems: 'totalSerItems',
        columnDefs: [
            {field: 'name', displayName: '巡检字段', width: 100},
            {field: 'cn_name', displayName: '巡检项名称', width: 100},
            {field: 'description', displayName: '描述'},
            {field: 'when_created', displayName: '添加时间', width: 150},
            {
                displayName: '操作', width: 150,
                cellTemplate: '<div style="width:100%;padding-top:5px;text-align: center;">' +
                // '<span title="编辑" class="fa fa-pencil fa-lg onoperate " style="color:blue;cursor: pointer;" ng-click="modifyItem(row.entity)"></span>&emsp;' +
                '<span title="删除" class="fa fa-trash-o fa-lg onoperate" style="color:red;cursor: pointer" ng-click="deleteItem(row)"></span>' +
                '</div>'
            }
        ]
    };

    $scope.deleteItem = function (row) {
        confirmModal.open({
            text: "请确认是否删除自定义巡检项",
            confirmClick: function () {
                loading.open();
                checkService.delete_custom_item({}, row.entity, function (res) {
                    loading.close();
                    if (res.result) {
                        msgModal.open("success", "删除成功！");
                        $scope.searchObj();
                    }
                    else {
                        errorModal.open([res.data]);
                    }
                })
            }
        })
    };
});