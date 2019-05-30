controllers.controller("customItemAddCtrl", function ($modalInstance, $scope, loading, errorModal, checkService, msgModal) {
    $scope.args = {
        name: "",
        cn_name: "",
        description: "",
        script_content: "",
        compare_way: ">",
        compare_value: "",
        created_by: current_user
    };
    $scope.title = "新增自定义巡检项";
    $scope.confirm = function () {
        var errors = validateObj();
        if (errors.length > 0) {
            errorModal.open(errors);
            return;
        }
        loading.open();
        checkService.create_custom_item({}, $scope.args, function (res) {
            loading.close();
            if (res.result) {
                msgModal.open("success", "添加成功");
                $modalInstance.close();
            }
            else {
                errorModal.open([res.data]);
            }
        })
    };

    var validateObj = function () {
        var errors = [];
        if ($scope.args.name === "") {
            errors.push("巡检字段不能为空！");
        }
        if ($scope.args.cn_name === "") {
            errors.push("巡检项名称不能为空")
        }
        if ($scope.args.script_content === "") {
            errors.push("巡检脚本不能为空");
        }
        return errors;
    };

    $scope.cancel = function () {
        $modalInstance.dismiss("cancel");
    }
});