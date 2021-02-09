/*!
    * Start Bootstrap - SB Admin v6.0.2 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2020 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    (function($) {
    "use strict";

    // Commented out because it works only party. It kees the active menu-item acitive indeed, but the collapsable
    // menu-parent-item where it belongs to is folded in. So for the moment better to keep everything closed.

    // // Add active state to sidebar nav links
    // var path = window.location.href; // because the 'href' property of the DOM element is the absolute path
    //     $("#layoutSidenav_nav .sb-sidenav a.nav-link").each(function() {
    //         if (this.href === path) {
    //             $(this).parent().parent().addClass("show")
    //             $(this).addClass("active");
    //         }
    //     });

    // Toggle the side navigation
    $("#sidebarToggle").on("click", function(e) {
        e.preventDefault();
        $("body").toggleClass("sb-sidenav-toggled");
    });
})(jQuery);
