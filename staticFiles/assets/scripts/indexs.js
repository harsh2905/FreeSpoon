/*(function(){
    var shop=document.querySelector(".shop");
    var popup=document.querySelector("#show");
    function show(){
        popup.className="show select";
        document.querySelector("#bg").className="bg select";
    }
    function hidDiv(){
        popup.className="show";
        document.querySelector("#bg").className="bg";
    }
    shop.onclick=function(){
        console.log(1);
        if(popup.className==="show"){
            show();
        }else {
            hidDiv();
        }
    };
})();*/
$(".regulator_right").bind("click",function(e){
    var tar= e.target;
    var count= Number($(this).find("span")[0].innerHTML);
    var boder_count=Number($(".shop").find("span")[0].innerHTML);

    if(tar.className=="block left"){
        if(count==0||boder_count==0){
            return
        }
        if(boder_count<2){
            $(".shop>span").hide();
        }
        $(this).find("span")[0].innerHTML--;
        $(".shop").find("span")[0].innerHTML--;
    }else if(tar.className=="block right"){
        $(".shop>span").show();
        $(this).find("span")[0].innerHTML++;
        $(".shop").find("span")[0].innerHTML++;
    }

});

