/**
 * Created by Administrator on 2017/6/20.
 */
/**
 * Created by Administrator on 2017/6/13.
 */
controllers.controller("checkItemModifyCtrl", ["$scope","checkService","objectItem","$modalInstance","errorModal","loading",function ($scope,checkService,objectItem,$modalInstance,errorModal,loading) {
    $scope.row = angular.copy(objectItem);
    $scope.title = "修改标准值";

    $scope.Save = function(){
        if ($scope.row.compare_value==""){
            errorModal.open(['标准值不能为空']);
            return;
        }
        loading.open();
        checkService.modify_check_item({},$scope.row,function(res){
            loading.close();
            if (res.is_success) {
                $modalInstance.close($scope.row);
            }
            else {
                errorModal.open(res.data.split(";"));
            }
        })
    };

    $scope.cancel = function () {
        $modalInstance.dismiss("cancel");
    };
}]);