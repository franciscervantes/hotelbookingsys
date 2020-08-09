



  // $(function() {
  //   $( ".datepicker" ).datepicker({
  //      dateFormat: "yy-mm-dd",
  //     changeMonth: true,
  //     changeYear: true,
  //     minDate: 0,
  //   });
  // });



// $("#logo").load(function() {
//   $(this).addClass("loaded");
// });




$(function () {
  // $('#ui-datepicker-div').css('clip', 'auto'); 
  $('.login-form').animate({ height: '70vh' }, 1000, 'linear');
  $('#logo').addClass("animate");
  $('#greet').addClass("animate-quote");
    console.log("wat")
     $("#datein").datepicker({
         minDate: 0,
         dateFormat: "yy-mm-dd",
         changeMonth: true,
         numberOfMonths: 1,
         changeYear: true,
         onClose: function (selectedDate, inst) {
             var minDate = new Date(Date.parse(selectedDate));
             minDate.setDate(minDate.getDate() + 1);
             $("#dateout").datepicker("option", "minDate", minDate);
         }
     });

     $("#dateout").datepicker({
         minDate: "+1D",
         dateFormat: "yy-mm-dd",
         changeMonth: true,
         numberOfMonths: 1,
         changeYear: true,
         onClose: function (selectedDate, inst) {
             var maxDate = new Date(Date.parse(selectedDate));
             maxDate.setDate(maxDate.getDate() - 1);
             $("#datein").datepicker("option", "maxDate", maxDate);
         }
     });
     // $("#id_room_id").value()
 });


$('#reservation-form').on('submit', function(e){

e.preventDefault();
token = $("#reservation-form").find('input[name=csrfmiddlewaretoken]').val();

  $.ajax({
       type : "POST", 
       url: $("#reservation-form").attr("data-ajax-target"), /* django ajax posting url  */
       data: {
        first_name : $('#id_first_name').val(),
        last_name : $('#id_last_name').val(),
        client_email: $('#id_client_email').val(),
        date_in: $('#datein').val(),
        date_out: $('#dateout').val(),
        client_phone: $('#id_client_phone').val(),
        room_id: $('#id_room_id').val(),
        csrfmiddlewaretoken: token,
        dataType: "json",

       },
       beforeSend: function () {
        $("#modal-reserve .modal-content").html("");
        $("#modal-reserve").modal("show");
      },
       
       success: function(data){
          // $('#output').html(data.msg) /* response message */
          console.log(data);
          if(data.status == 'created'){
            toastr.success('Successfully created');
            $("#modal-reserve .modal-content").html(data.html_form);
            // $("#booking").html(data.reservation);
            // $("#modal-reserve").modal("hide");
          }
          else{
            $("#modal-reserve").modal("hide");
            toastr.error('Invalid Dates or Room Type Unavailable')
          }
       },

       failure: function() {
           console.log("error");
       }


   });





});  



   var loadForm = function () {
    console.log("hi");
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-reserve .modal-content").html("");
        $("#modal-reserve").modal("show");
      },
      success: function (data) {
        $("#modal-reserve .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    console.log("here");
    var form = $(this);
    $.ajax({
      url: form.attr("data-url"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        console.log(data.status);
        if (data.status == "created") {
          toastr.success('Reservation Successfully Updated');
          $("#reserve-table tbody").html(data.reservation_list);
          $("#modal-reserve").modal("hide");
        }else if(data.status == 'deleted'){
          toastr.success('Reservation Successfully Deleted');
          $("#reserve-table tbody").html(data.reservation_list);
          $("#modal-reserve").modal("hide");
        }else if(data.status =='invalid_delete'){
          toastr.error('Invalid Deletion');
          $("#modal-reserve .modal-content").html(data.html_form);
        }else if(data.status == 'created room'){
          toastr.success('Room Successfully Created');
          $("#reserve-table tbody").html(data.room_list);
          $("#modal-reserve").modal("hide");
        }else if(data.status == 'invalid room'){
          toastr.error('Room with the same Room Number already exists');
          $("#reserve-table tbody").html(data.room_type_list);
          $("#modal-reserve").modal("hide");
        }else if(data.status == 'edited room'){
          toastr.success('Room Successfully Edited');
          $("#reserve-table tbody").html(data.room_list);
          $("#modal-reserve").modal("hide");
        }else if(data.status == 'deleted room'){
          toastr.success('Room Successfully Deleted');
          $("#reserve-table tbody").html(data.room_list);
          $("#modal-reserve").modal("hide");
        }else if(data.status == 'deleted roomtype'){
          toastr.success('Roomtype Successfully Deleted');
          $("#reserve-table tbody").html(data.roomtype_list);
          $("#modal-reserve").modal("hide");
        }

        
        else {
          // console.log("nani2");
          toastr.error('Invalid');
          $("#modal-reserve .modal-content").html(data.html_form);
        }
      },
       failure: function() {
           console.log("error");
       }
    });
    return false;
  };


var saveRoomType = function () {
    console.log("here");
    var form = $(this);
    var token = form.find('input[name=csrfmiddlewaretoken]').val();
    var formData = new FormData();
    $image = $('#id_image')[0].files[0];
    $type_name = $('#id_type_name').val();
    $price = $('#id_price').val();
    $details = $('#id_details').val()
    formData.append('image', $image);
    formData.append('type_name', $type_name)
    formData.append('price', $price)
    formData.append('details', $details)

    formData.append('csrfmiddlewaretoken', token);
    // console.log(token);
    $.ajax({
      url: form.attr("data-url"),
      data: formData,
      type: form.attr("method"),
      csrfmiddlewaretoken: token,
      dataType: 'json',
      
      success: function (data) {
        console.log(data.status);
        if(data.status == 'edited roomtype'){
          toastr.success('Roomtype Successfully Edited');
          $("#reserve-table tbody").html(data.room_type_list);
          $("#modal-reserve").modal("hide");
        }else if(data.status == 'created roomtype'){
          toastr.success('Roomtype Successfully Created');
          $("#reserve-table tbody").html(data.room_type_list);
          $("#modal-reserve").modal("hide");
        }else if(data.status == 'invalid roomtype'){
          toastr.error('Invalid Roomtype or Roomtype with the same name already exists');
          $("#reserve-table tbody").html(data.room_type_list);
          $("#modal-reserve").modal("hide");
        }

        
        else {
          // console.log("nani2");
          toastr.error('Invalid');
          $("#modal-reserve .modal-content").html(data.html_form);
        }
      },
            cache: false,
            contentType: false,
            processData: false,
       failure: function() {
           console.log("error");
       }
    });
    return false;
  };


  /* Binding */
  $(".js-create-reserve").click(loadForm);
  $("#modal-reserve").on("submit", ".js-reserve-create-form", saveForm);

  // Update book
  $("#reserve-table").on("click", ".js-update-reserve", loadForm);
  $("#modal-reserve").on("submit", ".js-reserve-update-form", saveForm);

  // Delete book
  $("#reserve-table").on("click", ".js-delete-reserve", loadForm);
  $("#modal-reserve").on("submit", ".js-reserve-delete-form", saveForm);

    $(".js-create-reserve").click(loadForm);
  $("#modal-reserve").on("submit", ".js-roomtype-create-form", saveRoomType);


  //search
//   $("#searchInput").keyup(function () {
//     //split the current value of searchInput
//     var data = this.value.split(" ");
//     //create a jquery object of the rows
//     var jo = $("#fbody").find("tr");
//     if (this.value == "") {
//         jo.show();
//         return;
//     }
//     //hide all the rows
//     jo.hide();

//     //Recusively filter the jquery object to get results.
//     jo.filter(function (i, v) {
//         var $t = $(this);
//         for (var d = 0; d < data.length; ++d) {
//             if ($t.text().toLowerCase().indexOf(data[d].toLowerCase()) > -1) {
//                 return true;
//             }
//         }
//         return false;
//     })
//     //show the rows that match.
//     .show();
// }).focus(function () {
//     this.value = "";
//     $(this).css({
//         "color": "black"
//     });
//     $(this).unbind('focus');
// }).css({
//     "color": "#C0C0C0"
// });