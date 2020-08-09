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