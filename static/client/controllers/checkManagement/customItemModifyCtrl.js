controllers.controller("customItemModifyCtrl", function ($modalInstance, $scope, loading, errorModal, checkService, msgModal, itemObj) {
    $scope.args = itemObj;
    $scope.title = "修改自定义巡检项";
    $scope.confirm = function () {
        loading.open();
        checkService.modify_custom_item({}, $scope.args, function (res) {
            loading.close();
            if (res.result) {
                msgModal.open("success", "修改成功");
                $modalInstance.close();
            }
            else {
                errorModal.open([res.data]);
            }
        })
    };

    $scope.cancel = function () {
        $modalInstance.dismiss("cancel");
    }
});