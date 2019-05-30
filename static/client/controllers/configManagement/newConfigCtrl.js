// /**
//  * Created by Administrator on 2017/6/13.
//  */
// controllers.controller("newConfigCtrl", ["$scope", "settingsService", "checkService", "confirmModal", "errorModal", "loading", "$interval", function ($scope, settingsService, checkService, confirmModal, errorModal, loading, $interval) {
//     $scope.filterObj = {
//         name: "",
//         when_created: ""
//     };
//     $scope.ObjList = [];
//     $scope.Pagingdata = [];
//     $scope.totalSerItems = 0;
//
//     $scope.pagingOptions = {
//         pageSizes: [10, 50, 100],
//         pageSize: "10",
//         currentPage: 1
//     };
//     $scope.condition = '';
//     $scope.searchObj = function () {
//         settingsService.search_server_config({}, {'ip': $scope.condition}, function (res) {
//             if (res.is_success) {
//                 $scope.ObjList = res.data;
//                 $scope.pagingOptions.currentPage = 1;
//                 $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
//             }
//             else {
//                 errorModal.open(res.data);
//             }
//         })
//     };
//
//     // var timeout_upd=$interval($scope.searchObj,3000);
//     // $scope.$on('$destroy',function(){
//     //    $interval.cancel(timeout_upd);
//     // })  ;
//
//     $scope.getPagedDataAsync = function (pageSize, page) {
//         $scope.setPagingData($scope.ObjList ? $scope.ObjList : [], pageSize, page);
//     };
//
//     $scope.setPagingData = function (data, pageSize, page) {
//         $scope.Pagingdata = data.slice((page - 1) * pageSize, page * pageSize);
//         $scope.totalSerItems = data.length;
//         if (!$scope.$$phase) {
//             $scope.$apply();
//         }
//     };
//
//     $scope.$watch('pagingOptions', function (newVal, oldVal) {
//         $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage);
//     }, true);
//     $scope.searchObj();
//
//     $scope.gridOption = {
//         data: "Pagingdata",
//         enablePaging: true,
//         showFooter: true,
//         pagingOptions: $scope.pagingOptions,
//         totalServerItems: 'totalSerItems',
//         columnDefs: [
//             {
//                 cellTemplate: '<div style="width:100%;padding-top:5px;">' +
//                 '<a ng-click="detail_open(row.entity)" style="color:#3c8dbc;">{{row.entity.ip}}</a>' +
//                 '</div>', displayName: '主机IP'
//             },
//             {field: 'application_name', displayName: '所属业务'},
//             {field: 'model_name', displayName: '所属模块'},
//             {field: 'update_time', displayName: '配置更新时间', width: 200},
//             {
//                 displayName: '操作', width: 150,
//                 cellTemplate: '<div style="width:100%;padding-top:5px;text-align: center;">' +
//                 '<span class="label label-sm label-info label-btn" ng-click="detail_open(row.entity)">详细配置</span>' +
//
//                 '</div>'
//             }
//         ]
//     };
//
//
//     $scope.server = "";
//     $scope.detail_open = function (row) {
//         $scope.server = row.ip;
//         $("btn_close").addClass("show_config");
//         $("#host_box").animate({"right": '0'});
//         loading.open();
//         settingsService.search_server_config_detail({}, {'server_config_id': row.server_config_id}, function (res) {
//             console.log(res);
//             loading.close();
//             $scope.BasicObj = [];
//             $scope.CpuObj = [];
//             $scope.MemObj = [];
//             $scope.DiskObj = [];
//             if (res.is_success) {
//                 for (var i = 0; i < res.data.length; i++) {
//                     if (res.data[i]['detail_type'] == 'basic') {
//                         $scope.BasicObj = res.data[i]['data'];
//                     }
//                     if (res.data[i]['detail_type'] == 'cpu') {
//                         $scope.CpuObj = res.data[i]['data'];
//                     }
//                     if (res.data[i]['detail_type'] == 'mem') {
//                         $scope.MemObj = res.data[i]['data'];
//                     }
//                     if (res.data[i]['detail_type'] == 'disk') {
//                         $scope.DiskObj = res.data[i]['data'];
//                     }
//                     $scope.customDetail = res.custom_detail;
//                     $scope.oldCustomDetail = angular.copy($scope.customDetail);
//                 }
//             }
//             else {
//                 errorModal.open(res.data);
//             }
//         })
//
//     };
//     $scope.detail_close = function () {
//         $("#host_box").animate({"right": '-1500px'});
//         $scope.title_index = 1;
//     };
//
//     $scope.start_sync = function () {
//         settingsService.start_sync_business({}, {}, function (res) {
//             if (res.is_success) {
//                 alert("成功")
//             } else {
//                 alert("失败")
//             }
//         })
//     }
//
//
//     $scope.title_index = 1;
//     $scope.isModify = false;
//
//     $scope.changeTitle = function (i) {
//         $scope.title_index = i;
//     };
//
//     $scope.modifyCustom = function () {
//         $scope.isModify = true;
//     };
//     $scope.cancelCustom = function () {
//         $scope.customDetail = angular.copy($scope.oldCustomDetail);
//         $scope.isModify = false;
//     };
//
//     $scope.saveCustom = function () {
//         loading.open();
//         settingsService.modify_custom_detail({}, {ip: $scope.server, detail: $scope.customDetail}, function (res) {
//             loading.close();
//             if (res.result) {
//                 $scope.oldCustomDetail = angular.copy($scope.customDetail);
//                 $scope.isModify = false;
//             }
//             else {
//                 errorModal.open(res.data);
//             }
//         })
//     }
// }]);