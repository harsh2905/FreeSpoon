/**
 * Created by Andy on 2016/3/28.
 */

function Item(){
    var that = this;
    this.title = null;
    this.unitPrice = null;
    this.num = 0;
    this.board = null;//显示数量的dom元素
    this.cart = null;//购物车
    this.addNum = function(){
        this.num += 1;
        //修改this.board元素
        this.cart.render();
    }
    this.removeNum = function(){
        this.num -= 1;
        //修改this.board元素
        this.cart.render();
    }
}


function Cart(){
    var that = this;
    this.init = function(domTotal, domSummary, data){
        that.domTotal = domTotal;
        that.domSummary = domSummary;
        //为data中的每一项，构造一个Item对象，并且添加到this.items中
        for(var _ in data){
            var item = new Item();
            item.cart = that;
            //为item赋值
            var domItem = null;//构造一个Dom元素，并且添加到页面中
            //为domCalc计算器绑定下面2个事件
            function addItem(){
                //修改items集合
            }// 添加商品方法
            function removeItem(){
                //修改items集合
            }// 移除商品方法
            that.items.append(item);
        }
    }
    this.total = function(){
        for(var _ in that.items){
            // 计算总数
        }
    }
    this.summary = function(){
        for(var _ in that.items){
            // 计算总价
        }
    } // 单位是分
    this.render = function(){
        //调用total方法，获取商品总数，并修改domTotal元素
        //调用summary方法，获取商品总价，并修改domSummary元素
    }
    this.items = {}; // Object Item
}

var cart = new Cart();
var domTotal = null;// 查找dom元素
var domSummary = null;
var data = null; //From Server-Side
cart.init(domTotal, domSummary, data);

