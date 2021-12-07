$(document).ready(function()
{
    $(".post").hover(function()
    {
        $(this).css("background-color", "aquamarine");
    },
    function()
    {
        $(this).css("background-color", "cornflowerblue");
    });
   // Jquery form validation just demo code
   $.validator.addMethod("strong_password", function (value, element)
   {
    let password = value;
    if (!(/^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[@#$%&])(.{8,20}$)/.test(password)))
    {
        return false;
    }
    return true;
}, 
function (value, element)
{
    let password = $(element).val();
    if (!(/^(.{8,20}$)/.test(password))) {
        return 'Password must be between 8 and 20 characters long.';
    }
    else if (!(/^(?=.*[A-Z])/.test(password))) {
        return 'Password must contain atleast one uppercase.';
    }
    else if (!(/^(?=.*[a-z])/.test(password))) {
        return 'Password must contain atleast one lowercase.';
    }
    else if (!(/^(?=.*[0-9])/.test(password))) {
        return 'Password must contain atleast one digit.';
    }
    else if (!(/^(?=.*[@#$%&])/.test(password))) {
        return "Password must contain special characters from @#$%&.";
    }
    return false;
});
    //end custome validation test
   $("#registerfrm").validate(
    {
            rules:
            {
                username: 'required',
                email:{required:true,
                    email:true},
                password:{required:true,
                          minlength:5,
                          strong_password:true },
                con_password:{required:true,
                                minlength:5,
                                equalTo:"[name=password]"
                                }
            },
            messages:
            {
                username:"Please Enter Your Username",
                email:{ 
                        required:"Please Enter your Email",
                        email:"Please Enter Valid Email" 
                       },
                password:{required:"Please Enter Your Password",
                           minlength:"Password Must be minimum 5 characters",
                           },
                con_password:{required:"Please Enter conform Password",
                                minlength:"Password Must be minimum 5 characters",
                            equalTo:"Enter Confirm Password Same as Password" }
            },
            highlight:function(element)
            {
                $(element).addClass('highlight_cls');
                $(element).removeClass('unhighlight_cls');
            },
            unhighlight:function(element)
            {
                $(element).removeClass("highlight_cls");
                $(element).addClass('unhighlight_cls');
            },
            submitHandler:function(form,e)
            {
                e.preventDefault();
                var row_data = $('#registerfrm').serializeArray();
                var userdata=new FormData();
                $.each(row_data, function(key, input)
                {
                    userdata.append(input.name,input.value);
                });
                console.log(userdata);
                    $.ajax({
                            type: "POST",
                            enctype: "multipart/form-data",
                            url:'/user_reg',
                            data:userdata,
                            processData: false,
                            contentType: false,
                            cache: false,
                            beforeSend: function()
                            {
                               $(".loader").css("display", "block");
                            },
                            success: function(response)
                            {
                                if(response.status == "True")
                                {
                                    console.log("This True Block");
                                    $('#registerfrm').trigger('reset');  +  
                                    var row = '<tr><td>' + response.username+ '</td><td>' + response.email + '</td><td>' + response.password + '</td></tr>';
                                    $('#tablebody').append(row);
                                    $.notify("Record Inserted Succesfully", "success");
                                    $(".loader").css("display", "none");
                                    $("#unm,#email,#pass,#cpass").removeClass('unhighlight_cls');
                                }
                                if(response.status == "False")
                                {
                                    console.log("This False Block");
                                    $(".loader").css("display", "block");
                                    $('#registerfrm').trigger('reset'); 
                                    $.notify("Username or Mail Already Exist...", "error");
                                    $(".loader").css("display", "none");
                                    $("#unm,#email,#pass,#cpass").removeClass('unhighlight_cls');
                                }        
                            },
                            // error:function(request, status, error,resp)
                            // {
                            //     console.log(request.res)
                            //     console.log(status.res,'Status')
                            //     console.log(error.res,'Error')
                            //     console.log(resp,'Error')
                            // }   
                    });//ajax end function  
            }
    }); // end validation
   
    $("#search_name").on("keyup",function()
    {
        var search_data=$("#search_name").val();
        console.log(search_data);
        content={"term":search_data}
        $.ajax({
            type:"POST",
            url:"/live_data", 
            data:content,
            datatype:"json",
            success: function(response)
            { 
                $("#disp_livedata").empty();
                if(response.result != "") 
                { 
                    $("#fulltbl").css('display', "block");
                    for(var i=0;i<response.result.length;i++)
                    {
                    $("#disp_livedata").append("<tr><td>"+response.result[i]+"</td></tr>");
                    }  
                }
                else
                {
                    $("#fulltbl").css('display', "block");
                    $("#disp_livedata").html("<tr><td>"+response.error+"</td></tr>");
                }
            }

        });
    });
    //password hide show function
    var bb=$("#password").attr("type");//just practive perpose
    var pass_val=$("#password").val();
    var b=null;

    $("#password").keypress(function()
        {
                $("#show").css('display','block');
                $("#show").click(function()
                {
                    $("#password").attr("type","text");
                    $("#show").css('display','none');
                    $("#hide").css('display','block');
                });
                $("#hide").click(function()
                {
                    $("#password").attr("type","password");
                    $("#show").css('display','block');
                    $("#hide").css('display','none');
                }
                );         
        }
    );// end password show function


    //For Pagination perpose
      $("#empTable").DataTable({
          proccessing: true,
          serverSide: true,
          serverMethod: "POST",
          'ajax':{url:'/pagination'},
          lengthMenu:[[5,10,25,50,-1],[5,10,25,50,'All']],
          seraching: true,
          'columns':[
                        {data: 'username'},
                        {data: 'email'},
                        {data: 'password'},
                    ]
      });

        $("[name='mycheckbox[]']").click(function() {
            if ($(this).is(':checked','false')) 
            {
      
                console.log($(this).attr('value'))
                $('#'+'del_check'+$(this).attr('value')).css('background','#ED6F89');
             }
          });

    // $("input[type=checkbox]").css('background','red');  
      $("#del_btn").click(function () 
      {
            var b=$("input[type='checkbox']").val();
            // var row_data = $('#del_frm').serializeArray();
            // var userdata=new FormData();
            // $.each(row_data, function(key, input)
            // {
            //     userdata.append(input.name,input.value);
            // });
            var val = [];
            $(':checkbox:checked').each(function(i)
            {
                val[i] = $(this).val();
                console.log(val[i])
                $("#del_check"+val[i]).css('background','pink');
            });
            
          
            console.log(val);
            request_dict={'data':val}
            $.ajax({
                type: "POST",
                url:"/delete_user_record",
                data:request_dict,
                datatype:"json",
                success:function(response)
                {
                    console.log(response.success);
                    // console.log(response.del_id,'backend response')
                    for(var i=0; i<response.del_id.length;i++)
                    {
                        $("#del_check"+response.del_id[i]).fadeOut('slow');
                    }
                    $.notify("Records Deleted Successfully", "success");
                },
            });
        });

}); // document.ready end

function edit_data(id)
{

    postid={'id':id}
    console.log(postid['id']);
    $.ajax({
        url:"/edit_data",
        type:"POST",
        data:postid,
        datatype:"json",
        success:function(response)
        {
            console.log(response.id,response.body);
            $("#modal_id").val(response.id);
            $("#modal_body").val(response.body);
        }
    });

}

function update_data()
{
    var row_data = $('#modal_form').serializeArray();
    var form_data=new FormData();
    $.each(row_data,function(key,input)
    {
        form_data.append(input.name,input.value);
    });
    console.log(row_data);
    $.ajax({
        type:"POST",
        url:"/update_data",
        data:form_data,
        datatype:"json",
        processData: false,
        contentType: false,
        cache: false,
        success:function(response)
        {      
            console.log(response,'<<<<<<<<<<<<<');
            var id=response.id;
            $("#body_value"+id).text(response.comment);
            // $(".success_message").text("recorded successfully").show("fast");
            // $(".success_message").hide(3000);
            $(".success_message").css("display","block");
            setTimeout(function(){  $(".success_message").css("display","none");  },3000);
            $.notify("Record Updated Successfully", "success");
        }
    });
}

///bootbox logic 
function delete_data(id)
{
    data_id={}
    data_id['id']=id;
    bootbox.confirm({
    message: "Are You Sure You Want To Delete Your Data ?",
    buttons: {
        confirm:{
            label: 'Yes',
            className: 'btn-success'
        },
        cancel:{
            label: 'No',
            className: 'btn-danger'
        },
    },

    callback:function(result){
        console.log(result);
    if (result) {
        $.ajax({
            url:"/delete_post",
            type:"POST",
            data:data_id,
            success:function(response)
            {
                $("#post-"+id).remove();
                console.log(response.status);
            }
        });
    }
    else{
        
    }
    }
});
}




