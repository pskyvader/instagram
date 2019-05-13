$('body').on('click', 'div.navbar-collapse li.nav-item', function() {
    $('div.navbar-collapse li.nav-item').removeClass('active');
    $(this).addClass('active');
});
$('footer h3.btn-desplegable').on('click', function() {
    var ul = $(this).siblings('.desplegable');
    var icono = $('.icono', this);
    icono.toggleClass('open');
    ul.slideToggle();
});


$('.dropdown-menu .dropdown-toggle').on('click', function(e) {
    if (!$(this).next().hasClass('show')) {
        $(this).parents('.dropdown-menu').first().find('.show').removeClass("show");
    }
    var $subMenu = $(this).next(".dropdown-menu");
    $subMenu.toggleClass('show');


    $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function(e) {
        $('.dropdown-submenu .show').removeClass("show");
    });
    return false;
});







$('body').on('click', '.disabled', function() {
    return false;
});
$('body').on('click', 'a:not(.disabled)', function(e) {
    if ($(this).prop('target') != '_blank') {
        var href = $(this).prop('href');
        if (check_link(href) && $(location).prop('href') != href) {
            if ($(this).closest('.menu-nav').length > 0) {
                $('.menu-btn').click();
            }
            cargar_ajax(href);
            e.preventDefault();
        }
    }
});
$(window).on('popstate', function(e) {
    var href = e.currentTarget.location.href;
    if (check_link(href)) {
        cargar_ajax(href, false);
    }
});

function formato_precio(n, c, d, t) {
    var c = isNaN(c = Math.abs(c)) ? 2 : c,
        d = d == undefined ? "," : d,
        t = t == undefined ? "." : t,
        s = n < 0 ? "-" : "",
        i = String(parseInt(n = Math.abs(Number(n) || 0).toFixed(c))),
        j = (j = i.length) > 3 ? j % 3 : 0;

    return "$" + s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
};

function formato_fecha(fecha) {
    fecha = new Date(fecha);
    var mm = fecha.getMonth() + 1; //January is 0!
    var yyyy = fecha.getFullYear();
    var dd = fecha.getDate();

    if (dd < 10) {
        dd = '0' + dd;
    }

    if (mm < 10) {
        mm = '0' + mm;
    }

    fecha = yyyy + '-' + mm + '-' + dd;
    return fecha;
}


function go_url(url, data_form) {
    if (check_link(url) && $(location).prop('href') != url) {
        cargar_ajax(url, true, data_form);
    } else {
        $(location).prop('href', url);
    }
}


function check_link(href) {
    if (href.indexOf(path) < 0) return false;
    else if (href == '') return false;
    else if (href.indexOf('#') >= 0) return false;
    else if (href.indexOf('jpg') >= 0) return false;
    else if (href.indexOf('png') >= 0) return false;
    else if (href.indexOf('jpeg') >= 0) return false;
    else if (href.indexOf('pdf') >= 0) return false;
    else if (href.indexOf('xlsx') >= 0) return false;
    else if (href.indexOf('lsx') >= 0) return false;
    else return true;
}

function cargar_ajax(href, push, data_form) {
    if (typeof(push) == 'undefined') {
        push = true;
    }
    if (typeof(data_form) == 'undefined') {
        data_form = "";
    }
    var actualizado = false;
    var actualizado_head = false;
    var valido = true;
    setTimeout(function() {
        if (!actualizado) {
            $('.preloader,.preloader i').fadeIn('fast');
            $('#contenido-principal').html('');
            //$(e).addClass('view overlay hm-white-strong');
            //$(e).prepend($('#cargando').html());
        }
    }, 200);
    setTimeout(function() {
        if (!actualizado) {
            $(location).prop('href', href);
            valido = false;
        }
    }, 1500);
    $.post(href, data_form + '&ajax_header=true', function(data) {
        if (data.current_url != href) {
            console.log(data.current_url, href);
            $(location).prop('href', href);
            valido = false;
        } else {
            var an = $("meta[name='application-name']");
            document.title = data.title;
            $("meta[property='og\\:site_name']").prop("content", data.title);
            $("meta[property='og\\:title']").prop("content", data.title);
            $("meta[property='og\\:url']").prop("content", data.current_url);
            an.data("modulo", data.modulo);
            an.data("url", data.current_url);
            if (data.image) {
                $("meta[property='og\\:image']").prop("content", data.image_url);
            } else {
                $("meta[property='og\\:image']").prop("content", data.logo);
            }
            if (data.description) {
                $("meta[name='description']").prop("content", data.description_text);
                $("meta[name='og\\:description']").prop("content", data.description_text);
            } else {
                $("meta[name='description']").prop("content", data.description_text);
                $("meta[name='og\\:description']").prop("content", data.description_text);
            }
            if (data.keywords) {
                $("meta[name='keywords']").prop("content", data.keywords_text);
            }
            if (push) history.pushState(data.current_url, data.title, data.current_url);
            actualizado_head = true;
            iniciar(actualizado, actualizado_head, data_form);
        }
    }).fail(function(jqXHR) {
        console.log(jqXHR.responseText);
        $(location).prop('href', href);
        valido = false;
    });
    $.post(href, data_form + '&ajax=true', function(data) {
        if (valido) {
            actualizado = true;
            $('#contenido-principal').html(data);
            iniciar(actualizado, actualizado_head, data_form);
        }
    }).fail(function(jqXHR) {
        console.log(jqXHR.responseText);
        $(location).prop('href', href);
        valido = false;
    });
}

function iniciar(body, head, data_form) {
    if (body && head) {
        $('#contenido-principal').css('opacity', 1).removeClass();
        if (typeof inicio === "function") {
            inicio();
        }
        activar_imagen();
        if (data_form == '') {
            mover('body', 0);
        }
        //$('#navbarCollapse').removeClass('show');
    }
}



function activar_imagen() {
    $('source[data-srcset]').each(function() {
        if (is_visible($(this))) {
            load_source($(this));
        }
    });

    $('.blur[data-background]').each(function() {
        if (is_visible($(this))) {
            load_background($(this));
        }
    });
    $('img[data-src]').each(function() {
        if (is_visible($(this))) {
            load_image($(this));
        }
    });
    $('.bg-offset[data-image-src]').each(function() {
        if (is_visible($(this))) {
            bg_image($(this));
        }
    });

    $('iframe[data-src]').each(function() {
        if (is_visible($(this))) {
            load_iframe($(this));
        }
    });
}

function load_image(image) {
    if (typeof($(image).data('src')) != 'undefined' && $(image).data('src') != '') {
        var src = $(image).data('src');
        $(image)[0].removeAttribute('data-src');
        $(image).prop('src', src).on('load', function(e) {
            $(e.target).fadeIn();
        });
    }
}

function load_source(source) {
    if (typeof($(source).data('srcset')) != 'undefined' && $(source).data('srcset') != '') {
        var srcset = $(source).data('srcset');
        $(source)[0].removeAttribute('data-srcset');
        $(source).prop('srcset', srcset);
    }
}


function load_background(background) {
    if (typeof($(background).data('background')) != 'undefined' && $(background).data('background') != '') {
        var back = $(background).data('background');
        $(background).css('background-image', 'url(' + back + ')');
        $(background)[0].removeAttribute('data-background');
    }
}

function bg_image(bg) {
    if ($(bg).data('image-src')) {
        var $img_source = $(bg).data('image-src');
        $(bg).css('background-image', 'url(' + $img_source + ')');
        $(bg)[0].removeAttribute('data-image-src');
    }
}

function load_iframe(iframe) {
    if ($(iframe).data('src')) {
        var src = $(iframe).data('src');
        $(iframe)[0].removeAttribute('data-src');
        $(iframe).prop('src', src);
    }
}


function is_visible(images) {
    var $w = $(window),
        th = 0;

    var $e = $(images);
    if ($e.is(":hidden")) {
        return false;
    } else {
        var wt = $w.scrollTop(),
            wb = wt + $w.height(),
            et = $e.offset().top,
            eb = et + $e.height();

        return eb >= wt - th && et <= wb + th;

    }
}

var createObjFromURI = function() {
    var uri = decodeURI(location.search.substr(1));
    var params = Object();
    if (uri != '') {
        var chunks = uri.split('&');
        for (var i = 0; i < chunks.length; i++) {
            var chunk = chunks[i].split('=');
            if (chunk[0].search("\\[\\]") !== -1) {
                if (typeof params[chunk[0]] === 'undefined') {
                    params[chunk[0]] = [chunk[1]];
                } else {
                    params[chunk[0]].push(chunk[1]);
                }
            } else {
                params[chunk[0]] = chunk[1];
            }
        }
    }
    return params;
};

function create_url(extra, data, url) {
    if (typeof(url) == 'undefined' || url == null) {
        url = location.origin + location.pathname;
    }
    if (typeof(extra) != 'undefined' && extra != null) {
        if (url == path) {
            url += extra;
        } else {
            url += '/' + extra;
        }
    }
    if (typeof(data) != 'undefined' && data != null) {
        if (Object.keys(data).length > 0) {
            url += '?' + $.param(data);
        }
    } else {
        url += location.search;
    }

    url = url.split("%20").join("+");
    url = url.split("%2B").join("+");
    url = url.split("%2F").join("/");
    return url;
}


function mover(elemento, tiempo, delay) {
    var alto = 0;
    if (delay != 0) {
        setTimeout(function() {
            $('html, body').animate({
                scrollTop: ($(elemento).first().offset().top - alto)
            }, tiempo);
        }, delay);
    } else {
        $('html, body').animate({
            scrollTop: ($(elemento).first().offset().top - alto)
        }, tiempo);
    }
}

var notify = null;

function notificacion(mensaje, tipo, url) {
    if (tipo == 'error') tipo = 'danger';
    if (notify != null) {
        notify.close();
    }
    var options = {
        message: mensaje,
        icon: 'fa fa-exclamation-circle',
    };
    var settings = {
        type: tipo
    };
    if (url) {
        options.url = url;
        options.target = '_self';

        settings.delay = 10000;
        settings.timer = 30;
        settings.mouse_over = 'pause';
        settings.showProgressbar = true;
        $('body').on('click', 'div[data-notify="container"]', function() {
            notify.close();
        });
    }

    notify = $.notify(options, settings);
}



function barra(porcentaje) {
    /*if (porcentaje >= 0 && porcentaje < 100) {
        $.skylo('show', function() {
            $.skylo('set', porcentaje);
        });
    } else {
        setTimeout(function() {
            $.skylo('end');
        }, 500);
    }*/
}
$.fn.removeClassRegex = function(regex) {
    return $(this).removeClass(function(index, classes) {
        return classes.split(/\s+/).filter(function(c) {
            return regex.test(c);
        }).join(' ');
    });
};