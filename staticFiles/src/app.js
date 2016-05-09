'use strict';

var $ = require('jquery-browserify');
var angular = require('angular');
var angular_route = require('angular-route');
var a = require('./modules/a');

var app = angular.module('app', ['ngRoute']);

app.service('$data',function($http,$location){
	var that = this;
	this.getCode=function(){
		if(!that.codeId){
			var code=$location.search();
			that.codeId=code.code;
		}
		return that.codeId;
	}
    this.getBatchId=function(){
    	if(!that.batchId){
			var params=$location.search();	
        	that.batchId=params.state;
    	}
	    return that.batchId;
    }
    this.getOrderId=function(){
    	if(!that.orderId){
    		var orderid=$location.search();
    		that.orderId=orderid.useroder;
    	}
    	return that.orderId;
    }
	this.fetchBatchInfo = function(cb){

		if(!!that.batchInfo){
			cb(that.batchInfo);
			return;
		}
		$http.post("http://yijiayinong.com/api/batch", {
			batchId: that.getBatchId(),
			code: that.getCode(),
		})
		.success(function(response){
			that.openId=response.res.openId;
			that.batchInfo = response;
			cb(response);
		});
	};
	this.getAddress=function(cb){
		if(!!that.addressInfo){
			cb(that.addressInfo);
			return;
		}
		$http.post("http://yijiayinong.com/api/checkout",{
			batchId:that.getBatchId(),
			code:''
		})
		.success(function(response){
			that.addressInfo=response;
			cb(response);
		});
	};
	this.getOrders=function(cb){       
		if(!!that.ordersInfo){
			cb(that.ordersInfo);
			return;
		}
		$http.get("../assets/json/orders.json",{
			batchId:that.getBatchId(),
			code:''
		})
		.success(function(response){
			that.ordersInfo=response;
			cb(response);
		});
    };
    	this.getOrder=function(cb){       
		if(!!that.orderInfo){
			cb(that.orderInfo);
			return;
		}
		$http.get("../assets/json/order.json",{
			batchId:that.getBatchId(),
			code:''
		})
		.success(function(response){
			that.orderInfo=response;
			cb(response);
		});
    };
});



app.filter('convert',function(){
	return function(price){
		if(!!price){
			price=(price/100).toFixed(2);
		}
		return price;
	}
})

app.filter('safenum', function(){
	return function(input){
		if(!input){
			return 0;
		}
		return input;
	}
});

app.filter('int',function(){
	return function(price){
		if(!!price){
			price=parseInt(price/100);
		}
		return price;
	}
})

app.filter('fraction',function(){
	return function(price){
		if(!!price){
			price=(price%100);
			if(price==0){
				price="0"+price;
			}
		}
		return price;
	}
})

app.controller('MenuController', function($scope, $route, $routeParams, $location){
	$scope.$route = $route;
	$scope.state = 1;
});

app.controller('IndexController', function($location,$scope, $routeParams, $data){
	if(!$data.getBatchId()){
			$location.path("/error");
			return;
		}
	$data.fetchBatchInfo(function(response){
		if(!response){
			$location.path("/error");
			return;
		}
		if(response.errcode!="Success"){
			$location.path("/error");
			return;
		}
		if(!response.res){
			$location.path("/error");
			return;
		}
		if(!response.res.data){
			$location.path("/error");
			return;
		}
		if(!response.res.data.commodities 
			|| !response.res.data.sponsor 
			|| !response.res.data.offered){
			$location.path("/error");
			return;
		}
      	$scope.commodities = response.res.data.commodities;
      	$scope.sponsor=response.res.data.sponsor;
      	$scope.offered=response.res.data.offered;
	});
	$scope.statement=function(){
		var commodities=$data.batchInfo.res.data.commodities;
		var num=0;
		for(var i=0;i<commodities.length;i++){
			var cur=commodities[i];
			if(cur.num){
				num+=cur.num;
			}				
		}
		if(!num){
				alert("请选择商品");
				return;
			}
		if(num>0){
			$location.path("/checkout");
		}
	}
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

  	$scope.del=function(commodities){
  		for(var i=0;i<commodities.length;i++){
  			var cur=commodities[i];
  			if(!!cur.num){
  				cur.num=0;
  			}
  		}
	}

	$scope.$watch('commodities',function(newValue, oldValue){
		var num=0;
		var total=0;
		if(!newValue){
			return;	
		}
		for(var i=0;i<newValue.length;i++){
			var cur=newValue[i];
			if(!!cur.num){
				total+=cur.num*cur.price;
				num+=cur.num;
			}
		}
		if(num==0){
					$(".__amount").css('display', 'none');
					$('.__overlay').css('display', 'none');
			        $('.popup-window-from-bottom').css('display', 'none');
				}
				if(num>0){
					$(".__amount").css('display', 'block');
					$scope.num=num;
				}
        $scope.total=total;
	}, true)
});

app.controller('CheckController', function($scope, $routeParams,$data,$location){
	if(!$data.getBatchId()){
			$location.path("/error");
			return;
		}
	$data.getAddress(function(response){
		if(!response){
			$location.path("/error");
			return;
		}
		if(response.errcode!="Success"){
			$location.path("/error");
			return;
		}
		if(!response.res){
			$location.path("/error");
			return;
		}
		if(!response.res.data){
			$location.path("/error");
			return;
		}
		$scope.address=response.res.data;
		$scope.submit=function(p){
			$scope.selectedAddress = p;
		}
	});
	$data.fetchBatchInfo(function(response){
		var total=0;
		var num=0;
		$scope.commodities = response.res.data.commodities;
		var data=response.res.data.commodities;
		for(var i=0;i<data.length;i++){
			var cur=data[i];
			if(!!cur.num){
				num+=cur.num;
				total+=cur.num*cur.price;
			}
			if(num==0){		
				$location.path("/error");
				return;
			}
		}
        $scope.total=total;
	});
	var obj={};
	$scope.pay=function(commodities){	
		if(!$scope.nickName ||$scope.nickName.length==0){
			alert("昵称不存在");
			return;
		}
		if(!$scope.tel ||$scope.tel.length==0){
			alert("电话不存在");
			return;
		}
		if(!$scope.selectedAddress){
			alert("请选择取货地址");
			return;
		}	
			obj.openid=$data.openId,
			obj.nickname=$scope.nickName,
			obj.tel=$scope.tel,
			obj.batch_id=$data.getBatchId(),
			obj.dist_id=$scope.selectedAddress.id,
			obj.puchared=[],
			obj.ipaddress="127.0.0.1";
		for(var i=0;i<commodities.length;i++){
			var cur=commodities[i]; 
			if(!!cur.num){
				var oder={};
				oder.id=cur.id;
				oder.num=cur.num;
				obj.puchared.push(oder);
			}
		}
		$http.post('',{
			orderInfo:obj
		})
		.success(function(){
			
		})
		.error(function(){
			
		});
		alert(JSON.stringify(obj));
	}
});

app.controller('OrderController', function($scope, $routeParams,$http,$data,$location){
	if(!$data.getOrderId()){
			$location.path("/error");
			return;
		}
		$data.getOrder(function(response){
			$scope.order=response.order;
		   	$scope.pickup=response.pickup;
		   	$scope.commodityList=response.commodityList;
		   	$scope.constList=response.constList;
		});
});

app.controller('ShareController', function($scope, $routeParams){
	//$scope.name = 'Page2Controller';
	//alert(2);
});

app.controller('OrdersController', function($scope, $routeParams,$data,$location){
		if(!$data.openId){
			$location.path("/error");
			return;
		}
		$data.getOrders(function(response){
			$scope.orders=response;
		});
		$scope.order = function(orderId){
			alert("11");
		}
});

app.controller('ErrorController', function($scope, $routeParams){
	$scope.name = 'Page3Controller';
});

app.config(function($routeProvider, $locationProvider){
	$routeProvider
		.when('/', {
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
	$locationProvider.html5Mode(true);
});


