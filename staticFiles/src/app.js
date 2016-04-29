'use strict';

var $ = require('jquery-browserify');
var angular = require('angular');
var angular_route = require('angular-route');
var a = require('./modules/a');

var app = angular.module('app', ['ngRoute']);

app.controller('MenuController', function($scope, $route, $routeParams, $location){
	$scope.$route = $route;
	$scope.state = 1;
	window.setInterval(function(){
		$scope.state = 2;
		$scope.$apply();
	}, 3000);
});

app.controller('IndexController', function($scope, $routeParams){
	$scope.name = 'IndexController';
	$scope.title = 'ERROR';
	$scope.x = {
		a: 123,
		b: 'aaaa'
	};
	$scope.desc = 'Order not found';
	window.setInterval(function(){
		$scope.title = 'ERROR again';
		$scope.$apply();
	}, 3000);
});

app.controller('CheckController', function($scope, $routeParams){
	//$scope.name = 'Page2Controller';
	//alert(2);
});

app.controller('OrderController', function($scope, $routeParams){
	//$scope.name = 'Page2Controller';
	//alert(2);
});

app.controller('ShareController', function($scope, $routeParams){
	//$scope.name = 'Page2Controller';
	//alert(2);
});

app.controller('OrdersController', function($scope, $routeParams){
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
