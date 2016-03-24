var dataAry=[{"name":"康师傅妙芙欧式奶油味妙芙欧式奶油味妙芙欧式奶油味妙芙欧式奶油味","nym":5,"count":20},{"name":"康师傅妙芙欧式奶油味","nym":5,"count":20},{"name":"趣多多","nym":2,"count":10},{"name":"优乐美","nym":8,"count":2},{"name":"碧生源减肥茶","nym":5,"count":20},{"name":"康师傅红烧牛肉面","nym":5,"count":58},{"name":"奥利奥","nym":5,"count":2},{"name":"好丽友","nym":5,"count":20}];

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
$("#adds").click(function(){
    $("#one").css("display","none");
    $("#two").css("display","block");
});

/*$.ajax({
    url:"assets/scripts/json.txt?_=" + Math.random(),
    type:"get",
    datatype:"json",
    asnyc:true,
    success: function (data) {
        return data;
    }
});*/
