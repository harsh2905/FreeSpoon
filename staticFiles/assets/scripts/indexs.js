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
~function () {
    var shop = document.getElementsByClassName("shop")[0];
    var num = shop.getElementsByTagName("span")[0];
    var flag = -1;
    shop.onclick = function () {
        var popup = document.getElementsByClassName("popup")[0];
        var popup_box = document.getElementsByClassName("popup_box")[0];
        if (num.innerHTML > 0 && flag == "-1") {
            popup.style.display = "block";
            popup_box.style.display = "block";
            flag = flag * -1;
        } else if (num.innerHTML > 0 && flag == "1") {
            popup.style.display = "none";
            popup_box.style.display = "none";
            flag = flag * -1;
        }
    };
}();


/*var oUls=document.getElementById("add_li");
 var oLis=oUls.children;
 for(var i=0;i<oLis.length;i++) {
 var cur = oLis[i].children[0];
 (function(e){
 cur.onclick =function(){
 for(var i = 0; i < oLis.length; i++){
 oLis[i].children[0].className="div";
 console.log(1);
 }
 oLis[e].children[0].className="page";
 };
 })(i);
 }*/
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

var obj = {};
var counter = document.getElementsByClassName("counter");
for (var i = 0; i < counter.length; i++) {
    counter[i].onclick = function (e) {
        var el = e.srcElement;
        var cls = el.className;
        var input = this.getElementsByTagName("input")[0];
        var val = parseInt(input.value);
        var cnotent = this.getElementsByTagName("span");
        var shop = document.getElementsByClassName("shop")[0].getElementsByTagName("span")[0];
        var unit_scrip = {};
        switch (cls) {
            case "block left":
                if (val > 0) {
                    unit_scrip[this.id] = input.value;
                    input.value = val - 1;
                    shop.innerHTML = Number(shop.innerHTML) - 1;
                }
                break;
            case "block right":
                shop.style.display = "block";
                shop.innerHTML = Number(shop.innerHTML) + 1;
                input.value = val + 1;
                break;

            default:
                break;
        }
    }
}



