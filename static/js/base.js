
/*
 Make a row clickable by adding class='clickable-row' data-url='/your-url'
 */
jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data("url");
    });
});

