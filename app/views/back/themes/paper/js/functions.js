$('body').on('click', '.disabled', function(e) {
    return false;
});
$('body').on('click', 'a:not(.disabled)', function(e) {
    if ($(this).prop('target') != '_blank') {
        var href = $(this).prop('href');
        if (check_link(href)) {
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
var habilitado = true;

function habilitar(valor) {
    habilitado = (valor) ? false : true;
    elementos = $('#guardar, #guardar-permanecer,#cancelar,.btn-group .btn,.guardar_modal,input:file,.eliminar_archivo,.btn-file,.acc-menu a,a#logout,table tbody tr');
    elementos.prop('disabled', habilitado).on("click", function() {
        return !habilitado;
    });
    if (habilitado) {
        elementos.css('opacity', '0.5');
        elementos.find('.fa-refresh').remove();
        elementos.prepend('<i class="fa fa-refresh fa-spin" style="position: absolute; left: 5px; top: calc(50% - 5px);"></i> ');
    } else {
        elementos.css('opacity', '1');
        elementos.find('.fa-refresh').remove();
    }
}
$.skylo({
    'flat': false,
});

function barra(porcentaje) {
    if (porcentaje >= 0 && porcentaje < 100) {
        $.skylo('show', function() {
            $.skylo('set', porcentaje);
        });
    } else {
        setTimeout(function() {
            $.skylo('end');
        }, 500);
    }
}
var alerta = null;

function notificacion(titulo, mensaje, tipo, callback) {
    if (alerta != null) {
        alerta.update({
            opacity: 0.5
        });
        alerta.remove();
    }
    if (titulo == false) return false;
    var options = {
        title: titulo,
        text: mensaje,
        type: tipo,
        icon: 'fa fa-close',
        styling: 'fontawesome'
    }
    if (callback) {
        options.hide = false;
        options.confirm = {
            confirm: true,
            buttons: [{
                text: callback.button,
                addClass: 'btn-raised',
                click: function(notice) {
                    callback.function();
                }
            }, null]
        };
        options.buttons = {
            closer: false,
            sticker: false
        };
    }
    alerta = new PNotify(options);
}
var a_f = [];

function notificacion_footer(mensaje) {
    if (mensaje == false) {
        $(a_f).each(function() {
            $(this).snackbar("hide");
        });
        a_f = [];
    }
    if (mensaje != false) {
        var a = $.snackbar({
            content: mensaje,
            timeout: 8000
        });
        var l = a_f.length;
        if (typeof(a_f[l - 1]) == 'undefined' || (a_f[l - 1][0].dataset.content != a[0].dataset.content)) {
            if (l > 0) {
                $(a_f).each(function(k, v) {
                    var b = (parseFloat($(this).css('opacity')) / 2);
                    if (b < 0.25) {
                        a_f.splice($.inArray(v, a_f), 1);
                        $(this).snackbar("hide");
                    } else {
                        $(this).css('opacity', b);
                    }
                });
            }
            a_f.push(a);
        } else {
            $(a).snackbar("hide");
        }
    }
}

function urlamigable(uri) {
    return String(uri).toLowerCase().replace(/\s/g, '-')
        .split(/[ÃÀÁÄÂãàáäâ]/).join("a")
        .split(/[ÈÉËÊèéëê]/).join("e")
        .split(/[ÌÍÏÎìíïî]/).join("i")
        .split(/[ÒÓÖÔòóöô]/).join("o")
        .split(/[ÙÚÜÛùúüû]/).join("u")
        .split(/[Çç]/).join("c")
        .split(/[Ññ]/).join("n")
        .split(/[^a-z0-9:/.\-\#]/).join("-")
        .split(/-+/).join("-")
        .replace(/^-*/, '')
        .replace(/-*$/, '');
}

function go_url(url, data) {
    if (check_link(url)) {
        cargar_ajax(url, true, data);
    } else {
        $(location).prop('href', url);
    }
}

function create_url(modulo, extra, data, url) {
    if (typeof(url) == 'undefined' || url == null) {
        if (typeof(modulo) == 'undefined' || modulo == null) {
            url = location.origin + location.pathname;
        } else {
            url = path + modulo;
        }
    }
    if (typeof(extra) != 'undefined' && extra != null) {
        url += '/' + extra;
    }
    if (typeof(data) != 'undefined' && data != null) {
        url += '?' + $.param(data);
    } else {
        url += location.search;
    }
    return url;
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
    barra(50);
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
            var e = $('#contenido-principal');
            $(e).empty().css('opacity', 0.5).append('<div class="panel-loading"><div class="panel-loader-circular"></div></div>');
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
            } else {
                $("meta[name='keywords']").prop("content", "");
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
        $('#contenido-principal').css('opacity', 1);
        if (typeof inicio === "function") {
            inicio();
        }
        activar_imagen();
        if (data_form == '') {
            mover('body', 0);
            notificacion(false);
        }
        barra(100);
    }
}


function activar_imagen() {
    $('img[data-src]').each(function() {
        if (typeof($(this).data('src')) != 'undefined' && $(this).data('src') != '') {
            if (isInViewport($(this)[0])) {
                var src = $(this).data('src');
                $(this)[0].removeAttribute('data-src');
                $(this).attr('src', src).on('load', function() {
                    $(this).fadeIn();
                });

            }
        }
    });
    $('source[data-srcset]').each(function() {
        if (typeof($(this).data('srcset')) != 'undefined' && $(this).data('srcset') != '') {
            if (isInViewport($(this)[0])) {
                var srcset = $(this).data('srcset');
                $(this)[0].removeAttribute('data-srcset');
                $(this).attr('srcset', srcset).on('load', function() {
                    $(this).fadeIn();
                });
            }
        }
    });

    $('.blur[data-background]').each(function() {
        if (typeof($(this).data('background')) != 'undefined' && $(this).data('background') != '') {
            if (isInViewport($(this)[0])) {
                var background = $(this).data('background');
                $(this).css('background-image', 'url(' + background + ')');
                $(this)[0].removeAttribute('data-background');
            }
        }
    });
}



function mover(elemento, tiempo, delay) {
    var alto = 65;
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

function isInViewport(el) {
    var rect = el.getBoundingClientRect();
    return (rect.bottom >= 0 && rect.right >= 0 && rect.top <= (window.innerHeight || document.documentElement.clientHeight) && rect.left <= (window.innerWidth || document.documentElement.clientWidth));
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

function appendArray(e, p, y) {
    if (!p && y) e.append(y, "");
    else if ("object" == typeof p)
        for (key in p) "object" == typeof p[key] ? appendArray(e, p[key], y + "[" + key + "]") : e.append(y + "[" + key + "]", p[key]);
    else e.append(y, p);
    return e
}
$.fn.serializeObject = function() {
    var a = {};
    var e, t, n = (e = this, t = [], $.each(e.serializeArray(), function(e, a) {
        if (a.name.indexOf("[]") < 0) return t.push(a), !0;
        var i = a.name.split("[]")[0],
            r = !1;
        $.each(t, function(e, n) {
            n.name === i && (r = !0, t[e].value.push(a.value))
        }), r || t.push({
            name: i,
            value: [a.value]
        })
    }), t);
    return $.each(n, function() {
        var e = this.value,
            n = function e(n, a) {
                if (n.length < 1) return a;
                var i = n[0];
                "]" == i.slice(-1) && (i = i.slice(0, -1));
                var r = {};
                if (1 == n.length) r[i] = a;
                else {
                    n.shift();
                    var t = e(n, a);
                    r[i] = t
                }
                return r
            }(this.name.split("["), e);
        $.extend(!0, a, n)
    }), a
};

const isEqual = (a, b,log) => {
    if (typeof(log)=='undefined'){
        log=true;
    }
    if (a === b) return true;
    if (a instanceof Date && b instanceof Date) {
        if (log) console.log(a.getTime(),b.getTime(),'time');
        return a.getTime() === b.getTime();
    }
    if (!a || !b || (typeof a !== 'object' && typeof b !== 'object')){
        if (log) console.log(a,b,a===b);
        return a === b;
    } 
    if (a === null || a === undefined || b === null || b === undefined){
        if (log) console.log(a,b,'null');
        return false;
    }
    if (a.prototype !== b.prototype){
        if (log) console.log(a.prototype,b.prototype,'prototype');
        return false;
    } 
    let keys = Object.keys(a);
    if (keys.length !== Object.keys(b).length){
        if (log) console.log(a,b,'keys');
        return false;
    } 
    return keys.every(k => isEqual(a[k], b[k],log));
  };