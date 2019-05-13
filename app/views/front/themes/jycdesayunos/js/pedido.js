var modulo_pedido = "pedido/";

function inicio_pedido() {
    mover('.order', 300, 500);
    if ($('.producto_atributo').length > 0) {
        inicio_pedido_atributos();
    }
    if ($('.mensaje_pedido').length > 0) {
        inicio_pedido_mensaje();
    }
    if ($('.direccion_entrega').length > 0) {
        inicio_direccion_entrega();
    }
    pedido_proceso = false;
    pedido_exito = true;
}


$('body').on('click', '.order.step-1 #next_step', function(e) {
    if (pedido_proceso) {
        setTimeout(function() {
            $(this).trigger("click");
        }, 200);
        return false;
    } else if (!pedido_exito) {
        return false;
    }
    var error = false;
    $('.order .producto_atributo').each(function() {
        if ($(this).val() == null) {
            notificacion("Debes elegir un globo", 'error');
            mover($(this).parents('.producto')[0]);
            error = true;
            return false;
        }
    });
    if (error) {
        return false;
    } else {
        inicio_cart();
        go_url($(this).data('href'), {});
        mover('.order', 0, 500);
    }
});

var pedido_proceso = false;
var pedido_exito = true;


$('body').on('click', '.order.step-2 #next_step', function(e) {
    var error = false;
    $('.direccion').each(function() {
        if ($('.lista_productos_pedido .producto', this).length < 1) {
            error = true;
            notificacion("Debes agregar al menos 1 producto por direccion, o eliminar las direcciones vacias", 'error');
            mover(this);
            return false;
        } else if ($('.fecha_entrega', this).val() == '') {
            error = true;
            $('.fecha_entrega', this).addClass('is-invalid');
            notificacion("Debes seleccionar una fecha de envio", 'error');
            mover(this);
            return false;
        } else if ($('.hora_entrega option:selected', this).val() == '') {
            error = true;
            $('.hora_entrega', this).addClass('is-invalid');
            notificacion("Debes seleccionar una hora de envio", 'error');
            mover(this);
            return false;
        }
    });
    if (error) {
        return false;
    } else {
        inicio_cart();
        go_url($(this).data('href'), {});
        mover('.order', 0, 500);
    }
});


$('body').on('click', '.order.step-3 #next_step', function(e) {
    var modulo = modulo_pedido;
    var url = create_url(modulo + "crear_pedido", {}, path);
    notificacion("Creando tu pedido, por favor espera", 'warning');
    $('#next_step').addClass('disabled');

    post_basic(url, {}, function(data) {
        $('#next_step').removeClass('disabled');
        if (typeof(data) != 'object') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                console.log(e, data);
                data = {};
            }
        }

        if (data.exito) {
            inicio_cart();
            notificacion("Tu pedido esta listo para pagar", 'success');
            go_url(data.url);
        }

        if (!data.exito) {
            notificacion(data.mensaje, 'error');
        }
    });

    return false;
});


function inicio_pedido_atributos() {
    var options = {
        width: '100%',
        templateResult: formato_imagen,
        templateSelection: formato_imagen,
        placeholder: "Selecciona un Globo para tu desayuno",
    };
    if (is_mobile) {
        options.minimumResultsForSearch = Infinity;
    }
    $('.producto_atributo').select2(options).on('change', function() {
        var t = $(this);
        var idproductoatributo = $(this).val();
        var idpedidoproducto = $($(this).select2('data')[0].element).parent().data('id');

        var modulo = modulo_carro;
        var url = create_url(modulo + "change_atributo", {}, path);
        $('#next_step').addClass('disabled');
        post_basic(url, {
            idproductoatributo: idproductoatributo,
            idpedidoproducto: idpedidoproducto
        }, function(data) {
            $('#next_step').removeClass('disabled');
            if (typeof(data) != 'object') {
                try {
                    data = JSON.parse(data);
                } catch (e) {
                    console.log(e, data);
                    data = {};
                }
            }
            if (!data.exito) {
                notificacion(data.mensaje, 'error');
            }
        });
    });
}

function inicio_pedido_mensaje() {
    $('.mensaje_pedido').on('change', function() {
        var mensaje = $(this).val();
        var idpedidoproducto = $(this).data('id');
        var modulo = modulo_carro;
        var url = create_url(modulo + "change_mensaje", {}, path);
        pedido_proceso = true;
        pedido_exito = false;
        $('#next_step').css('opacity', 0.4);
        post_basic(url, {
            mensaje: mensaje,
            idpedidoproducto: idpedidoproducto
        }, function(data) {
            pedido_proceso = false;
            $('#next_step').css('opacity', 1);
            if (typeof(data) != 'object') {
                try {
                    data = JSON.parse(data);
                } catch (e) {
                    console.log(e, data);
                    data = {};
                }
            }

            pedido_exito = data.exito;
            if (!data.exito) {
                notificacion(data.mensaje, 'error');
            }
        });
    });
}


function inicio_direccion_entrega() {
    check_quitar();
    $('.direccion_entrega').on('change', function() {
        var idusuariodireccion = $('option:selected', this).val();
        var direccion = $(this).parents('.direccion');
        var idpedidodireccion = direccion.data('id');

        var modulo = modulo_pedido;
        var url = create_url(modulo + "change_direccion", {}, path);
        $('#next_step').addClass('disabled');
        post_basic(url, {
            idusuariodireccion: idusuariodireccion,
            idpedidodireccion: idpedidodireccion
        }, function(data) {
            $('#next_step').removeClass('disabled');
            if (typeof(data) != 'object') {
                try {
                    data = JSON.parse(data);
                } catch (e) {
                    console.log(e, data);
                    data = {};
                }
            }
            if (data.exito) {
                $('.precio', direccion).text(formato_precio(data.precio, 0));
                total_sidebar();
            }
            if (!data.exito) {
                notificacion(data.mensaje, 'error');
            }
        });
    });

    inicio_direccion_datepicker();
    inicio_direccion_sortable();
    new_direccion();
}

function new_direccion() {
    $('#new_grupo').on('click', function() {
        var direccion = $('.direccion:first').clone();
        var modulo = modulo_pedido;
        var url = create_url(modulo + "new_direccion", {}, path);
        post_basic(url, {}, function(data) {
            pedido_proceso = false;
            $('#next_step').removeClass('disabled');
            if (typeof(data) != 'object') {
                try {
                    data = JSON.parse(data);
                } catch (e) {
                    console.log(e, data);
                    data = {};
                }
            }
            if (data.exito) {
                direccion.data('id', data.idpedidodireccion);
                direccion.prop('data-id', data.idpedidodireccion);
                $(direccion)[0].dataset.id = data.idpedidodireccion;
                $('.lista_productos_pedido', direccion).empty();

                $('.direccion_entrega option', direccion).each(function() {
                    $(this).prop('selected', false);
                    if ($(this).val() == data.idusuariodireccion) {
                        $(this).prop('selected', true);
                    }
                });

                $('.fecha_entrega', direccion).val('');
                var k = 0;
                $('.hora_entrega option', direccion).each(function() {
                    $(this).prop('selected', false);
                    if (k == 0) {
                        $(this).prop('selected', true);
                    }
                    k++;
                });
                $('.lista_direcciones').append(direccion);
                inicio_direccion_datepicker();
                inicio_direccion_sortable();
                total_sidebar();

                check_quitar();
                mover(direccion);
            }
            if (!data.exito) {
                notificacion(data.mensaje, 'error');
            }
        });
    });
}

function check_quitar() {
    $('.direccion').each(function() {
        if ($('.lista_productos_pedido .producto', this).length < 1) {
            $('.remove_direccion', this).show();
        } else {
            $('.remove_direccion', this).hide();
        }
    });
}

function total_sidebar() {
    var total = parseInt($('.precio_subtotal').text().substring(1).replace(".", ""));
    if (isNaN(total)) {
        total = 0;
    }

    var envio = 0;
    $('.order .direccion .precio').each(function() {
        envio += parseInt($(this).text().substring(1).replace(".", ""));
    });

    $('.precio_envio').text(formato_precio(envio, 0));
    $('.precio_total').text(formato_precio(total + envio, 0));
}

function inicio_direccion_datepicker() {

    var fechas_bloqueadas = JSON.parse($('#fechas_bloqueadas').val());
    var fechas_especiales = JSON.parse($('#fechas_especiales').val());

    var fecha_inicio = new Date();
    fecha_inicio = fecha_inicio.setDate(fecha_inicio.getDate() + 1);
    var fecha_fin = new Date();
    var fecha_fin = fecha_fin.setMonth(fecha_fin.getMonth() + 2);

    $('.fecha_entrega').datepicker({
        format: "yyyy-mm-dd",
        startDate: formato_fecha(fecha_inicio),
        endDate: formato_fecha(fecha_fin),
        maxViewMode: 0,
        language: "es",
        autoclose: true,
        beforeShowDay: function(date) {
            var ret = true;
            date = formato_fecha(date);
            $(fechas_bloqueadas).each(function(k, v) {
                if (date == v.fecha) {
                    ret = {
                        tooltip: v.texto,
                        enabled: false
                    };
                    return false;
                }
            });
            $(fechas_especiales).each(function(k, v) {
                if (date == v.fecha) {
                    ret = {
                        tooltip: v.texto,
                        classes: "special"
                    };
                    return false;
                }
            });
            return ret;
        }
    });

    $('.fecha_entrega').on('changeDate', function() {
        var direccion = $(this).parents('.direccion');
        var fecha = $(this).datepicker('getFormattedDate');
        var hora = $('.hora_entrega option:selected', direccion).val();
        var idpedidodireccion = $(direccion).data('id');
        $(this).removeClass('is-invalid');
        cambiar_fecha(fecha, hora, idpedidodireccion);
    });

    $('.hora_entrega').on('change', function() {
        var direccion = $(this).parents('.direccion');
        var fecha = $('.fecha_entrega', direccion).datepicker('getFormattedDate');
        var hora = $('option:selected', this).val();
        var idpedidodireccion = $(direccion).data('id');
        $(this).removeClass('is-invalid');
        cambiar_fecha(fecha, hora, idpedidodireccion);
    });
}

function inicio_direccion_sortable() {
    $(".grupo_pedido .lista_productos_pedido").sortable({
        connectWith: ".lista_productos_pedido",
        cursor: "producto",
        tolerance: "pointer",
        axis: "y",
        handle: '.handle',
        revert: true,
        scrollSensitivity: 120,
        scrollSpeed: 15,
        stop: function(event, ui) {
            check_quitar();
            mover(ui.item, 200, 0);
        },
        receive: function(event, ui) {
            var idfinal = $(ui.item).parents('.direccion').data('id');
            cambiar_id_productopedido(ui.item, idfinal);
        }
    });
}


function cambiar_fecha(fecha, hora, idpedidodireccion) {
    var modulo = modulo_pedido;
    var url = create_url(modulo + "change_fecha", {}, path);
    $('#next_step').addClass('disabled');
    post_basic(url, {
        fecha: fecha,
        hora: hora,
        idpedidodireccion: idpedidodireccion,
    }, function(data) {
        pedido_proceso = false;
        $('#next_step').removeClass('disabled');
        if (typeof(data) != 'object') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                console.log(e, data);
                data = {};
            }
        }
        if (!data.exito) {
            notificacion(data.mensaje, 'error');
        }
    });
}




function cambiar_id_productopedido(e, idfinal) {
    var idpedidoproducto = $(e).data('id');
    var modulo = modulo_pedido;
    var url = create_url(modulo + "change_productodireccion", {}, path);
    $('#next_step').addClass('disabled');
    post_basic(url, {
        idpedidoproducto: idpedidoproducto,
        idfinal: idfinal,
    }, function(data) {
        pedido_proceso = false;
        $('#next_step').removeClass('disabled');
        if (typeof(data) != 'object') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                console.log(e, data);
                data = {};
            }
        }
        if (!data.exito) {
            notificacion(data.mensaje, 'error');
        }
    });
}


function remove_direccion(e) {
    var id = $(e).parents('.direccion').data('id');
    var modulo = modulo_pedido;
    var url = create_url(modulo + "remove_direccion", {}, path);
    post_basic(url, {
        id: id
    }, function(data) {
        if (typeof(data) != 'object') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                console.log(e, data);
                data = {};
            }
        }
        if (data.exito) {
            notificacion(data.mensaje, 'success');
            if (e) {
                $('[data-toggle="tooltip"]').tooltip('dispose');
                e.parents('.direccion').remove();
                $('[data-toggle="tooltip"]').tooltip();
                total_sidebar();
            }
        } else {
            notificacion(data.mensaje, 'error');
        }
    });
}


function formato_imagen(e) {
    if (!$(e.element).data('foto')) {
        return e.text;
    }
    return $('<span><img src="' + $(e.element).data('foto') + '"> ' + e.text + '</span><span>');
};