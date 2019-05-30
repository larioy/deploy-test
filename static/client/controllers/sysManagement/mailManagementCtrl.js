controllers.controller("mailManagementCtrl", ["$scope", "errorModal", "$modal", "loading", "confirmModal", "sysService", function ($scope, errorModal, $modal, loading, confirmModal, sysService) {
    $scope.args = {
        username: "",
        mailbox: ""
    };

    $scope.ObjList = [];
    $scope.Pagingdata = [];
    $scope.totalSerItems = 0;
    $scope.pagingOptions = {
        pageSizes: [10, 50, 100],
        pageSize: "10",
        currentPage: 1
    };
    $scope.search_mail = function () {
        loading.open();
        sysService.search_mail({}, $scope.args, function (res) {
            loading.close();
            if (res.result) {
                $scope.ObjList = res.data;
                $scope.pagingOptions.currentPage = 1;
                $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
            }
            else {
                errorModal.open(res.data.split(";"));
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

    $scope.search_mail();

    $scope.add_mail = function () {
        var modalInstance = $modal.open({
            templateUrl: static_url + 'client/views/sysManagement/mailManagementOperation.html',
            windowClass: 'dialog_custom',
            controller: 'mailAddCtrl',
            backdrop: 'static',
            resolve: {
                objectItem: function () {
                    return $scope.username
                }
            }
        });
        modalInstance.result.then(function (res) {
            // $scope.ObjList.unshift(res);
            for (var i in res) {
                $scope.ObjList.unshift(res[i]);
            }
            $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
        })
    };

    $scope.modify_mail = function (row) {
        var modalInstance = $modal.open({
            templateUrl: static_url + 'client/views/sysManagement/mailManagementOperation.html',
            windowClass: 'dialog_custom',
            controller: 'mailModifyCtrl',
            backdrop: 'static',
            resolve: {
                objectItem: function () {
                    return row.entity;
                }
            }
        });
        modalInstance.result.then(function (res) {
            row.entity.username = res.username;
            row.entity.mailbox = res.mailbox;
            row.entity.when_created = res.when_created;
        })
    };

    $scope.delete_mail = function (row) {
        var id = row.entity.id;
        confirmModal.open({
            text: "确认删除该邮箱吗？",
            confirmClick: function () {
                sysService.delete_mail({id: id}, {}, function (res) {
                    if (res.result) {
                        $scope.ObjList.splice(row.rowIndex, 1);
                        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
                    }
                    else {
                        errorModal.open(res.data.split(";"));
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
            {field: 'username', displayName: '用户名'},
            {field: 'mailbox', displayName: '邮箱地址'},
            {field: 'when_created', displayName: '添加时间'},
            {field: 'created_by', displayName: '创建者'},
            {
                displayName: '操作', width: 180,
                cellTemplate: '<div style="width:100%;text-align: center;padding-top: 5px;z-index: 1">' + '<span ng-click="delete_mail(row)" class="label label-danger" style="min-width:50px;margin-left: 5px;cursor:pointer;">删除</span>' +
                '</div>'
            }

        ]
    };
}]);



