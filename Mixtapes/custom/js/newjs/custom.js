$(document).ready(function() {

    var navbarHeight = $('.navbar.navbar-fixed-top').height();

    //scrolling to the specific class
    var hash = window.location.hash;
    if (hash) {
        hash = hash.replace('#','');
        if ($('.' + hash).length > 0) {
            setTimeout(function() {
                $.scrollTo($('.' + hash), {duration: 500, offset:-navbarHeight });
            }, 250);
        }
    }

    //scrolling to add comment form
    $("[data-scroll-to='button']").click(function(){
        $.scrollTo($("[data-scroll-to='target']"), {duration: 500, offset:-navbarHeight });
    });

    //tooltip init - only for notouch
    if (!Modernizr.touch) {
        $("[data-toggle='tooltip']").tooltip();
    }

    //img-square list animation when csstransitions off
    if ((!Modernizr.csstransitions) && (!Modernizr.touch)) {
        $('.item-img-square').hover(function(){
            $(this).find('.description').animate({'top': '0'}, 350);
        }, function() {
            $(this).find('.description').stop(true, false).animate({'top': '-100%'}, 350);
        });
    }

});