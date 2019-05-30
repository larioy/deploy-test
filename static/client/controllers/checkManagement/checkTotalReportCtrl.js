controllers.controller("checkTotalReportCtrl", ["$scope", "checkService", "loading", "errorModal", "msgModal", function ($scope, checkService, loading, errorModal, msgModal) {

    $scope.selectItem = {id: "", ip: ""};
    $scope.title_index = 2;
    $scope.changeIndex = function (i) {
        $scope.title_index = i;
    };
    $scope.ipList = [];
    checkService.get_ip_list({}, {}, function (res) {
        if (res.is_success) {
            $scope.ipList = res.data;
            if (res.data.length > 0) {
                $scope.selectItem.id = $scope.ipList[0].id;
                $scope.getChartList();
            }
        }
        else {
            errorModal.open(res.data);
        }
    });


    $scope.selectOptions = {
        data: "ipList",
        multiple: false,
        modelData: "selectItem.id"
    };

    $scope.cpuChart = {
        data: "selectItem.cpuF",
        chart: {type: 'line'},
        title: {text: '', enabled: true},
        xAxis: {
            categories: []
        },
        //提示框位置和显示内容
        tooltip: {
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            '<td style="padding:0"><b>{point.y:f}</b></td></tr>',
            headerFormat: ""
        }
    };


    $scope.memChart = {
        data: "selectItem.memF",
        chart: {type: 'line'},
        title: {text: '', enabled: true},
        xAxis: {
            categories: []
        },
        //提示框位置和显示内容
        tooltip: {
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            '<td style="padding:0"><b>{point.y:f}</b></td></tr>',
            headerFormat: ""
        }
    };


    $scope.diskChart = {
        data: "selectItem.diskF",
        chart: {type: 'line'},
        title: {text: '', enabled: true},
        xAxis: {
            categories: []
        },
        //提示框位置和显示内容
        tooltip: {
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            '<td style="padding:0"><b>{point.y:f}</b></td></tr>',
            headerFormat: ""
        }
    };

    $scope.diskSpaceChart = {
        data: "selectItem.diskS",
        chart: {type: 'line'},
        title: {text: '', enabled: true},
        xAxis: {
            categories: []
        },
        //提示框位置和显示内容
        tooltip: {
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
            '<td style="padding:0"><b>{point.y:f}</b></td></tr>',
            headerFormat: ""
        }
    };

    $scope.changeIP = function () {
        $scope.getChartList();
    };

    $scope.getChartList = function () {
        loading.open();
        checkService.get_chart_list({ip: $scope.selectItem.id}, {}, function (res) {
            loading.close();
            if (res.result) {
                // $scope.selectItem.serverList = res.data.serverList;
                $scope.selectItem.cpuF = res.data.cpu_one;
                // $scope.selectItem.cpuS = res.data.cpu_two;
                $scope.selectItem.memF = res.data.mem_one;
                // $scope.selectItem.memS = res.data.mem_two;
                $scope.selectItem.diskF = res.data.disk_one;
                $scope.selectItem.diskS = res.data.disk_space;

                // $scope.selectItem.diskS = res.data.disk_two;
            }
            else {
                errorModal.open(res.data);
            }
        })
    };
}]);