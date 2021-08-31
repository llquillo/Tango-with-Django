

$(document).ready(function() {
  
  $('.rango-page-add').click(function () {
    var categoryid = $(this).attr('data-categoryid'); var title = $(this).attr('data-title');
    var url = $(this).attr('data-url');
    var clickedButton = $(this);
    $.get('/rango/search_add_page/',
      {'category_id': categoryid, 'title': title, 'url': url}, 
      function(data) {
        $('#page-listing').html(data);
          clickedButton.hide();
      })
  });


  $('#search-input').keyup(function() { 
    var query;
    query = $(this).val();
    $.get('/rango/suggest/', {'suggestion': query}, 
    function(data) {
        $('#categories-listing').html(data);
    }) 
  });


  $('#about-btn').click(function() {
    alert("You clicked the button using JQuery!");
  });
  $('p').hover( 
    function() {
      $(this).css('color', 'red'); },
    function() {
      $(this).css('color', 'black');
    });
    $("#about-btn").click(function() { 
      msgStr = $("#msg").html() 
      msgStr = msgStr + " ooo, fancy!"
    $("#msg").html(msgStr)
  });


  $('#like_btn').click(function() {
    var category_id_var;
    category_id_var = $(this).attr('data-categoryid');
    $.get('/rango/like_category/', {'category_id': category_id_var},
    function(data){
      $('#like_count').html(data);
      $('#like_btn').hide();
    })
  });     
});
  