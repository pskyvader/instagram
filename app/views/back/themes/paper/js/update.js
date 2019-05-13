var update_finalizado = false;

function get_update() {
    $.get(create_url(modulo, 'get_update')).done(function(data) {
        if (typeof(data) != 'object') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                data = {
                    mensaje: data,
                    exito: false
                };
            }
        }
        if (data.version) {
            var mensaje = "Version " + data.version.version + "<br/>" + data.version.descripcion;
            $(update_content).html(mensaje);
            $('input[name=id_update]').val(data.version.version);
            $('.panel-body').show();
        } else {
            notificacion('Oh no!', data.mensaje, 'error');
        }
    });
}

function iniciar_update() {
    post_basic(create_url(modulo, 'vaciar_log'), {}, 'Iniciando', function(data) {
        update_elemento();
    });
}

function update_elemento() {
    var archivo = $('input[name=id_update]').val();
    if (archivo == "") {
        notificacion('Oh no!', 'Ha ocurrido un error, por favor actualiza la pagina e intentalo nuevamente', 'error');
    } else {
        habilitar(false);
        update_content.empty();
        update_finalizado = false;
        $('#progreso_sitemap').val(15).trigger('change');
        barra(15);
        update_content.prepend($('<p>' + 'Descargando archivo ' + archivo + '</p>'));
        post_basic(create_url(modulo, 'get_file'), {
            file: archivo
        }, 'Descargando archivo ' + archivo, archivo_listo);

        setTimeout(function() {
            if (!update_finalizado) {
                notificacion('Advertencia', 'La restauracion puede tomar un tiempo <br/> <b>No cierres esta ventana<b/>', 'danger');
            }
        }, 3000);
    }
}

function archivo_listo(data) {
    if (typeof(data) != 'object') {
        try {
            data = JSON.parse(data);
        } catch (e) {
            data = {
                mensaje: data,
                exito: false
            };
        }
    }
    if (data.exito) {
        var archivo = $('input[name=id_update]').val();
        $('#progreso_sitemap').val(30).trigger('change');
        barra(30);
        update_content.prepend($('<p>' + 'Actualizando Version ' + archivo + '</p>'));
        post_basic(create_url(modulo, 'update_file'), {
            file: archivo
        }, 'Actualizando Version ' + archivo, fin_update);

        leer_log_update();
        setTimeout(function() {
            if (!update_finalizado) {
                notificacion('Advertencia', 'La restauracion puede tomar un tiempo <br/> <b>No cierres esta ventana<b/>', 'danger');
            }
        }, 3000);
    } else {
        notificacion('Oh no!', 'Ha ocurrido un error, por favor actualiza la pagina e intentalo nuevamente'+data.mensaje, 'error');
    }
}



function leer_log_update() {
    if (!update_finalizado) {
        $.ajax({
            cache: false,
            url: path + 'log.json',
            success: function(data) {
                //console.log('leer', data);
                //end();
                if (typeof(data) == 'object') {
                    if (data.mensaje) {
                        update_content.prepend($('<p>' + data.mensaje + '</p>'));
                        notificacion_footer(data.mensaje);
                    }
                    if (data.porcentaje) {
                        barra(data.porcentaje);
                        $('#progreso_sitemap').val(data.porcentaje).trigger('change');
                        if (data.porcentaje == 100) {
                            data.exito = true;
                            data = JSON.stringify(data);
                            fin_update(data);
                        }
                    }
                    setTimeout(leer_log_update, 500);
                } else {
                    setTimeout(leer_log_update, 500);
                }
            },
            error: function() {
                setTimeout(leer_log_update, 1000);
            },
            timeout: 500 //in milliseconds
        });
    }
}



function fin_update(data) {
    //console.log(data);
    if (!update_finalizado) {
        if (typeof(data) != 'object') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                data = {
                    mensaje: data,
                    exito: false
                };
            }
        }
        if (data.exito) {
            if (data.inicio) {
                var archivo = $('input[name=id_update]').val();
                post_basic(create_url(modulo, 'update_file'), {
                    file: archivo,
                    inicio: data.inicio
                }, '', fin_update);
            } else {
                habilitar(true);
                update_finalizado = true;
                notificacion('Confirmacion', 'Actualizacion completada', 'success');
                barra(100);
                $('#progreso_sitemap').val(100).trigger('change');
                go_url(url);
            }
        } else {
            habilitar(true);
            update_finalizado = true;
            var mensaje = (($.isArray(data['mensaje'])) ? data['mensaje'].join('<br/>') : data['mensaje']);
            notificacion('Oh no!', mensaje, 'error');
            barra(0);
            $('#progreso_sitemap').val(0).trigger('change');
        }
    }
}