$(function() {
    'use strict';
    //Menu
    $('.menu-btn').on('click', function(e) {
        if ($(this).hasClass('active')) {
            $('.menu-nav').animate({
                right: '-23rem'
            }, 500);
            $(this).removeClass('active');
            $(this).find('i').attr('class', 'fa fa-bars');
        } else {
            $('.menu-nav').animate({
                right: '0px'
            }, 500);
            $(this).addClass('active');
            $(this).find('i').attr('class', 'fa fa-remove');
        }
    });
    $(document).on('click', '.menu-nav ul.menu > li', function(e) {
        if ($(window).width() < 991) {
            $(this).children('ul').toggle();
            e.stopPropagation();
        }
    });
    $(document).on('mouseover', '.menu-nav ul.menu > li', function(e) {
        if ($(window).width() > 991) {
            $(this).find('.sub-menu').show();
        }
    }).mouseout(function() {
        if ($(window).width() > 991) {
            $(this).find('.sub-menu').hide();
        }
    });
    //Search
    $('.icon-search').on('click', function(e) {
        if ($(this).hasClass('icon-search-1')) {
            if ($(window).width() < 577) {
                search_f();
            }
        } else {
            search_f();
        }
    });

    function search_f() {
        var $searchb = $('.search-box');
        if (!$searchb.hasClass('active')) {
            $searchb.addClass('active');
            $('.search-box input').val('');
            $searchb.fadeIn();
            $('.search-box input').focus();
        } else {
            $searchb.fadeOut();
            $searchb.removeClass('active');
        }
    }
    $('.search_btn').on('click', function(e) {
        $('.icon-search').trigger('click');
    });
    //Header resize
    window.addEventListener('scroll', function(e) {
        //var $header = $('.header-absolute .main-header,.header-fixed .main-header');
        var $tr = 0;
        if ($('header').height()) {
            if ($('.top-header').height()) {
                $tr = $('.top-header').height();
            } else {
                $tr = 0;
            }
        } else {
            $tr = 0;
        }
        var distanceY = window.pageYOffset || document.documentElement.scrollTop,
            shrinkOn = $tr;
        //var header = document.querySelector('header');
        if (distanceY > shrinkOn) {
            $('header').addClass('smaller');
        } else {
            if ($('header').hasClass('smaller')) {
                $('header').removeClass('smaller');
            }
        }
    });
});