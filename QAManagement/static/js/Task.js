var toggle = true;

$(".sidebar-icon").click(function() {
    if (toggle)
    {
        $(".page-container").addClass("sidebar-collapsed").removeClass("sidebar-collapsed-back");
        $("#menu span").css({"position":"absolute"});
    }
    else
    {
        $(".page-container").removeClass("sidebar-collapsed").addClass("sidebar-collapsed-back");
        setTimeout(function() {
            $("#menu span").css({"position":"relative"});
        }, 400);
    }

    toggle = !toggle;
});

$(window).load(function () {
    //content大小自适应
    var winheight = $(window).innerHeight();
    console.log(winheight)
    $("#content").css("height",(450/798)*winheight);
    //动态添加可选择文件
    $.ajax({
        url:"/getfilename/",
        type:"POST",
        success:function (data) {
            data = JSON.parse(data);
            filename = data["filename"];
            for(var i=0;i<data["filenum"];i++){
                if(filename[i].slice(1,4) != "已生成") {
                    $("<div class='filelogo' style='float:left;margin-top:2%'><table><tr><td><img src='/static/img/filelogo.png' class = 'notbechoosed' style='position:relative;cursor:pointer;z-index:1' onclick='haschoosed(this)'></img></td></tr><tr><td><span class='filename'>" + filename[i] + "</span></td></tr></table></div>").appendTo("#filechoose");
                }
                else{
                    $("<div class='filelogo' style='float:left;margin-top:2%'><table><tr><td><img src='/static/img/filelogo-unable.png' class = 'cantbechoosed' style='position:relative;cursor:pointer;z-index:1'></img></td></tr><tr><td><span class='filename'>" + filename[i] + "</span></td></tr></table></div>").appendTo("#filechoose");
                }
            }
        }
    })
})
//文件被选中
function haschoosed(obj) {
    var tdobj = obj.parentNode;
    console.log("choosed")
    //$("<i class=\"glyphicon glyphicon-ok-sign text-success\" style=\"position:relative;float:right;z-index:100\"></i>").appendTo(tdobj);
    tdobj.removeChild(obj);
    $("<img src='/static/img/filelogo3.png' class = 'bechoosed' style='position:relative;cursor:pointer;z-index:1' onclick='canclechoosed(this)'></img>").appendTo(tdobj)

}
//取消选中文件
function canclechoosed(obj) {
    var tdobj = obj.parentNode;
    tdobj.removeChild(obj);
    $("<img src='/static/img/filelogo.png' class = 'notbechoosed' style='position:relative;cursor:pointer;z-index:1' onclick='haschoosed(this)'></img>").appendTo(tdobj)
}
//运行选中文件
$("#dotask").click(function () {
    $("#result").empty();
    $("<div class=\"modal-header\">\n" +
        "                   <button type=\"button\" class=\"close\" data-dismiss=\"modal\"><span aria-hidden=\"true\">&times;</span><span class=\"sr-only\">Close</span></button>\n" +
        "                   <h4 class=\"modal-title\">Please wait for a moment</h4>\n" +
        "            </div>\n" +
        "              <div class=\"modal-body\">\n" +
        "                <div class=\"loader-inner line-scale-pulse-out-rapid\" style=\"position: absolute; left: 45%;\">\n" +
        "                  <div></div>\n" +
        "                  <div></div>\n" +
        "                  <div></div>\n" +
        "                  <div></div>\n" +
        "                  <div></div>\n" +
        "                </div>\n" +
        "                  <br>\n" +
        "                  <br>\n" +
        "                  <p>The program is currently running. Please wait for a moment and try not to close this popup window. You will be notified once the program has finished running.</p>\n" +
        "              </div>").appendTo($("#result"));
    // 运行函数
    var activea = $("#filechoose").find(".bechoosed");
    if(activea.length>0) {
        $('#dotask').attr({
            'data-toggle': 'modal',
            'data-target': '#Doexe'
        });
    }else{
        alert('You have not selected the webpage to be parsed. Please choose a webpage.');
    }
});
// 运行算法函数
function  bechoosedfiledom(){
    this.filebechoosed = new Array();
    this.filenames = new Array();
}//存放被选中的文件DOM对象
bechoosedfiledom = new bechoosedfiledom();
$(".Do").click(function () {
    var activea = $("#filechoose").find(".bechoosed");
    console.log(activea.length)
    if(activea.length>0) {
        var modelchoose = $("#model-body").find(".active")
        console.log(modelchoose.length);
        if(modelchoose.length>0) {
            //var filename = new Array();
            //将选中文件文件名放到数组中
            for (var i = 0; i < activea.length; i++) {
                var activetemp = activea[i];
                console.log(activetemp.parentNode.parentNode.nextSibling.firstChild.firstChild.innerHTML);
                bechoosedfiledom.filenames[i] = activetemp.parentNode.parentNode.nextSibling.firstChild.firstChild.innerHTML;
                bechoosedfiledom.filebechoosed[i] = activea[i];
                //activetemp.parentNode.parentNode.nextSibling.firstChild.firstChild.innerHTML = "(已生成)"+filename[i]
                //将已经生成了QA对的文件变成不可选
                //activea[i].classList.remove("bechoosed")
                //activea[i].classList.add("cantbechoosed")
            }
            /*var fileuable = $(".cantbechoosed");
            for (var i = 0; i < fileuable.length; i++) {
                var $unabletemp = fileuable[i];
                var tdobj = $unabletemp.parentNode;
                tdobj.removeChild($unabletemp);
                $("<img src='/static/img/filelogo-unable.png' class = 'cantbechoosed' style='position:relative;cursor:pointer;z-index:1'></img>").appendTo(tdobj);
                //文件名标记
            }*/
            //将文件名数组传递给后台
            $.ajax({
                type: "POST",
                url: '/choose_file/',
                data: {"filename": JSON.stringify(bechoosedfiledom.filenames)},
                success: function (data) {
                    filename.splice(0, filename.length);
                    data = JSON.parse(data)
                    console.log("选中的文件有：" + data["filename"]);
                }

            });
            //清空modelbody的子元素
            /*if ($(".modal-body").children('a').length != 0) {
            $(".modal-body").empty();
        }*/

            //开始显示等待画面
            $(this).attr({
                'data-toggle': 'modal',
                'data-target': '#wait'
            });
            //$('.line-scale-pulse-out-rapid').css('display','block');
            // 在上一个算法程序没有完成前，不能进行下一轮的使用
            $("#doexe").attr({
                'data-target': '#sorry'
            });

            //将选中的模板传递给后台
            var modelname = new Array();
            for (var i = 0; i <modelchoose.length; i++) {
                var $modeltemp = $(modelchoose[i]);
                console.log($modeltemp.find(".file-caption-info").html());
                modelname[i] = $modeltemp.find(".file-caption-info").html();

            }
            $.ajax({
                type: "POST",
                url: '/Doexe/',
                data: {"modelname": JSON.stringify(modelname)},
                success: function (data) {
                    //filename.splice(0, filename.length);
                    //console.log(data);
                    data = JSON.parse(data);
                    console.log('Number of Generated QA Pairs：' + data['num']);
                    //console.log(data['qa'][0]['question']);
                    for (i = 0; i < data['qa'].length; i++) {
                        console.log('Questions from the Generated QA Pairs：' + data['qa'][i]['question']);
                    }
                    // $('#wait').removeAttr('data-toggle');
                    // alert('完成');
                    //$("#wait").css('display','none');
                    //modal('hide');

                    $("#result").empty();
                    //显示完成
                    alert("The operation is complete. A total of " + data['num'] + " QA pairs have been generated this time.");

                    $("               <div class=\"modal-header\">\n" +
                        "                   <button type=\"button\" class=\"close\" data-dismiss=\"modal\"><span aria-hidden=\"true\">&times;</span><span class=\"sr-only\">Close</span></button>\n" +
                        "                   <h4 class=\"modal-title\">Run completed</h4>\n" +
                        "               </div>\n" +
                        "               <div class=\"modal-body\" id=\"model_body\">\n" +
                        "                  <p>The operation is complete. A total of " + data['num'] + " QA pairs have been generated this time." +
                        "                  <a href='/show_result' style='cursor:pointer' class=\"showresult\">Click to view the results</a>" +
                        "               </div>\n" +
                        "               <div class=\"modal-footer\">\n" +
                        "                   <button type=\"button\" class=\"btn btn-primary\" data-dismiss=\"modal\" onclick='saveQA()'>Confirm and Save</button>\n" +
                        "                   <button type=\"button\" class=\"btn btn-primary\" data-dismiss=\"modal\" onclick=''>Cancel Save</button>\n" +
                        "               </div>\n" +
                        "           </div>\n").appendTo($("#result"));
                    $("#doexe").attr({
                        'data-target': '#choose_file'
                    });
                }

            });
            //先生成后rename,将已生成QA对的文件传递给后台
            /*$.ajax({
                url: "/filerename/",
                type: "POST",
                data: {"unablefile": JSON.stringify(filename)},
                success: function (data) {
                    //location.reload();
                    console.log(data);
                }
            })*/
        }else{
            alert('You have not selected a web page extraction template. Please choose an appropriate template or create a new one.');
        }
    }else{
        alert('You have not selected a webpage for parsing. Please choose a webpage.');
    }
})
//保存生成的QA对
function saveQA(){
    $.ajax({
        url:"/saveQA/",
        type:"POST",
        success:function (data) {
            console.log(data)
            console.log(bechoosedfiledom.filebechoosed.length)
            var unablefilename = bechoosedfiledom.filenames;
            for(var i=0;i<bechoosedfiledom.filebechoosed.length;i++){
                //unablefilename[i] = bechoosedfiledom.filebechoosed[i].parentNode.parentNode.nextSibling.firstChild.firstChild.innerHTML;
                console.log(unablefilename[i])
                bechoosedfiledom.filebechoosed[i].parentNode.parentNode.nextSibling.firstChild.firstChild.innerHTML = "(已生成)"+unablefilename[i]
                //将已经生成了QA对的文件变成不可选
                bechoosedfiledom.filebechoosed[i].classList.remove("bechoosed")
                bechoosedfiledom.filebechoosed[i].classList.add("cantbechoosed")
            }
            var fileuable = $(".cantbechoosed");
            for (var i = 0; i < fileuable.length; i++) {
                var $unabletemp = fileuable[i];
                var tdobj = $unabletemp.parentNode;
                tdobj.removeChild($unabletemp);
                $("<img src='/static/img/filelogo-unable.png' class = 'cantbechoosed' style='position:relative;cursor:pointer;z-index:1'></img>").appendTo(tdobj);
                //文件名标记
            }
            //先生成后rename,将已生成QA对的文件传递给后台
            $.ajax({
                url: "/filerename/",
                type: "POST",
                data: {"unablefile": JSON.stringify(unablefilename)},
                success: function (data) {
                    //location.reload();
                    console.log(data);
                }
            })
        }
    })
}
//创建模板函数
$(".createModel").click(function () {
    $(this).attr({
        "data-toggle": 'modal',
        "data-target": '#createModel'
    })
})

$(".Docreate").click(function () {
    var activea = $("#filechoose").find(".bechoosed");
    console.log(activea.length)
    if(activea.length>0) {
        var filename = new Array();
        //将选中文件文件名放到数组中
        for (var i = 0; i < activea.length; i++) {
            var activetemp = activea[i];
            console.log(activetemp.parentNode.parentNode.nextSibling.firstChild.firstChild.innerHTML);
            bechoosedfiledom.filenames[i] = activetemp.parentNode.parentNode.nextSibling.firstChild.firstChild.innerHTML;
            bechoosedfiledom.filebechoosed[i] = activea[i]
            //activetemp.parentNode.parentNode.nextSibling.firstChild.firstChild.innerHTML = "(已生成)"+filename[i]
            //将已经生成了QA对的文件变成不可选
            //activea[i].classList.remove("bechoosed")
            //activea[i].classList.add("cantbechoosed")
        }
    }
    //不可选的文件用灰色图标显示
    /*var fileuable = $(".cantbechoosed");
    for(var i=0;i<fileuable.length;i++){
        var $unabletemp = fileuable[i];
        var tdobj = $unabletemp.parentNode;
        tdobj.removeChild($unabletemp);
        $("<img src='/static/img/filelogo-unable.png' class = 'cantbechoosed' style='position:relative;cursor:pointer;z-index:1'></img>").appendTo(tdobj);
        //文件名标记
        {#var spantemp = tdobj.parentNode.nextSibling.firstChild.firstChild.innerHTML;#}
        {#spantemp += "(已生成)"#}
    }*/
    var msg={};
    msg["begintitle"] = $("#begintitle").val();
    msg["endtitle"] = $("#endtitle").val();
    msg["littlebegintitle"] = $("#littlebegintitle").val();
    msg["littleendtitle"] = $("#littleendtitle").val();
    msg["tabbegin"] = $("#tabbegin").val();
    msg["tabend"] = $("#tabend").val();
    msg["imgbegin"] = $("#imgbegin").val();
    msg["imgend"] = $("#imgend").val();
    msg["topicalbegin"] = $("#topicalbegin").val();
    msg["topicalend"] = $("#topicalend").val();
    msg["description"] = $("#description").val();

    console.log(msg);
    //开始显示等待画面
    $(this).attr({
        'data-toggle': 'modal',
        'data-target': '#wait'
    });
    //$('.line-scale-pulse-out-rapid').css('display','block');
    // 在上一个算法程序没有完成前，不能进行下一轮的使用
    $("#doexe").attr({
        'data-target': '#sorry'
    });
    $.ajax({
        type:"POST",
        url:"/create_model/",
        data:{"createdata":JSON.stringify(msg)},
        success:function (data) {
            //filename.splice(0, filename.length);
            //console.log(data);
            data = JSON.parse(data);
            console.log('Number of Generated QA Pairs：'+data['num']);
            //console.log(data['qa'][0]['question']);
            for (i = 0 ; i < data['qa'].length ; i++){
                console.log('Questions from the Generated QA Pairs：'+data['qa'][i]['question']);
            }
            // $('#wait').removeAttr('data-toggle');
            // alert('完成');
            //$("#wait").css('display','none');
            //modal('hide');

            $("#result").empty();
            //显示完成
            alert("The operation is complete. A total of " + data['num'] + " QA pairs have been generated this time.");

            $("               <div class=\"modal-header\">\n" +
                "                   <button type=\"button\" class=\"close\" data-dismiss=\"modal\"><span aria-hidden=\"true\">&times;</span><span class=\"sr-only\">Close</span></button>\n" +
                "                   <h4 class=\"modal-title\">Run completed</h4>\n" +
                "               </div>\n" +
                "               <div class=\"modal-body\" id=\"model_body\">\n" +
                "                  <p>The operation is complete. A total of " + data['num'] + " QA pairs have been generated this time." +
                "                  <a href='/show_result' style='cursor:pointer' class=\"showresult\">Click to view the results</a>" +
                "               </div>\n" +
                "               <div class=\"modal-footer\">\n" +
                "                   <button type=\"button\" class=\"btn btn-primary\" data-dismiss=\"modal\" onclick='saveQA()'>Confirm and Save</button>\n" +
                "                   <button type=\"button\" class=\"btn btn-primary\" data-dismiss=\"modal\" onclick=''>Cancel Save</button>\n" +
                "               </div>\n" +
                "           </div>\n").appendTo($("#result"));
            $("#doexe").attr({
                'data-target': '#choose_file'
            });
        }
    });
    //先生成后rename,将已生成QA对的文件传递给后台
    /*$.ajax({
        url:"/filerename/",
        type:"POST",
        data:{"unablefile":JSON.stringify(filename)},
        success:function (data) {
            console.log(data);
        }
    })*/

});
//文件选中添加图标
function checkfile(checka) {
    var $checka = $(checka)
    if($checka.hasClass("active")){
        $checka.removeClass("active")
        checka.removeChild(checka.childNodes[0])

    }
    else{
        $checka.addClass("active")
        $checka.prepend($("<i class=\"glyphicon glyphicon-ok-sign text-success\" style='float:right;margin-top:4%'></i>"))
    }
}
//文件全选
$("#chooseall").click(function () {
    var fileunchoosed = $(".notbechoosed")
    for(var i=0;i<fileunchoosed.length;i++){
        var $temp = fileunchoosed[i]
        var tdobj = $temp.parentNode;
        tdobj.removeChild($temp);
        $("<img src='/static/img/filelogo3.png' class = 'bechoosed' style='position:relative;cursor:pointer;z-index:1' onclick='canclechoosed(this)'></img>").appendTo(tdobj)

    }
})
//文件取消全选
$("#cancleall").click(function () {
    var filechoosed = $(".bechoosed")
    for(var i=0;i<filechoosed.length;i++){
        var $temp = filechoosed[i]
        var tdobj = $temp.parentNode;
        tdobj.removeChild($temp);
        $("<img src='/static/img/filelogo.png' class = 'notbechoosed' style='position:relative;cursor:pointer;z-index:1' onclick='canclechoosed(this)'></img>").appendTo(tdobj)

    }
})

