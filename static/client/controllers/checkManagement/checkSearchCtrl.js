controllers.controller("checkSearchCtrl", ["$scope","msgModalN","checkService","errorModal","confirmModal","loading",function ($scope,msgModalN,checkService,errorModal,confirmModal,loading) {

    $scope.ObjList = [];
    $scope.Pagingdata = [];
    $scope.totalSerItems = 0;

    $scope.pagingOptions = {
        pageSizes: [10, 50, 100],
        pageSize: "10",
        currentPage: 1
    };
    $scope.task_name="";
    $scope.task_type="";
    $scope.searchObj = function () {
        checkService.search_check_task({},{'time_type':$scope.task_type,'name':$scope.task_name}, function (res) {
            if (res.is_success) {
                for (var i = 0; i < res.data.length; i++) {
                    if (res.data[i].celery_time_set.set_type == "TIMER"){
                        res.data[i].run_type_value = "定时";
                        res.data[i].when_modified = res.data[i]['celery_time_set']['run_time']
                    }
                    else if (res.data[i].celery_time_set.set_type == "NOW"){
                        res.data[i].run_type_value = "立即";
                    }
                    else{
                        res.data[i].run_type_value = "周期";
                        res.data[i].when_modified = res.data[i]['celery_time_set']['run_time']
                    }
                }
                $scope.ObjList = res.data;
                $scope.pagingOptions.currentPage = 1;
                $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
            }
            else {
                errorModal.open(res.message);
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
    $scope.searchObj();


    $scope.gridOption = {
        data: "Pagingdata",
        enablePaging: true,
        showFooter: true,
        pagingOptions: $scope.pagingOptions,
        totalServerItems: 'totalSerItems',
        columnDefs: [
            {field: 'name', displayName: '任务名称'},
            {field: 'modified_by', displayName: '创建者',width:100},
            {field: 'when_created', displayName: '创建时间',width:160},
            {field: 'run_type_value', displayName: '创建类型', width: 200},
            {field: 'when_modified', displayName: '下一次巡检时间',width:160},
            {
                displayName: '操作', width: 150,
                cellTemplate: '<div style="width:100%;padding-top:5px;text-align: center;">' +
                '<span title="立即巡检" class="fa fa-stethoscope fa-lg onoperate" style="cursor: pointer;" ng-click="run_task_now(row.entity)"></span>&emsp;' +
                '<span title="编辑" class="fa fa-pencil fa-lg onoperate " style="color:blue;cursor: pointer;" ui-sref="checkModify({id:row.entity.id})"></span>&emsp;' +
                '<span title="删除" class="fa fa-trash-o fa-lg onoperate" style="color:red;cursor: pointer" ng-click="deleteServer(row.entity)"></span>' +
                '</div>'
            }
        ]
    };

    $scope.deleteServer = function (row) {
        confirmModal.open({
            text: "请确认是否删除任务",
            confirmClick: function () {
                checkService.delete_check_task({}, row, function (res) {
                    if (res.is_success) {
                        $scope.searchObj();
                    }
                    else {
                        errorModal.open(res.data);
                    }
                })
            }
        })
    };

    $scope.modifyServer = function(row){
        console.log(row);
        // checkService.modify_check_task({},{'id':row.id},function(res){
        //     console.log(res)
        // });
    };

     $scope.run_task_now=function(row) {
         loading.open();
         checkService.start_task({},{'task_id':row.id},function(res){
            loading.close();
            if (res.is_success) {
                msgModalN.open("启动成功！");
                window.location.href = site_url + "#/checkReport";
            } else {
                app_alert(res.message);
            }
         });

    }
}]);