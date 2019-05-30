controllers.controller("checkModifyCtrl", ["$scope", "msgModalN", "checkService", "$modal", "$stateParams", "errorModal", "loading", function ($scope, msgModalN, checkService, $modal, $stateParams, errorModal, loading) {
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
        if (selected == "01") {
            $("#date_start")[0].disabled = true;
            $("#day_long")[0].disabled = true;
            $("#per_date")[0].disabled = true;
            $("#timer_minu")[0].disabled = true;
            $("#timer_hour")[0].disabled = true;
            $(".period").attr('disabled', 'disabled');
            $("#interval_type")[0].disabled = true;
            $scope.time_type = "NOW";
        }
        else if (selected == "02") {
            $("#date_start")[0].disabled = false;
            $("#day_long")[0].disabled = true;
            $("#per_date")[0].disabled = true;
            $("#timer_minu")[0].disabled = false;
            $("#timer_hour")[0].disabled = false;
            $(".period").attr('disabled', 'disabled');
            $("#interval_type")[0].disabled = true;
            $scope.time_type = "TIMER";
        }
        else {
            $("#date_start")[0].disabled = true;
            $("#day_long")[0].disabled = false;
            $("#per_date")[0].disabled = false;
            $("#timer_minu")[0].disabled = true;
            $("#timer_hour")[0].disabled = true;
            $(".period").removeAttr('disabled');
            $("#interval_type")[0].disabled = false;

            $scope.time_type = "CYCLE"
        }
    };
    $scope.change_value('01');


    $scope.searchObj = function () {
        loading.open();
        checkService.get_modify_check_task({}, {'id': $stateParams.id}, function (res) {
            loading.close();
            if (res.is_success) {
                $scope.row = res.data;
                $scope.Reset($scope.row)
            }
            else {
                window.location.href = site_url + "#/checkReport";
                msgModalN.open(res.message);
            }
        })
    };
    $scope.searchObj();
    $scope.moduleList = [];
    $scope.receiveList = [];
    $scope.moduleOption = {
        data: "moduleList",
        modelData: "row.check_module_id",
        multiple: false
    };
    $scope.reveiveOpt = {
        data: "receiveList",
        modelData: "row.receivers",
        multiple: true
    };
    checkService.get_task_option({}, {}, function (res) {
        if (res.result) {
            $scope.moduleList = res.module_list;
            $scope.receiveList = res.mail_list;
        }
    });

    //获取原有数据
    $scope.Reset = function (row) {
        //获取邮箱初始值
        //获取IP初始值
        $scope.serverSelect = row.servers;
        $scope.app_id = row['app_id_list'].split(";");
        $scope.set_time_value(row)
    };
    $scope.set_time_value = function (row) {
        var run_time_selected = row.celery_time_set.set_type;
        if (run_time_selected === "NOW") {
            $scope.change_value('01');
        }
        else {
            run_time = row.celery_time_set.run_time;
            date_val = run_time.split(" ")[0];
            time_val = run_time.split(" ")[1];
            hour_val = time_val.split(":")[0];
            minu_val = time_val.split(":")[1];
            if (run_time_selected === "TIMER") {
                $("#timer_hour").val(hour_val);
                $("#timer_minu").val(minu_val);
                $scope.change_value("02");
                timer_dataP.value(date_val);
            }
            else {
                $("#per_hour").val(hour_val);
                $("#per_minu").val(minu_val);
                var task_interval = row.celery_time_set.interval_type;
                $("#interval_type").val(task_interval);
                $("#day_long").val(row.celery_time_set.time_interval);
                $scope.change_value("03");
            }
        }
    };

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
                $scope.serverSelect.push({'ip': servers[i].ip, 'source': servers[i].source, 'app_id': servers[i].app_id, 'server_name': servers[i].bk_os_name ,'source_name':servers[i].source_name});
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
            {field: 'ip', displayName: 'IP地址',width:120},
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

    var app_id_list = "";

    $scope.confirm = function () {
        var timeset = "";
        var time_type = $("input[name='time_select']:checked").val();
        if (!$("#task_name").val()) {
            msgModalN.open("任务名称不能为空！");
            return;
        }
        if ($scope.row.check_module_id === "") {
            msgModalN.open("请选择模板！");
            return;
        }
        if ($scope.row.account === "") {
            msgModalN.open("执行账号不能为空！");
        }
        if (time_type !== "NOW") {
            if (time_type === "TIMER") {
                timeset = $("#date_start").val();
                timeset = timeset + " " + ($('#timer_hour').val() ? $('#timer_hour').val() : "00") + ":" + ($('#timer_minu').val() ? $('#timer_minu').val() : "00") + ":00"
                var errors = is_datetime(timeset);
                if (errors !== "") {
                    msgModalN.open(errors);
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
                if ($("#day_long").val() === "0" || $("#day_long").val() === 0) {
                    msgModalN.open("时间间隔不能设置为0!");
                    return false;
                }
                timeset = $("#per_date").val();
                timeset = timeset + " " + ($('#per_hour').val() ? $('#per_hour').val() : "00") + ":" + ($('#per_minu').val() ? $('#per_minu').val() : "00") + ":00"
                var errors = is_datetime(timeset);
                if (errors !== "") {
                    msgModalN.open(errors);
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
            if ($scope.app_id[i]) {
                app_id_list += $scope.app_id[i] + ";"
            }
        }
        var task_info = {
            id: $stateParams.id,
            name: $("#task_name").val(),
            receivers: $scope.row.receivers,
            time_type: time_type,
            time_set: timeset,
            servers: $scope.serverSelect,
            day_long: day_long,
            interval_type: $("#interval_type").val(),
            app_id_list: app_id_list,
            account: $scope.row.account,
            check_module_id: $scope.row.check_module_id
        };
        checkService.modify_check_task({}, task_info, function (res) {
            loading.close();
            if (res.is_success) {
                msgModalN.open('巡检任务修改成功！');
                if (task_info.time_type === "NOW")
                    window.location.href = site_url + "#/checkReport";
                else
                    window.location.href = site_url + "#/checkSearch";
            }
            else {
                msgModalN.open(res.message);
            }
        })
    };
}]);
