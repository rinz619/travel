function restrictAlphabets(e) {
    var x = e.which || e.keycode;
    if (x >= 48 && x <= 57) return true;
    else return false;
  }
  
  $("#message_div").fadeOut(3000);
  
  function delete_modal(id) {
    $("#hid").val(id);
    $("#modaldemo5").modal("show");
  }
  
  function filtercategory(data) {
    var page = "1";
    if (data != "None") {
      page = data;
    }
  
    var search = $("#searchkey").val();
    var status = $("#status").val();
  
    var url = $("#url").val();
    $.ajax({
      url: url,
      type: "GET",
      data: { page: page, status: status, search: search },
  
      beforeSend: function () {
          $("#loaderid").show();
        },
        success: function (data) {
          $("#loaderid").hide();
        $(".table-responsive").html(data.template);
      },
    });
  }
  
  function categorystatus(id, vl) {
    page = $("#page").val();
  
    var search = $("#searchkey").val();
    var status = $("#status").val();
    var url = $("#url").val();
    $.ajax({
      url: url,
      type: "GET",
      data: {
        page: page,
        status: status,
        id: id,
        vl: vl,
        type: 1,
        search: search,
      },
  
      beforeSend: function () {
        $("#loaderid").show();
      },
      success: function (data) {
        $("#loaderid").hide();
  
        $(".table-responsive").html(data.template);
      },
    });
  }
  
  function deletecategory() {
    page = $("#page").val();
    id = $("#hid").val();
  
    var search = $("#searchkey").val();
    var status = $("#status").val();
    var url = $("#url").val();
    $.ajax({
      url: url,
      type: "GET",
      data: { page: page, status: status, id: id, type: 2, search: search },
  
      beforeSend: function () {
        $("#loaderid").show();
      },
      success: function (data) {
        $("#loaderid").hide();
        $("#modaldemo5").modal("hide");
  
        $(".table-responsive").html(data.template);
      },
    });
  }
  



  
  function set_sequence(id,seq){
    page=$("#page").val();


//    var search = $('#searchkey').val()
  var status = $('#status').val()
  var url = $('#url').val()
  $.ajax({
    url: url,
    type: 'GET',
    data: {page:page,status:status,id:id,seq:seq,type:4},

    beforeSend: function() {
      $("#loaderid").show();
  },
    success: function(data) {
      $("#loaderid").hide();

     $(".table-responsive").html(data.template)


    }
});
}