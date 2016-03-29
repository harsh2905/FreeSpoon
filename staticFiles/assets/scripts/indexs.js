window.onload=function(){
    var pageAry={};
    var allDom=document.getElementsByTagName("body")[0].getElementsByTagName("*");
    var activePage=null;
    for(var i=0;i<allDom.length;i++) {
        var cur = allDom[i];
        if (cur.getAttribute("cls") && cur.getAttribute("jid")) {
            var id=cur.getAttribute("jid");
            pageAry[id]=cur;
        }
        if (cur.getAttribute("method") && cur.getAttribute("target")) {
            cur.addEventListener("click", jump);
        }
        var defaultAttr = cur.getAttribute('default');
        if(!!defaultAttr && defaultAttr == 'yes'){
            activePage = cur;
            activePage.style.display = 'block';
        }
    }
    function jump(e){
        if(!!activePage){
            activePage.style.display="none";
        }
        var id= e.currentTarget.getAttribute("target");
        pageAry[id].style.display="block";
        activePage= pageAry[id];
    }
};
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
for(var _ in checkbox_group){
    var checkbox = checkbox_group[_];
    checkbox.onclick = function(){
        for(var i = 0; i < checkbox_group.length; i++){
            var checkbox_ = checkbox_group[i];
            checkbox_.classList.remove('checked');
        }
        this.classList.add('checked');
    };
}





