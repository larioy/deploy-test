controllers.controller("checkAddCtrl", ["$scope", "msgModalN", "checkService", "sysService", "$modal", "loading", function ($scope, msgModalN, checkService, sysService, $modal, loading) {
    $scope.args = {
        check_module_id: "",
        receivers: "",
        account: ""
    };
    $scope.moduleList = [];
    $scope.receiveList = [];
    checkService.get_task_option({}, {}, function (res) {
        if (res.result) {
            $scope.receiveList = res.mail_list;
            $scope.moduleList = res.module_list;
        }
    });

    $scope.getAccount = function () {
        checkService.get_account({}, {}, function (res) {
            $scope.args.account = res.data;
        })
    };
    $scope.getAccount();


    $('#date_start').kendoDatePicker({
        value: new Date(),
        format: "yyyy-MM-dd"
    });

    $('#per_date').kendoDatePicker({
        value: new Date(),
        format: "yyyy-MM-dd"
    });
    var timer_dataP = $("#date_start").data("kendoDatePicker");
    var per_dataP = $("#per_date").data("kendoDatePicker");

    $scope.change_value = function (selected) {
        if (selected === "01") {
            $("#date_start")[0].disabled = true;
            $("#day_long")[0].disabled = true;
            $("#per_date")[0].disabled = true;
            $("#timer_minu")[0].disabled = true;
            $("#timer_hour")[0].disabled = true;
            $(".period").attr('disabled', 'disabled');
            $("#interval_type")[0].disabled = true;
            timer_dataP.enable(false);
            per_dataP.enable(false);
        }
        else if (selected === "02") {
            $("#date_start")[0].disabled = false;
            $("#day_long")[0].disabled = true;
            $("#per_date")[0].disabled = true;
            $("#timer_minu")[0].disabled = false;
            $("#timer_hour")[0].disabled = false;
            $(".period").attr('disabled', 'disabled');
            $("#interval_type")[0].disabled = true;
            timer_dataP.enable(true);
            per_dataP.enable(false);
        }
        else {
            $("#date_start")[0].disabled = true;
            $("#day_long")[0].disabled = false;
            $("#per_date")[0].disabled = false;
            $("#timer_minu")[0].disabled = true;
            $("#timer_hour")[0].disabled = true;
            $(".period").removeAttr('disabled');
            $("#interval_type")[0].disabled = false;
            timer_dataP.enable(false);
            per_dataP.enable(true);
        }
    };
    $scope.change_value('01');

    $scope.moduleOption = {
        data: "moduleList",
        modelData: "args.check_module_id",
        multiple: false
    };

    $scope.reveiveOpt = {
        data: "receiveList",
        modelData: "args.receivers",
        multiple: true
    };
    $scope.serverSelect = [];
    $scope.serverKBs = [];
    $scope.flag = false;
    $scope.select_server = function () {
        var modalInstance = $modal.open({
            templateUrl: static_url + 'client/views/checkManagement/selectServers.html',
            windowClass: 'serverDialog',
            controller: 'selectServersCtrl',
            backdrop: 'static'
        });
        modalInstance.result.then(function (servers) {
            $scope.serverSelect = [];
            $scope.app_id = [];
            for (var i = 0; i < servers.length; i++) {
                $scope.serverSelect.push({'ip': servers[i].ip, 'source': servers[i].source, 'app_id': servers[i].app_id, 'server_name': servers[i].bk_os_name, 'source_name': servers[i].source_name});
                if ($scope.app_id.indexOf(servers[i].app_id) < 0) {
                    $scope.app_id.push(servers[i].app_id);
                }
            }
        });
    };

    $scope.gridOption = {
        data: 'serverSelect',
        columnDefs: [
            {field: 'source_name', displayName: '区域名称', width: 100},
            {field: 'ip', displayName: 'IP地址', width: 120},
            {field: 'server_name', displayName: '操作系统'},

            {
                displayName: '操作', width: 60, height: 0,
                cellTemplate: '<div style="width:100%;text-align: center;padding-top: 5px;z-index: 1">' +
                '<span ng-click="deleteServer(row)" class="label label-danger" style="min-width:50px;margin-left: 5px;cursor:pointer;">删除</span>' +
                '</div>'
            }
        ]
    };

    $scope.deleteServer = function (row) {
        $scope.serverSelect.splice(row.rowIndex, 1);
    };


    //保存配置信息
    var app_id_list = "";

    $scope.confirm = function () {
        var timeset = "";
        var time_type = $("input[name='time_select']:checked").val();
        if (!$("#task_name").val()) {
            msgModalN.open("任务名称不能为空！");
            return;
        }
        if ($scope.args.account === '') {
            msgModalN.open("执行账号不能为空！");
            return;
        }
        if ($scope.args.check_module_id === "") {
            msgModalN.open("请选择模板!");
            return;
        }
        if (time_type !== "NOW") {
            if (time_type === "TIMER") {
                timeset = $("#date_start").val();
                timeset = timeset + " " + ($('#timer_hour').val() ? $('#timer_hour').val() : "00") + ":" + ($('#timer_minu').val() ? $('#timer_minu').val() : "00") + ":00"
                var errors = is_datetime(timeset);
                if (errors !== "") {
                    app_alert(errors);
                    return;
                }
            }
            else {
                if (!$("#day_long").val()) {
                    msgModalN.open("周期任务时间间隔不能为空！");
                    return;
                }
                if (!is_num($("#day_long").val())) {
                    msgModalN.open("周期任务时间间隔格式错误！");
                    return;
                }
                if ($("#day_long").val() == "0" || $("#day_long").val() == 0) {
                    msgModalN.open("时间间隔不能设置为0!");
                    return false;
                }
                timeset = $("#per_date").val();
                timeset = timeset + " " + ($('#per_hour').val() ? $('#per_hour').val() : "00") + ":" + ($('#per_minu').val() ? $('#per_minu').val() : "00") + ":00"
                var errors = is_datetime(timeset);
                if (errors != "") {
                    app_alert(errors);
                    return;
                }
            }
        }
        var day_long = $("#day_long").val();
        if ($scope.serverSelect.length === 0) {
            msgModalN.open("请选择服务器！");
            return;
        }
        loading.open();
        var app_id_list = "";
        for (var i = 0; i < $scope.app_id.length; i++) {
            app_id_list += $scope.app_id[i] + ";"
        }
        var task_info = {
            name: $("#task_name").val(),
            receivers: $scope.args.receivers,
            time_type: time_type,
            time_set: timeset,
            servers: $scope.serverSelect,
            day_long: day_long,
            interval_type: $("#interval_type").val(),
            app_id_list: app_id_list,
            account: $scope.args.account,
            check_module_id: $scope.args.check_module_id
        };
        checkService.create_check_task({},task_info,function (res) {
            loading.close();
                if (res.is_success) {
                    if (time_type === "NOW") {
                        msgModalN.open("启动成功！");
                    } else {
                        msgModalN.open("任务创建成功！");
                    }
                    if (time_type === "NOW")
                        window.location.href = site_url + "#/checkReport";
                    else
                        window.location.href = site_url + "#/checkSearch";
                }
                else {
                    msgModalN.open(res.message);
                }
        });
    };

}]);