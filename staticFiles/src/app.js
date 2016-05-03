'use strict';

var $ = require('jquery-browserify');
var angular = require('angular');
var angular_route = require('angular-route');
var a = require('./modules/a');

var app = angular.module('app', ['ngRoute']);

app.service('$data',function($http){
	var that = this;
	this.fetchBatchInfo = function(cb){
		if(!!that.batchInfo){
			cb(that.batchInfo);
			return;
		}
		$http.post("http://192.168.102.21/api/batch", {
			batchId: 2,
			code: ''
		})
		.success(function(response){
			that.batchInfo = response;
			cb(response);
		});
	};
});

app.filter('safenum', function(){
	return function(input){
		if(!input){
			return 0;
		}
		return input;
	}
});

app.controller('MenuController', function($scope, $route, $routeParams, $location){
	$scope.$route = $route;
	$scope.state = 1;
	//window.setInterval(function(){
	//	$scope.state = 2;
	//	$scope.$apply();
	//}, 3000);
});

app.controller('IndexController', function($scope, $routeParams, $data){
	$data.fetchBatchInfo(function(response){
      	$scope.commodities = response.commodity;
      	$scope.sponsor=response.sponsor;
      	$scope.offered=response.offered;
	});
	$scope.addCommodity = function(commodity){
		if(!commodity.num){
			commodity.num = 0;
		}
		commodity.num += 1;
	};
	$scope.removeCommodity = function(commodity){
		if(!commodity.num){
			commodity.num = 0;
		}
		commodity.num -= 1;
		if(commodity.num < 0){
			commodity.num = 0;
		}
	};
	(function(status){
	    $('.__overlay').on('click', function(){
	    	status = false;
	    	window.popup_window_from_bottom();
		});
		window.popup_window_from_bottom = function(){
			var total = 0;
			for(var _ in $scope.commodities){
				var commodity = $scope.commodities[_];
				if(!!commodity.num){
					total += commodity.num;
				}
			}
		    if(status&&total>0){
		        status = false;
		        $('.__overlay').css('display', 'block');
		        $('.popup-window-from-bottom').css("display","block");
		        $("#index").css("overflow","hidden");
		    } else {
		        status = true;
		        $('.__overlay').css('display', 'none');
		        $('.popup-window-from-bottom').css('display', 'none');
		        $("#index").css("overflow","auto");
		    }
		}
	})(true);
  
});

app.controller('CheckController', function($scope, $routeParams,$http, $data){
	$data.fetchBatchInfo(function(response){
		alert(response);
	});
	$http.get("../assets/json/checkout.json")
	   .success(function(response){
	   	$scope.Pickpoint=response.Pickpoint;
	   	$scope.address=response.address;
	   	$scope.commodityList=response.commodityList;
	   	$scope.constList=response.constList;
	   })
	//$scope.name = 'Page2Controller';
	//alert(2);
});

app.controller('OrderController', function($scope, $routeParams,$http){
	$http.get("../assets/json/order.json")
	   .success(function(response){
	   	$scope.order=response.order;
	   	$scope.pickup=response.pickup;
	   	$scope.commodityList=response.commodityList;
	   	$scope.constList=response.constList;
	   })
	//$scope.name = 'Page2Controller';
	//alert(2);
});

app.controller('ShareController', function($scope, $routeParams){
	//$scope.name = 'Page2Controller';
	//alert(2);
});

app.controller('OrdersController', function($scope, $routeParams,$http){
	$http.get("../assets/json/orders.json")
	.success(function(response){
		$scope.orders=response;
	})
	$scope.name = 'Page3Controller';
});

app.controller('ErrorController', function($scope, $routeParams){
	$scope.name = 'Page3Controller';
});

app.config(function($routeProvider, $locationProvider){
	$routeProvider
		.when('/index', {
			templateUrl: 'html/index.html',
			controller: 'IndexController'
		})
		.when('/checkout', {
			templateUrl: 'html/checkout.html',
			controller: 'CheckController'
		})
		.when('/order', {
			templateUrl: 'html/order.html',
			controller: 'OrderController'
		})
		.when('/share', {
			templateUrl: 'html/share.html',
			controller: 'ShareController'
		})
		.when('/orders', {
			templateUrl: 'html/orders.html',
			controller: 'OrdersController'
		})
		.when('/error', {
			templateUrl: 'html/error.html',
			controller: 'ErrorController'
		})
	//$locationProvider.html5Mode(true);
});