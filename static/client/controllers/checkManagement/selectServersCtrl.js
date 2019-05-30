controllers.controller("selectServersCtrl", ["$scope", "$filter", "sysService", "errorModal", "confirmModal", "loading", "$modalInstance", function ($scope, $filter, sysService, errorModal, confirmModal, loading, $modalInstance) {
    $scope.serverList = [];
    $scope.selectIndex = {value: "1"};
    $scope.businessTopo = [];
    $scope.filterObj = {
        ip: ""
    };
    $scope.all_server = [];
    $scope.Pagingdata = [];
    $scope.totalSerItems = 0;

    $scope.pagingOptions = {
        pageSizes: [7],
        pageSize: "7",
        currentPage: 1
    };

    $scope.changeType = function (i) {
        if(i === 1){
            $scope.all_selection.selectAll = false;
            $scope.selectedItems = [];
            $scope.filterObj.ip = "";
            $scope.serverList = angular.copy($scope.all_server);
            $scope.pagingOptions.currentPage = 1;
            $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
        }
        else if (i === 2 && $scope.businessTopo.length === 0) {
            $scope.search_business_topo();
        }
    };
    $scope.search_business_servers = function () {
        loading.open("", ".server-load");
        sysService.search_business_servers({}, {}, function (res) {
            loading.close(".server-load");
            if (res.result) {
                $scope.all_server = angular.copy(res.data);
                $scope.serverList = res.data;
                $scope.pagingOptions.currentPage = 1;
                $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
            }
            else {
                errorModal.open(res.data)
            }
        })
    };
    setTimeout($scope.search_business_servers, 500);

    $scope.getPagedDataAsync = function (pageSize, page) {
        $scope.setPagingData($scope.serverList ? $scope.serverList : [], pageSize, page);
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
    $scope.selectedItems = [];
    $scope.gridOption = {
        data: "Pagingdata",
        enablePaging: true,
        showFooter: true,
        pagingOptions: $scope.pagingOptions,
        totalServerItems: 'totalSerItems',
        enableColumnResize: true,
        enableRowSelection: true,
       // selectedItems: $scope.selectedItems,
        checkboxCellTemplate:'<div style="width:100%;padding:9px 5px;"><input type="checkbox" ng-change="change_select(row.entity)" ng-model="row.entity.is_checked" /></div>',
        checkboxHeaderTemplate:'<div style="width:100%;padding:9px 5px;"><input type="checkbox" ng-model="all_selection.is_select_all" ng-change="selectAll()" /></div>',
        showSelectionCheckbox: true,
        selectWithCheckboxOnly: true,
        // multiSelect: true,
        columnDefs: [
            {field: "source_name", displayName: "区域名称"},
            {field: "ip", displayName: "IP"},
            {field: "bk_os_name", displayName: "操作系统"}
        ]
    };

    $scope.all_selection = {is_select_all : false};
    $scope.selectAll =function(){
        angular.forEach($scope.Pagingdata,function(i){
            i.is_checked = $scope.all_selection.is_select_all;
        })
        angular.forEach($scope.serverList,function(i){
            i.is_checked = $scope.all_selection.is_select_all;
        })
        if ($scope.all_selection.is_select_all){
           $scope.selectedItems = angular.copy($scope.serverList);
        }
        else{
            $scope.selectedItems = [];
        }
    };

    $scope.change_select = function (rowEntity){
        if(rowEntity.is_checked){
            $scope.selectedItems.push(rowEntity);
        }
        else{
            var tmp = angular.copy($scope.selectedItems);
            for(var i in $scope.selectedItems){
                if($scope.selectedItems[i].ip === rowEntity.ip && $scope.selectedItems[i].source === rowEntity.source){
                    tmp.splice(i,1);
                    break;
                }
            }
            $scope.selectedItems = angular.copy(tmp);
        }

    };
    $scope.search_business_topo = function () {
        loading.open("", ".server-load");
        sysService.search_business_topo({}, {}, function (res) {
            loading.close(".server-load");
            if (res.result) {
                $scope.businessTopo = res.data;
            }
            else {
                errorModal.open(res.data);
            }
        })
    };

    $scope.zTreeOptions = {
        check: {
            enable: true
        },
        data: {
            key: {
                name: "bk_inst_name",
                children: "child",
                isParent: "isParent",
                checked: "checked"
            }
        },
        asyncUrl: site_url + 'search_module_servers/',
        autoParam: ["bk_inst_id=bk_inst_id", 'bk_biz_id=bk_biz_id'],
        onCheck: function (event, treeId, treeNode) {
            if (treeNode.checked)
                $scope.check_all_servers(event, treeId, treeNode);
        }
    };

    $scope.check_all_servers = function (event, treeId, treeNode) {
        if (treeNode.is_open_all) {
            return;
        }
        treeNode.is_open_all = true;
        if (treeNode.bk_obj_name === "IP") {
            return;
        }
        if (treeNode.child.length > 0 && treeNode.child[0].bk_obj_name === 'IP') {
            return;
        }
        loading.open("", ".server-load");
        sysService.get_check_servers({}, treeNode, function (res) {
            loading.close(".server-load");
            if (res.data.length === 0) {
                return;
            }
            var treeObj = $.fn.zTree.getZTreeObj("businessTopo");
            treeObj.removeChildNodes(treeNode);
            for (var i = 0; i < res.data.length; i++) {
                treeObj.addNodes(treeNode, res.data[i]);
            }
        })
    };

    $scope.moduleServers = [];

    $scope.selectServers = [];
    $scope.confirm = function () {
        if ($scope.selectIndex.value == '1') {
            $modalInstance.close($scope.selectedItems);
        }
        else {
            var tmp = [];
            var treeObj = $.fn.zTree.getZTreeObj("businessTopo");
            var select_servers = treeObj.getCheckedNodes(true);
            var items = [];
            for (var i = 0; i < select_servers.length; i++) {
                if (select_servers[i].bk_obj_name === "IP") {
                    var oneObj = select_servers[i].ip + "s" + select_servers[i].source;
                    if (tmp.indexOf(oneObj) < 0){
                        items.push(select_servers[i]);
                        tmp.push(oneObj);
                    }
                }
            }
            $modalInstance.close(items);
        }
    };

    $scope.search_ip = function () {
        $scope.serverList = [];
        filter_list = $scope.filterObj.ip.split(" ");
        real_filter_list = $filter('filter')(filter_list, function (i) {
            return i != "";
        });
        if (real_filter_list.length > 0){
            for (var j in real_filter_list){
                $scope.serverListOne = $filter('filter')($scope.all_server, function (i) {
                    return i.ip.indexOf(real_filter_list[j]) > -1;
                });
                for (var z in $scope.serverListOne){
                    if ($scope.serverList.indexOf($scope.serverListOne[z]) == -1){
                       $scope.serverList.push($scope.serverListOne[z])
                    }
                }
            }
        }
        else{
            $scope.serverList = $filter('filter')($scope.all_server, function (i) {
                return i.ip.indexOf($scope.filterObj.ip) > -1;
            });
        }
        $scope.all_selection.is_select_all = false;
        $scope.selectAll();
        $scope.selectedItems.splice(0, $scope.selectedItems.length);
        $scope.pagingOptions.currentPage = 1;
        $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
    };

    $scope.cancel = function () {
        $modalInstance.dismiss("cancel");
    };
}]);