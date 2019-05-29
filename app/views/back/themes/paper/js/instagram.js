instagram_finalizado=false;
$('body').on('click', 'button.accion_instagram', function() {
    var accion = $(this).data('action');
    var id = $(this).data('id');
    var mensaje = $(this).data('mensaje');
    accion_instagram(accion,id,mensaje);
});

function accion_instagram(accion,id,mensaje){
    websocket_start();
    if(websocket == null){
        leer_log_instagram();
    }
    post(create_url(modulo, accion), {
        id: id
    }, mensaje, false, null, fin_instagram);
}




function fin_instagram(data) {
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
    
    if (data.exito){
        if(data.mensaje){
            notificacion('Completado', data.mensaje, 'success');
        }
        if (data.porcentaje) {
            barra(data.porcentaje);
            if ($('#progreso_instagram').length > 0) {
                $('#progreso_instagram').val(data.porcentaje).trigger('change');
            }
        }
    }
    setTimeout(websocket_stop, 1000);
    instagram_finalizado=true;
}


function leer_log_instagram() {
    if (!instagram_finalizado) {
        $.ajax({
            cache: false,
            url: path + 'log.json',
            success: function(data) {
                //console.log('leer', data);
                //end();
                if (typeof(data) == 'object') {
                    if (data.mensaje) {
                        notificacion_footer(data.mensaje);
                    }
                    if (data.porcentaje) {
                        barra(data.porcentaje);
                        $('#progreso_instagram').val(data.porcentaje).trigger('change');
                        if (data.porcentaje == 100) {
                            data.exito = true;
                            fin_instagram();
                        }
                    }
                } else {
                    //console.log(data)
                    setTimeout(leer_log_instagram, 500);
                }
            },
            error: function() {
                setTimeout(leer_log_instagram, 1000);
            },
            timeout: 500 //in milliseconds
        });
    }
}