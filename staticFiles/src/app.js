'use strict';

require('jquery-browserify');
var angular = require('angular');
var angular_route = require('angular-route');

var app = angular.module('app1', ['ngRoute']);

app.controller('MenuController', function($scope, $route, $routeParams, $location){
	$scope.$route = $route;
	$scope.state = 1;
	window.setInterval(function(){
		$scope.state = 2;
		$scope.$apply();
	}, 3000);
});

app.controller('Page1Controller', function($scope, $routeParams){
	$scope.name = 'Page1Controller';
	$scope.title = 'ERROR';
	$scope.desc = 'Order not found';
	window.setInterval(function(){
		$scope.title = 'ERROR again';
		$scope.$apply();
	}, 3000);
});

app.controller('Page2Controller', function($scope, $routeParams){
	$scope.name = 'Page2Controller';
});

app.controller('Page3Controller', function($scope, $routeParams){
	$scope.name = 'Page3Controller';
});

app.config(function($routeProvider, $locationProvider){
	$routeProvider
		.when('/page1', {
			templateUrl: 'html/page1.html',
			controller: 'Page1Controller'
		})
		.when('/page2', {
			templateUrl: 'html/page2.html',
			controller: 'Page2Controller'
		})
		.when('/page3', {
			templateUrl: 'html/page3.html',
			controller: 'Page3Controller'
		})
	//$locationProvider.html5Mode(true);
});
