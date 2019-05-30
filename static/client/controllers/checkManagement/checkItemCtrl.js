controllers.controller("checkItemCtrl", ["$scope","checkService","$modal","errorModal",function ($scope,checkService,$modal,errorModal) {
    $scope.ObjList = [];
    $scope.searchObj = function () {
        checkService.search_check_item({},{}, function (res) {
            console.log(res);
            if (res.is_success) {
                $scope.ObjList = res.data;
            }
            else {
                errorModal.open([res.message]);
            }
        })
    };
    $scope.searchObj();


    $scope.modify_check_item = function (row) {
        var modalInstance = $modal.open({
            templateUrl: static_url + 'client/views/checkManagement/checkItemModify.html',
            windowClass: 'dialog_custom',
            controller: 'checkItemModifyCtrl',
            backdrop: 'static',
            resolve: {
                objectItem: function () {
                    return row.entity;
                }
            }
        });
        modalInstance.result.then(function (res) {
            row.entity.compare_value = res.compare_value;
        })
    };
    $scope.mySwitch=true;
    $scope.edit=function(){
        copy_data = angular.copy($scope.ObjList);
        $scope.mySwitch=false;
    };
    $scope.quit=function(){
        $scope.ObjList=copy_data;
        $scope.mySwitch=true;
    };
    $scope.save=function(){
        var details=[];
        var menus=[];
        for(var m=0;m<$scope.ObjList.length;m++){
            if($scope.ObjList[m]['item'].length==0){
                menus.push($scope.ObjList[m]);
            }
            for(var n=0;n<$scope.ObjList[m]['item'].length;n++){
                details.push($scope.ObjList[m]['item'][n]);
                if($scope.ObjList[m]['item'][n]['compare_value']==""){
                    errorModal.open([$scope.ObjList[m]['item'][n]['name']+"下的比较值不能为空"]);
                    return
                }

            }
        }
        checkService.modify_check_item({},{"details":details,"menus":menus},function(res){
            if(res.is_success){
                $scope.searchObj();
            }else{
                errorModal.open([res.message]);
            }
        });
        $scope.mySwitch=true;
    };

    $scope.All= function (data) {
        for(var m=0;m<$scope.ObjList.length;m++){
            if($scope.ObjList[m]['menu_name']==data['menu_name']){
                for(var i=0;i<$scope.ObjList[m]['item'].length;i++){
                    if(data['selectAll'] == true){
                        $scope.ObjList[m]['item'][i].menu__is_show = true;
                    } else {
                        $scope.ObjList[m]['item'][i].menu__is_show = false;
                    }
                }
            }
        }
    };


    $scope.One=function(){
        for(var m=0;m<$scope.ObjList.length;m++){
            var checkeds = [];
            for(var n=0;n<$scope.ObjList[m]['item'].length;n++){
                if($scope.ObjList[m]['item'][n]['menu__is_show']==false){
                    $scope.ObjList[m]['is_show']=false;
                    checkeds.push($scope.ObjList[m]['item'][n]['menu__is_show']);
                }
                if(checkeds.length==0){
                    $scope.ObjList[m]['is_show']=true;
                }
            }
        }
    };

    $scope.show=function($event){
        if ($($event.currentTarget).next('.menu').hasClass('open_item')) {
             $($event.currentTarget).next('.menu').removeClass('open_item');
             $($event.currentTarget).removeClass("bot_item");
             $($event.currentTarget).children().children().children().css({"transform":"rotate(90deg)"})
        } else {
            $($event.currentTarget).next('.menu').addClass('open_item');
            $($event.currentTarget).addClass('bot_item');
            $($event.currentTarget).children().children().children().css({"transform":"rotate(0deg)"})
        }
    }

}]);
