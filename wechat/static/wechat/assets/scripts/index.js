    $(function(){
        //实现购物车弹层功能
        (function(status){//标识符->方法执行时传入一个参数true
            // TODO clean all touch events
            $('.overlay').on('click', function(){//TODO WTF click to tap   //给弹出背景绑定点击事件
                status = false;//点击时，让function下的私有status变为false
                window.popup_window_from_bottom();//触发window下popup_window_from_bottom这个事件
            });
            window.popup_window_from_bottom = function(){
                if(status&&CartManager.total!=0){//判断，如果status为true
                    status = false;//修改statusde值为false
                    $('.overlay').css('display', 'block');//修改样式名为overlay的行内样式，显示背景弹层
                    $('.popup-window-from-bottom').css("display","block");//调用jQuery中的slideToggle方法，让购物车弹层滑动显示
                } else {//如果status不是true,那么....
                    status = true;//修改status的值为true
                    $('.overlay').css('display', 'none');//修改样式名为overlay的行内样式，隐藏背景弹层
                    $('.popup-window-from-bottom').css('display', 'none');//修改购物车弹层的行内样式
                }
            }
        })(true);
    });

    $(function(){//把所有方法写在一个自执行函数里，形成闭包
        var PageManager = window.PageManager = {//初始化页面 哈市表
            pages: {},//用来存放通过className=__page__的页面->五个代表页面的div
            switchData: {},//用来存放
            init: function(){//初始化页面方法
                var that = this;//将当前作用下的this赋值给that   this->Object {pages: Object, switchData: Object}
                $('.__page__').each(function(){//通过jQuery中each()方法对className为__page__的每个元素规定运行的函数
                    var name = $(this).attr('name');//定义私有变量name 把通过attr返回的name属性下的属性值赋值给私有变量，this->div#index.__page__ 、div#checkout.__page__、div#Payment_success.__page__、div#Order_details.__page__、div#success_popup.__page__    name->index、checkout、success、details、popup
                    that.pages[name] = $(this);//把获取到的dom元素集合按照各自的name存放在page对象里面。当前作用域下的this是div，我们需要放在上一作用域下的pages对象里，所以需要用that
                });
            },
            jump: function(pageName, closure){//实现页面切页效果 参数1：要跳转的页面、参数2：dumpDataToCheckout
                var activePage = this.pages[pageName];//私有变量存储用户点击执行jump方法时，当前点击的dom元素。->是在pages对象中通过键取出
                if(!!activePage){//如果dom元素存在
					var closureMethod = null;
					if(typeof closure == 'function'){
						closureMethod = closure;
					} else {
						closureMethod = this.switchData[closure];//
					}
                    if(!!closureMethod){
                        if(!closureMethod(activePage)){
                            return;
                        }
                    }
                    for(var _ in this.pages){//循环pages对象下的每一个项->dom元素
                        var currentPage = this.pages[_];//把每一项赋值给私有变量
                        currentPage.css('display', 'none');//让每一项dom元素的display为none->元素不显示
                    }
                    activePage.css('display', 'block');//再让当前项dom元素display为block->元素显示
                }
            }
        };
        var CheckoutManager = window.CheckoutManager = {
            detail: null,//dom元素->ul
            detailTemplate: null,//checkout页下商品列表li模板
            total: null,//商品数量合计
            addresses: null,
            currentAddress: null,//用户选中收货地址
            tel: null,  //用户电话信息初始化
            commodities: null,//用户订单信息数据->
            user_info: null,
            batch_id: null,
            init: function(addresses, user_info, batch_id, tel_, form){
                var that = this;
                var tel = $('.__checkout_tel');
                tel.change(function(){
                    that.tel = $(this).val();
                });
		if(!!tel_ && tel_.length > 0){
			that.tel = tel_;
			tel.val(tel_);
		}
                this.addresses = addresses;
                this.user_info = user_info;
                this.batch_id = batch_id;
		this.form = form;
                this.detail = $('.__checkout_detail');
                this.detailTemplate = $('.__template_checkout_detail_item');
                this.detailTemplate.remove();
                this.detailTemplate.removeClass('.__template_checkout_detail_item');
                this.total = $('.__checkout_total');
                var checkbox_group = $('.__checkbox__');
                checkbox_group.click(function(){
                    checkbox_group.each(function(){
                        $(this).removeClass('checked');
                    });
                    $(this).addClass('checked');
                });
            },
	    formSubmit: function(orderId){
		var orderIdElement = this.form.find('.__field_orderId');
		orderIdElement.val(orderId);
		this.form.submit();
	    },
            setAddress: function(id){//获取用户选中地址方法
                var address = this.addresses[id];
                if(!!address){
                    this.currentAddress = address;
                }
            },
            fetchPayInfo: function(){
                var result = {};
                if(!this.tel || this.tel.length == 0){
                    result.status = 'failed';
                    result.msg = '电话号码不能为空';
                    return result;
                } else {
                    result.tel = this.tel;
                }
                if(!this.currentAddress){
                    result.status = 'failed';
                    result.msg = '请选择取货地';
                    return result;
                } else {
                    result.address = this.currentAddress.id;
                }
                result.status = 'success';
                result.commodities = [];
                for(var _ in this.commodities){
                    var commodity = this.commodities[_];
                    if(!commodity.quantity || commodity.quantity == 0){
                        continue;
                    }
                    var item = {
                        id: commodity.id,
                        quantity: commodity.quantity
                    };
                    result.commodities.push(item);
                }
                return result;
            },
            pay: function(){
              var that = this;
              var payInfo = this.fetchPayInfo();
              if(payInfo.status == 'failed'){
                return;
              }
              var cart_data = {
                nick_name: that.user_info.nickname,
                openid: that.user_info.openid,
                tel: payInfo.tel,
                ipaddress: '127.0.0.1',
                batch_id: that.batch_id,
                dist_id: payInfo.address,
                commodities: payInfo.commodities
              }
              $.ajax({
                data: JSON.stringify(cart_data),
                dataType: 'text',
                error: function(){},
                success: function(data, status, xhr){
                  data = (new Function('', 'return ' + data))();
		  if(!!data && data.errcode == 0){
			if(!!data.orderId){
				that.formSubmit(data.orderId);
			}
		  }
                  //if(!!window.WeChatIsReady && window.WeChatIsReady){
                  //  WeixinJSBridge.invoke(
                  //    'getBrandWCPayRequest', data.payRequest,
                  //    function(res){
                  //      if(res.err_msg == "get_brand_wcpay_request:ok" ) {
                  //        that.pay_callback(data);
                  //      }
                  //    }
                  //  );
                  //}
                },
                type: 'POST',
                url: 'unifiedOrder'
              });
            },
            dump: function(commodities){
                this.commodities = commodities;
                this.detail.empty();
                var total = 0;
                for(var _ in commodities){
                    var commodity = commodities[_];
                    if(!commodity.quantity || commodity.quantity == 0){
                        continue;
                    }
                    total += commodity.quantity * commodity.unit_price;
                    var item = this.detailTemplate.clone();
                    item.find('.__field_checkout_title').text(commodity.title);
                    item.find('.__field_checkout_quantity').text(commodity.quantity);
                    var price = (commodity.quantity * commodity.unit_price / 100).toFixed(2).toString();
                    item.find('.__field_checkout_price').text(price);
                    this.detail.append(item);
                }
                this.total.text('￥' + (total / 100).toFixed(2).toString());
            }
        };
        var CartManager = window.CartManager = {
            commodities: null,
            cartTemplate: null,
            cart: null,
            total: 0,
            init: function(data){
                var that = this;
                this.commodities = data;
                for(var _ in this.commodities){
                    var commodity = this.commodities[_];
                    var className = '.__field_quantity_' + commodity.id;
                    var domObject = $(className);
                    commodity.quantity_in_list = domObject;
                }
                this.cartTemplate = $('.__template');
                this.cartTemplate.remove();
                this.cartTemplate.removeClass('.__template');
                this.cart = $('.__cart');
                window.PageManager.switchData['dumpDataToCheckout'] = (function(commodities){
                    var closureMethod = function(){
                        if(!that.total || that.total == 0){
                            return false;
                        }
                        window.CheckoutManager.dump(commodities);
                        return true;
                    }
                    return closureMethod;
                })(data);
            },
            generateCartItem: function(commodity){
                var that = this;
                var domObject = this.cartTemplate.clone();
                domObject.find('.__field_title').text(commodity.title);
                var price = (commodity.quantity * commodity.unit_price / 100).toFixed(2).toString();
                domObject.find('.__field_price').text(price);
                domObject.find('.__field_quantity').text(commodity.quantity);
                domObject.find('.__button_add').click(function(){
                    that.add(commodity.id);
                });
                domObject.find('.__button_remove').click(function(){
                    that.remove(commodity.id);
                });
                return domObject;
            },
            updateCartItem: function(commodity, domObject){
                var price = (commodity.quantity * commodity.unit_price / 100).toFixed(2).toString();
                domObject.find('.__field_price').text(price);
                domObject.find('.__field_quantity').text(commodity.quantity);
            },
            add: function(id){
                var commodity = this.commodities[id];
                if(!!commodity){
                    if(!commodity.quantity){
                        commodity.quantity = 1;
                    }else{
                        commodity.quantity += 1;
                    }
                    this.render();
                }
            },
            remove: function(id){
                var commodity = this.commodities[id];
                if(!!commodity && !!commodity.quantity){
                    if(commodity.quantity > 1){
                        commodity.quantity -= 1;
                    } else{
                        commodity.quantity = 0;
                    }
                    this.render();
                }
            },
            empty: function(){
                for(var _ in this.commodities){
                    var commodity = this.commodities[_];
                    commodity.quantity = 0;
                }
                this.render();
                $('.overlay').css('display', 'none');
                $('.popup-window-from-bottom').css('display', 'none');
            },
            render: function(){
                var amount = 0;
                var total = 0;
                for(var _ in this.commodities){
                    var commodity = this.commodities[_];
                    if(!!commodity.quantity){
                        amount += commodity.quantity;
                        total += commodity.quantity * commodity.unit_price;
                        commodity.quantity_in_list.text(commodity.quantity);
                    }else{
                        commodity.quantity_in_list.text(0);
                    }
                    if(!commodity.item_in_cart){
                        if(!!commodity.quantity && commodity.quantity > 0){
                            var domObject = this.generateCartItem(commodity);
                            commodity.item_in_cart = domObject;
                            this.cart.append(domObject);
                        }
                    } else {
                        var domObject = commodity.item_in_cart;
                        if(!!commodity.quantity && commodity.quantity > 0){
                            this.updateCartItem(commodity, domObject);
                        } else {
                            domObject.remove();
                            commodity.item_in_cart = null;
                        }
                    }
                }
                this.render_amount(amount);
                this.render_total(total);
                this.total = total;
            },
            render_amount: function(amount){
                var domObject = $('.__amount');
                if(!amount && amount == 0){
                    domObject.css('display', 'none');
                } else{
                    domObject.css('display', 'block');
                    domObject.text(amount);
                }
            },
            render_total: function(total){
                var domObject = $('.__total');
                if(!total && total == 0){
                    domObject.text(0);
                }else{
                    total_string = (total / 100).toFixed(2).toString();
                    domObject.text('￥' + total_string);
                }
                return total;
            }
        };
    });
