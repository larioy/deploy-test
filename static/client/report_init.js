var app = angular.module("myApp", ['myController', 'utilServices', 'myDirective', 'ui.bootstrap', 'ui.router', 'webApiService','ngGrid']);
var controllers = angular.module("myController", []);
var directives = angular.module("myDirective", []);


app.config(["$stateProvider", "$urlRouterProvider", "$httpProvider", function ($stateProvider, $urlRouterProvider, $httpProvider) {
    $httpProvider.defaults.headers.post['X-CSRFToken'] = $("#csrf").val();
    $urlRouterProvider.otherwise("/reportInfoDetail");//默认展示页面
    $stateProvider.state('reportInfoDetail', {
        url: "/reportInfoDetail",
        controller: "reportInfoDetailCtrl",
        templateUrl: static_url + "client/views/reportDetailManagement/reportInfoDetail.html"
    })
}]);
