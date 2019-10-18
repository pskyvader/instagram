$(window).on('load', inicio);
$(window).on('load', register_sw);
$(window).on('load', activar_imagen);
$(window).on('scroll', activar_imagen);
$(window).on('resize', activar_imagen);

var application_name = $("meta[name='application-name']");
var websocket_url = application_name.data("websocket_url");
var path = application_name.data("path");
var modulo = application_name.data("modulo");
var url = application_name.data("url");
var googlemaps_key = application_name.data("googlemaps_key");
var max_size = application_name.data("max_size");
var max_size_format = application_name.data("max_size_format");
var is_mobile = $.browser.mobile;
var update_content = $('#update_content');
$.skylo('start');
$.skylo('set', 50);

function inicio() {
    var application_name = $("meta[name='application-name']");
    is_mobile = $.browser.mobile;
    $.material.init();
    $.skylo('end');
    modulo = application_name.data("modulo");
    url = application_name.data("url");
    Utility.animateContent();
    $('body').scrollSidebar();
    $('.select').dropdown(); // DropdownJS
    enquire.register("screen and (max-width: 1199px)", {
        match: function() { //smallscreen
            $('body').addClass('sidebar-collapsed');
        },
        unmatch: function() { //bigscreen
            $('body').removeClass('sidebar-collapsed');
            $('.static-content').css('width', '');
        }
    });


    $('body').sidebarAccordion();
    $(window).trigger('resize');
    $.wijets.make();
    prettyPrint();
    $('.tooltips,.tooltip, [data-toggle="tooltip"]').tooltip();
    //if (url.indexOf("detail") != -1) { } else { }
    inicio_detail();
    inicio_list();
    $(".dial").knob(); // knob
    $('textarea.autosize').autosize({
        append: "\n"
    });
    update_content = $('#update_content');
    if (update_content.length > 0) {
        setTimeout(get_update, 1000);
    }
}

var day = moment($('#time').data('time'), 'YYYY-MM-DD HH:mm:ss');
$('#time span').text(day.format('DD/MM HH:mm:ss'));

setInterval(function() {
    day = day.add(1, 'second');
    $('#time span').text(day.format('D/MM HH:mm:ss'));
}, 1000);

function register_sw() {
    if ('serviceWorker' in navigator) {
        // console.log('sw');
        navigator.serviceWorker.register(path + 'sw.js').then(function(registration) {
            // Registration was successful
            // console.log('ServiceWorker registration successful with scope: ', registration.scope);
        }).catch(function(err) {
            // registration failed :(
            console.log('ServiceWorker registration failed: ', err);
        });
    } else {
        console.log('no sw');
    }
}