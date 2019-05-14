function update_orden(b) {
    var a = 999999;
    $(b[0]).each(function(b, c) {
        c.order < a && (a = c.order);
        if (1 == a) return !1;
    });
    var e = [];
    $(b[0]).each(function(b, c) {
        var d = c.id;
        "undefined" != typeof d && (e.push({
            id: d,
            orden: a
        }), $(".sorted_table > tbody tr[data-id=" + d + "]").data("order", a).find("td[data-field=orden]").text(a), a++);
    });
    post(create_url(modulo, 'orden'), {
        elementos: e
    }, "Actualizando Orden", !1);
}

function post_basic(url_post, info, mensaje_inicial, callback) {
    if (mensaje_inicial) notificacion_footer(mensaje_inicial);
    $.post(url_post, info, function(data) {
        if (callback) callback(data);
    }).fail(function(jqXHR, textStatus, errorThrown) {
        console.log(textStatus);
        console.log(jqXHR);
        console.log(errorThrown);
        notificacion('Oh no!', 'Ha ocurrido un error, por favor intenta más tarde', 'error');
        if (callback) callback(textStatus);
    });
}


var xhr = null;

function post(url_post, info, mensaje_inicial, importante, archivo, callback, extra) {
    barra(10);
    if (typeof(archivo) == 'undefined') {
        archivo = null;
    }
    if (typeof(importante) == 'undefined') {
        importante = true;
    }
    if (typeof(callback) == 'undefined') {
        callback = null;
    }
    var data = new FormData();
    appendArray(data, info, 'campos');
    if (archivo != null) {
        $.each(archivo, function(key, value) {
            data.append(key, value);
        });
        //process=false
        //type=false
        
        process=true
        type='application/x-www-form-urlencoded; charset=UTF-8'
    }else{
        process=true
        type='application/x-www-form-urlencoded; charset=UTF-8'
        data={'campos':info}
    }
    
    $.ajax({
        url: url_post,
        type: 'POST',
        data: data,
        cache: false,
        dataType: 'json',
        processData: process, // Dont process the files
        contentType: type, // Set content type to false as jQuery will tell the server its a query string request
        beforeSend: function() {
            notificacion_footer(mensaje_inicial);
        },
        xhr: function() {
            xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener("progress", function(evt) { //Barra de progreso de subida y ejecución
                if (evt.lengthComputable) {
                    var percentComplete = (evt.loaded / evt.total) * 50;
                    barra(percentComplete);
                } else {
                    barra(25);
                }
            }, false);
            xhr.addEventListener("progress", function(evt) {
                if (evt.lengthComputable) {
                    var percentComplete = 50 + (evt.loaded / evt.total) * 50;
                    barra(percentComplete);
                } else {
                    barra(75);
                }
            }, false);
            return xhr;
        },
        success: function(datos, textStatus, jqXHR) {
            if (typeof(datos['exito']) != 'undefined' && datos['exito']) {
                if (importante) {
                    var mensaje = (($.isArray(datos['mensaje'])) ? datos['mensaje'].join('<br/>') : datos['mensaje']);
                    notificacion('Confirmación', mensaje, 'success');
                }
                if (callback != null) {
                    callback(datos, extra);
                }
                if (typeof(datos['refresh']) != 'undefined' && datos['refresh']) {
                    go_url(url);
                }
            } else {
                var mensaje = (($.isArray(datos['mensaje'])) ? datos['mensaje'].join('<br/>') : datos['mensaje']);
                notificacion('Oh no!', mensaje, 'error');
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            if (errorThrown != "") {
                console.log(textStatus);
                console.log(jqXHR);
                console.log(errorThrown);
                notificacion('Oh no!', 'Ha ocurrido un error, por favor intenta más tarde', 'error');
            }
        },
        complete: function() {
            xhr = null;
            barra(100);
            habilitar(true);
            notificacion_footer(false);
        }
    });
}