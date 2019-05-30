controllers.controller('error', ["$scope", "$modalInstance", "errorList", function ($scope, $modalInstance, errorList) {
    if (!Array.isArray(errorList))
        $scope.errors = [errorList];
    else{
        $scope.errors = errorList;
    }
    $scope.confirm = function () {
        $modalInstance.close();
    };
}]);