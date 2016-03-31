
window.onload = function () {
    var pageAry = {};
    var allDom = document.getElementsByTagName("body")[0].getElementsByTagName("*");
    var activePage = null;
    for (var i = 0; i < allDom.length; i++) {
        var cur = allDom[i];
        if (cur.getAttribute("cls") && cur.getAttribute("jid")) {
            var id = cur.getAttribute("jid");
            pageAry[id] = cur;
        }
        if (cur.getAttribute("method") && cur.getAttribute("target")) {
            cur.addEventListener("click", jump);
        }
        var defaultAttr = cur.getAttribute('default');
        if (!!defaultAttr && defaultAttr == 'yes') {
            activePage = cur;
            activePage.style.display = 'block';
        }
    }
    function jump(e) {
        if (!!activePage) {
            activePage.style.display = "none";
        }
        var id = e.currentTarget.getAttribute("target");
        pageAry[id].style.display = "block";
        activePage = pageAry[id];
    }
};
function in_list(){

}
var checkbox_group = document.getElementsByClassName('__checkbox__');
for (var _ in checkbox_group) {
    var checkbox = checkbox_group[_];
    checkbox.onclick = function () {
        for (var i = 0; i < checkbox_group.length; i++) {
            var checkbox_ = checkbox_group[i];
            checkbox_.classList.remove('checked');
        }
        this.classList.add('checked');
    };
}

var shop = document.getElementsByClassName("shop")[0];
var popup = document.getElementsByClassName("popup")[0];
var popup_box = document.getElementsByClassName("popup_box")[0];
var flag = -1;
popup.onclick=function(){
    console.log(1);
    if( popup_box.style.display="block"){
        popup_box.style.display="none";
        popup.style.display="none";
    }
};
shop.onclick = function () {
    if (num[0].innerHTML > 0 && flag == "-1") {
        popup.style.display = "block";
        popup_box.style.display = "block";
        flag = flag * -1;
    } else if (num[0].innerHTML > 0 && flag == "1") {
        popup.style.display = "none";
        popup_box.style.display = "none";
        flag = flag * -1;
    }
};
(function () {
    var commodities = (new Function('', 'return ' + '{"1": {"cur":0,"quota": 1, "id": 1, "unit_price": 20, "title": "\u6cf0\u56fd\u6930\u9752"}, "3": { "cur":0,"quota": 1, "id": 3, "unit_price": 59, "title": "\u7ea2\u989c\u8349\u8393"}, "2": {"cur":0,"quota": 1, "id": 2, "unit_price": 28, "title": "\u83f2\u5f8b\u5bbe\u51e4\u68a8"}, "4": {"cur":0,"quota": 1, "id": 4, "unit_price": 0, "title": "\u8d85\u4fbf\u5b9c\u6c34\u679c"}}'))();
    var cart = $("#popup");
    var template = $("._template");
    num=$(".shop span");
    var invent=$("#invent");
    var inventory_list=$("._inventory_list");
    window.addCommodity = function (id) {
        var commodity = commodities[id];
        if (!!commodity) {
            if (!commodity.domeObject) {
                var item = template.clone();
                var inventory=inventory_list.clone();
                commodity.domeObject = item;
                commodity.dome_inventory_list = inventory;
                commodity.quantity = 1;
                item.find("._field_title").text(commodity.title);
                item.find("._field_price").text(commodity.unit_price.toFixed(2));
                num.text(1);
                item.find("._field_quantity").val(1);
                $('._field_quantity_' + id).val(1);
                inventory.find(".inventory_title").text(commodity.title);
                inventory.find(".inventory__price").text(commodity.quantity);
                inventory.find(".inventory__total").text((commodity.unit_price * commodity.quantity).toFixed(2));
                (function (id) {
                    item.find("._button_remove").click(function () {
                        window.removedCommodity(id);
                    });
                    item.find("._button_add").click(function () {
                        window.addCommodity(id);
                    });
                })(id);
                cart.append(item);
                invent.append(inventory);
                inventory_list.remove();
                template.remove();
            } else {
                commodity.quantity += 1;
                num.text(commodity.quantity);
                $('._field_quantity_' + id).val(commodity.quantity);
                commodity.domeObject.find("._field_quantity").val(commodity.quantity);
                commodity.domeObject.find("._field_price").text((commodity.unit_price * commodity.quantity).toFixed(2));
                commodity.dome_inventory_list.find(".inventory__price").text(commodity.quantity);
                commodity.dome_inventory_list.find(".inventory__total").text((commodity.unit_price * commodity.quantity).toFixed(2));
            }
        }
        total(id);
    };
    window.removedCommodity = function (id) {
        var commodity = commodities[id];
        if (!!commodity) {
            if (!!commodity.domeObject) {
                if (commodity.quantity > 1) {
                    commodity.quantity -= 1;
                    num.text(commodity.quantity);
                    $('._field_quantity_' + id).val(commodity.quantity);
                    commodity.domeObject.find("._field_quantity").val(commodity.quantity);
                    commodity.domeObject.find("._field_price").text((commodity.unit_price * commodity.quantity).toFixed(2));
                } else {
                    commodity.quantity -= 1;
                    $('._field_quantity_' + id).val(commodity.quantity);
                    commodity.domeObject.remove();
                    commodity.domeObject = null;
                }
            }
        }
        total(id);
    };
    function total(id){
        var commodity=commodities[id];
        var num=0;
        if(!!commodity){
            for(key in commodities){
                var a=(commodity.unit_price*commodity.quantity).toFixed((2));
                commodity.cur=a;
                num+=eval(commodities[key].cur);
            }
        }
        $("._total").text(num);
        $(".total_number").text(num);
        console.log(num);
        return num;
    };

    $("#del")[0].onclick=function(){
        console.log(commodities[1]);
        for(key in  commodities){
            commodities[key].quantity=0;
            if(!!commodities[key].domeObject) {
                commodities[key].domeObject.remove();

            }
        }
        $("._total").text(0);
        $(".total_number").text(0);
    }


})();




