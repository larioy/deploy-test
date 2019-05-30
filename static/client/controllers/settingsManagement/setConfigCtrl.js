/**
 * Created by Administrator on 2017/7/7.
 */
controllers.controller("setConfigCtrl", ["$scope","$modal","errorModal","settingsService", "msgModalN", "confirmModal","loading",function ($scope,$modal,errorModal,settingsService, msgModalN, confirmModal,loading) {
    $scope.taskObj = {
        isCreated:true,
        config_account: "",
        report_num:""
    };
    $scope.searchObj=function(){
        loading.open();
        settingsService.get_set_config({},{},function(res){
            loading.close();
            if(res.is_success){
                copy_data=angular.copy(res.data);
                $scope.taskObj.config_account=res.data['config_account'];
                $scope.taskObj.report_num=res.data['report_num'];
            }else{
                msgModalN.open(res.message);
            }
        });
    };
    $scope.searchObj();

    $scope.confirm=function(){
        if($scope.taskObj.config_account==""){
            msgModalN.open("配置执行账号不能为空");
            return
        }
        if($scope.taskObj.report_num==""){
            msgModalN.open("历史报告保留份数不能为空");
            return
        }
        loading.open();
        settingsService.modify_set_config({},$scope.taskObj,function(res){
            loading.close();
            if(res.is_success){
                $scope.searchObj();
                $scope.taskObj.isCreated = true;
            }else{
                msgModalN.open(res.message);
            }
        });
    };

    $scope.modifyItem = function () {
        $scope.taskObj.isCreated = false;
    };

    $scope.cancel = function () {
        $scope.taskObj.config_account = copy_data['config_account'];
        $scope.taskObj.report_num=res = copy_data['report_num'];
        $scope.taskObj.isCreated = true;
    }

}]);