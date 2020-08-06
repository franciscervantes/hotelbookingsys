



  // $(function() {
  //   $( ".datepicker" ).datepicker({
  //      dateFormat: "yy-mm-dd",
  //     changeMonth: true,
  //     changeYear: true,
  //     minDate: 0,
  //   });
  // });

$(function () {
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
       
       success: function(data){
          // $('#output').html(data.msg) /* response message */
          console.log(data);
          if(data.status == 'created')
            toastr.success('Successfully created');

          else{

            toastr.error('Invalid Dates')
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
        console.log("nani");
        if (data.status == "created") {
          toastr.success('Successfully created');
          $("#reserve-table tbody").html(data.reservation_list);
          $("#modal-reserve").modal("hide");


        }else if(data.status == 'deleted'){
          toastr.success('Successfully deleted');
          $("#reserve-table tbody").html(data.reservation_list);
          $("#modal-reserve").modal("hide");
        }else if(data.status =='invalid_delete'){
          toastr.error('Invalid Deletion');
          $("#modal-reserve .modal-content").html(data.html_form);
        }
        else {
          console.log("nani2");
          toastr.error('Invalid Edit');
          $("#modal-reserve .modal-content").html(data.html_form);
        }
      },
       failure: function() {
           console.log("error");
       }
    });
    return false;
  };




  /* Binding */

  // Update book
  $("#reserve-table").on("click", ".js-update-reserve", loadForm);
  $("#modal-reserve").on("submit", ".js-reserve-update-form", saveForm);

  // Delete book
  $("#reserve-table").on("click", ".js-delete-reserve", loadForm);
  $("#modal-reserve").on("submit", ".js-reserve-delete-form", saveForm);