controllers.controller('addCustomCtrl', ["$scope", "sysService", "errorModal", "$modalInstance", "loading", function ($scope, sysService, errorModal, $modalInstance, loading) {
    $scope.title = "添加自定义字段";
    $scope.args = {
        cn_name: "",
        name: "",
        description: ""
    };
    $scope.confirm = function () {
        var errorList = validateObj();
        if (errorList.length > 0) {
            errorModal.open(errorList);
            return;
        }
        loading.open();
        sysService.add_custom({}, $scope.args, function (res) {
            loading.close();
            if (res.result) {
                $modalInstance.close(res.data);
            }
            else {
                errorModal.open(res.data);
            }
        })
    };
    $scope.cancel = function () {
        $modalInstance.dismiss("cancel");
    };

    var validateObj = function () {
        var errors = [];
        if ($scope.args.cn_name === "") {
            errors.push("显示名称不能为空！");
        }
        if ($scope.args.name === "") {
            errors.push("字段名不能为空！");
        }
        else if (!CWApp.isEng($scope.args.name)) {
            errors.push("字段名不允许有中文和特殊符号！");
        }
        return errors;
    }
}]);