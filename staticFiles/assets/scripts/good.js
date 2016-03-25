var dataAry=[{"name":"康师傅妙芙欧式奶油味妙芙欧式奶油味妙芙欧式奶油味妙芙欧式奶油味","nym":5,"count":20},{"name":"康师傅妙芙欧式奶油味","nym":5,"count":20},{"name":"趣多多","nym":2,"count":10},{"name":"优乐美","nym":8,"count":2},{"name":"碧生源减肥茶","nym":5,"count":20},{"name":"康师傅红烧牛肉面","nym":5,"count":58},{"name":"奥利奥","nym":5,"count":2},{"name":"好丽友","nym":5,"count":20}];
var provinceList=["北京市海淀区","北京市丰台区","北京市石景山区","北京市石朝阳北京市石景山区北京市石景山区石景山区北京市石景山区"];
~function(){
  var tab=document.getElementById("group-list");
  var frg=document.createDocumentFragment();
    for(var i=0;i<dataAry.length;i++){
        var cur=dataAry[i];
        var oTr=document.createElement("tr");
        oTr.className="spline block";
        for(var key in cur){
            var oTd=document.createElement("td");
            oTd.innerHTML=cur[key];
            oTr.appendChild(oTd);
        }
        frg.appendChild(oTr);
    }
    tab.appendChild(frg);
    frg=null;
}();

function define(){
    $("#one").css("display","block");
    $("#two").css("display","none");
    $(".adds-table td:eq(0)").html($(".infor").val());
}
$("#adds").click(function(){
    $("#one").css("display","none");
    $("#two").css("display","block");
});
$("#list_name").click(function(){
    $("#toggle").toggle(function(){});
});
$("#icon").click(function(){
    console.log(1);
});