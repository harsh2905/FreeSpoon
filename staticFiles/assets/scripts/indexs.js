$(".regulator_right").bind("click",function(e){
    var tar= e.target;
    var count= Number($(this).find("span")[0].innerHTML);
    var boder_count=Number($(".shop").find("span")[0].innerHTML);
    if(tar.className=="block left"||tar.className=="box_left block left"){
        if(count==0||boder_count==0){
            return
        }
        if(boder_count<2){
            $(".shop>span").hide();
        }
        $(this).find("span")[0].innerHTML--;
        $(".shop").find("span")[0].innerHTML--;
    }else if(tar.className=="block right"|| tar.className=="box_right block right"){
        $(".shop>span").show();
        $(this).find("span")[0].innerHTML++;
        $(".shop").find("span")[0].innerHTML++;
    }
    if(boder_count===1){
        $(".shop").unbind();
    }else if(boder_count>=1){

    }

});
$(".shop").bind("click",function(e){
    $(".popup").toggle();
    $(".popup_box").toggle();
});


$("#del").bind("click",function(){
    $(".popup").hide();
    $(".popup_box").hide();
});

$(".f_right").bind("click",function(){
    $("#index").hide();
    $("#checkout").show();
});
$("#black").bind("click",function(){
    console.log(1);
    $("#index").show();
    $("#checkout").hide();
});

