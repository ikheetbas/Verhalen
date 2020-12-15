
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
});
