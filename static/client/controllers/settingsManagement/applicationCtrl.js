/**
 * Created by Administrator on 2017/6/13.
 */
controllers.controller("applicationCtrl", ["$scope","$modal","errorModal","settingsService", "msgModal", "confirmModal","loading",function ($scope,$modal,errorModal,settingsService, msgModal, confirmModal,loading) {
    var height = auto_height(195);
    $scope.add_business=function () {
        loading.open();
        $.post(site_url + "is_integrated",function (res) {
            loading.close();
            if (res.result){
                errorModal.open(['你已集成，无需添加业务！']);
            }
            else{
                loading.open();
                $.post(site_url + "add_business_page/", function (res) {
                loading.close();
                var d = dialog({
                    width: 500,
                    title: '添加业务',
                    content: res,
                    okValue: '确定',
                    ok: function () {
                        var dict = {businesses: selectItems};
                        var data = JSON.stringify(dict);
                        console.log(data);
                        $.post(site_url + "add_business", {
                            data: data
                        }, function (res) {
                            console.log(res);
                            if (!res.is_success) {
                                app_alert(res.message);
                                return false;
                            }
                            else {
                                selectItems.splice(0, selectItems.length);
                                $scope.searchObj();
                            }
                        })
                    },
                    cancelValue: '取消',
                    cancel: function () {
                        selectItems.splice(0, selectItems.length);
                        // do something
                    },
                    onshow: function () {
                        // do something
                    }
                });
                d.showModal();
                })
            }
        });
    };

    $scope.filterObj = {
        name: "",
        when_created: ""
    };
    $scope.businessList = [];
    $scope.Pagingdata = [];
    $scope.totalSerItems = 0;

    $scope.pagingOptions = {
        pageSizes: [10, 50, 100],
        pageSize: "10",
        currentPage: 1
    };
    $scope.condition="";
    $scope.searchObj = function () {
        console.log($scope.condition);
        settingsService.get_business_list({},{'app_name':$scope.condition}, function (res) {
            if (res.is_success) {
                $scope.businessList = res.data;

                $scope.pagingOptions.currentPage = 1;
                $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
            }
            else {
                errorModal.open(res.data);
            }
        })
    };

    $scope.getPagedDataAsync = function (pageSize, page) {
        $scope.setPagingData($scope.businessList ? $scope.businessList : [], pageSize, page);
    };

    $scope.setPagingData = function (data, pageSize, page) {
        $scope.Pagingdata = data.slice((page - 1) * pageSize, page * pageSize);
        console.log($scope.Pagingdata);
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
            {field: 'name', displayName: '业务名称'},
            {field: 'when_created', displayName: '添加时间', width: 300},
            {
                displayName: '操作', width: 150,
                cellTemplate: '<div style="width:100%;padding-top:5px;text-align: center;">' +
                // '<span class="label label-sm label-info label-btn" ng-click="modifyServer(row.entity)">修改</span>&emsp;' +
                '<span class="label label-sm label-danger label-btn" ng-click="deleteServer(row)">删除</span>' +
                '</div>'
            }
        ]
    };


    $scope.deleteServer = function (row) {
        confirmModal.open({
            text: "请确认是否删除业务",
            confirmClick: function () {
                settingsService.delete_business({}, row.entity, function (res) {
                    if (res.is_success) {
                        $scope.businessList.splice(row.rowIndex, 1);
                        $scope.pagingOptions.currentPage = 1;
                        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
                    }
                    else {
                        errorModal.open(res.data);
                    }
                })
            }
        })
    };


    $scope.sync_business = function () {
        loading.open();
        $.post(site_url + "is_integrated",function (res) {
            loading.close();
            if (res.result){
                errorModal.open(['你已集成，无需同步信息！']);
            }
            else{
            confirmModal.open({
                text: "立即同步所有业务的服务器列表",
                confirmClick: function () {
                    loading.open();
                    settingsService.sync_business({}, {}, function (res) {
                        loading.close();
                        if (res.is_success) {
                            msgModal.open("success","同步成功")
                        }
                        else {
                            errorModal.open(res.data);
                        }
                    })
                }
            })
            };
        });
    };
}]);