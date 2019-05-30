controllers.controller("moduleModifyCtrl", function ($filter, $scope, itemObj, moduleService, loading, msgModal, errorModal, $modalInstance) {
    $scope.moduleObj = itemObj;
    $scope.tabIndex = 1;
    $scope.changeTab = function (i) {
        $scope.tabIndex = i;
    };
    $scope.moduleList = [];
    $scope.itemList = [];
    $scope.menuList = [];
    $scope.customItemList = [];
    $scope.customObj = {
        is_checked: true,
        isShow: true
    };

    $scope.init = function () {
        loading.open();
        moduleService.get_module_list({}, {}, function (res) {
            loading.close();
            if (res.result) {
                $scope.moduleList = [];
                angular.forEach(res.data, function (i) {
                    if (i.id != $scope.moduleObj.id)
                        $scope.moduleList.push(i);
                });
            }
            else {
                errorModal.open(res.data);
            }
        })
    };

    $scope.init();

    $scope.changeModule = function (module_id) {
        loading.open();
        moduleService.get_module_item_list({module_id: module_id}, {}, function (res) {
            loading.close();
            if (res.result) {
                $scope.itemList = res.data;
                $scope.menuList = res.menu_list;
                $scope.customItemList = res.custom_item_list;
            }
            else {
                errorModal.open(res.data);
            }
        })
    };
    $scope.changeModule($scope.moduleObj.id);

    $scope.moduleOption = {
        data: "moduleList",
        modelData: "moduleObj.base_module_id"
    };

    $scope.openDetail = function (i) {
        i.isShow = !i.isShow;
    };

    $scope.changeMenuOne = function (i) {
        angular.forEach(i.menu_two, function (u) {
            u.is_checked = i.is_checked;
        });
        angular.forEach($scope.itemList, function (u) {
            if (u.menu_one == i.menu_one) {
                u.is_checked = i.is_checked;
            }
        })
    };

    $scope.changeMenuTwo = function (i) {
        angular.forEach($scope.itemList, function (u) {
            if (u.menu_two == i.name) {
                u.is_checked = i.is_checked;
            }
        })
    };

    $scope.cancel = function () {
        $modalInstance.dismiss("cancel");
    };


    var validateObj = function () {
        var errors = [];
        if ($scope.moduleObj.name === "") {
            errors.push("模板名称不能为空!");
        }
        if ($scope.moduleObj.base_module_id === "") {
            errors.push("基准模板未选择!");
        }
        return errors;
    };

    $scope.confirm = function () {
        var errors = validateObj();
        if (errors.length > 0) {
            errorModal.open(errors);
            return;
        }
        loading.open();
        $scope.moduleObj.check_item_list = angular.copy($scope.itemList);
        $scope.moduleObj.custom_item_list = angular.copy($scope.customItemList);
        moduleService.modify_module({}, $scope.moduleObj, function (res) {
            loading.close();
            if (res.result) {
                msgModal.open("success", "修改成功");
                $modalInstance.close();
            }
            else {
                errorModal.open(res.data);
            }
        })
    };

    $scope.changCustomItem = function (i) {
        angular.forEach($scope.customItemList, function (u) {
            u.is_checked = i.is_checked;
        })
    };
});