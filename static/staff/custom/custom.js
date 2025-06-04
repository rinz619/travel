

function login(id){
  var url = '/staff/add_to_login'
  $.ajax({
    url: url,
    type: 'GET',
    data: {id:id},


    success: function(data) {
        if(data.status == true){
            location.reload();
        }
        

    }
});

}

function logout(id){
  var url = '/staff/add_to_logout'
  $.ajax({
    url: url,
    type: 'GET',
    data: {id:id},


    success: function(data) {
        if(data.status == true){
            location.reload();
        }
        

    }
});

}