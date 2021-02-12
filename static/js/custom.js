
/*
 Make a row clickable by adding class='clickable-row' data-url='/your-url'
 */
jQuery(document).ready(function($) {

    $(".clickable-row").click(function() {
        window.location = $(this).data("url");
    });

    $(".nav-tabs a").click(function(){
        $(this).tab('show');
    });
    $('.nav-tabs a').on('shown.bs.tab', function(event){
        var x = $(event.target).text();         // active tab
        var y = $(event.relatedTarget).text();  // previous tab
        $(".act span").text(x);
        $(".prev span").text(y);
    });

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

//
// // Disable search and ordering by default
// $.extend( $.fn.dataTable.defaults, {
//     searching: false,
//     ordering:  false
// } );

$(document).ready( function () {
    $('#contract_table').DataTable();
    $('#uploads_table').DataTable( {
        "order": [[ 0, "desc" ]]
    } )
    $('#datasets_table').DataTable( {
        "order": [[ 0, "desc" ]]
    } );

} );

