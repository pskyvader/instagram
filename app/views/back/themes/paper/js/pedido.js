function inicio_pedido() {
    $('.grupo_pedido').each(function() {
        inicio_direcciones_pedido($(this));
        inicio_usuarios_pedido($(this).parents('form'));
    });
    inicio_sorted_pedido();
    inicio_select_productos();
    inicio_select_atributos();
}

function inicio_select_productos() {
    var options = {
        width: '100%',
        templateResult: formato_imagen,
        templateSelection: formato_imagen,
    };
    if (is_mobile) {
        options.minimumResultsForSearch = Infinity;
    }

    $('.lista_productos').select2(options);
}


function inicio_select_atributos() {
    var options = {
        width: '100%',
        templateResult: formato_imagen,
        templateSelection: formato_imagen,
    };
    if (is_mobile) {
        options.minimumResultsForSearch = Infinity;
    }
    $('.producto_atributo').select2(options);
}

function formato_imagen(e) {
    if (!$(e.element).data('foto')) {
        return e.text;
    }
    var i = $('<span><img src="' + $(e.element).data('foto') + '"> ' + e.text + '</span><span>');
    return i;
};


var new_line_direcciones = null;

function inicio_usuarios_pedido(e) {
    var usuarios = $('select[name=idusuario]', e);
    var nombre = $('#nombre', e);
    var email = $('#email', e);
    var telefono = $('#telefono', e);
    var add_direccion = $('.add_direccion', e);
    var min = 0;
    if ($('option', usuarios).length > 30) {
        min = 1;
        if ($('option', usuarios).length > 100) {
            min = 3;
        }
    }
    var options = {
        width: '100%',
        minimumInputLength: min,
    };
    if (is_mobile) {
        options.minimumResultsForSearch = Infinity;
    }
    usuarios.select2(options);
    $(email).prop('disabled', true);
    if (usuarios.length > 0) {
        $(nombre).prop('disabled', true);
        $(telefono).prop('disabled', true);
        $(add_direccion).prop('disabled', true);
    }
    $(usuarios).on('change', function() {
        var idusuario = usuarios.val();
        if (idusuario != null) {
            post_basic(create_url(modulo, 'get_usuario'), {
                idusuario: idusuario
            }, "Recuperando informacion del usuario", function(data) {
                if (typeof(data)!='object'){
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
                    if (data.direcciones.length > 0) {
                        $(nombre).val(data.usuario.nombre);
                        $(email).val(data.usuario.email);
                        $(telefono).val(data.usuario.telefono);

                        var direcciones = $('.direccion_entrega', new_line_direcciones);
                        $(data.direcciones).each(function(k, v) {
                            var d = $('<option value="' + v[0] + '" data-precio="' + v.precio + '">' + v.titulo + ' (' + v.direccion + ')</option>');
                            direcciones.append(d);
                        });
                        notificacion_footer(false);
                    } else {
                        notificacion('Oh no!', 'El usuario no tiene direcciones asignadas', 'error', {
                            button: "Crear direccion?",
                            function() {
                                var url = create_url('usuariodireccion', 'detail', {
                                    idusuario: idusuario,
                                    tipo: 1
                                });
                                go_url(url);
                            }
                        });
                    }
                } else {
                    notificacion('Oh no!', data.mensaje, 'error');
                }
                $(nombre).prop('disabled', false);
                $(email).prop('disabled', false);
                $(telefono).prop('disabled', false);
                $(add_direccion).prop('disabled', false);
            });
        }
    });
}

function inicio_direcciones_pedido(e) {
    var boton = $('button.add_direccion', e);
    var contenedor = $('.direcciones_pedido', e);
    var id = [];
    var id_actual = 0;
    var id_producto = [];
    var id_producto_actual = 0;

    var new_row = $('.new_row', e).clone();
    $('.new_row', e).remove();
    new_line_direcciones = $('.new_line', e).clone();
    $('.new_line', e).remove();

    $('.datos_producto', contenedor).each(function() {
        var idp = $('.idproductopedido', this).val();
        id_producto[idp] = idp;
    });
    $('.direccion', contenedor).each(function() {
        var idd = $('.iddireccionpedido', this).val();
        id[idd] = idd;
    });


    $(boton).on('click', function() {
        do {
            id_actual++;
        } while (typeof(id[id_actual]) != 'undefined');
        id[id_actual] = id_actual;

        var new_l = new_line_direcciones.clone();
        var direccion = $('.direccion_entrega', new_l);
        direccion.prop('required', true);
        direccion.prop('name', direccion.prop('name').replace("[]", "[" + id_actual + "]"));

        var fecha = $('.fecha_entrega', new_l);
        fecha.prop('required', true);
        fecha.prop('name', fecha.prop('name').replace("[]", "[" + id_actual + "]"));

        var iddireccion = $('.iddireccionpedido', new_l);
        iddireccion.prop('name', iddireccion.prop('name').replace("[]", "[" + id_actual + "]")).val(id_actual);


        var cantidad_productos = $('.cantidad_productos', new_l);
        cantidad_productos.prop('name', cantidad_productos.prop('name').replace("[]", "[" + id_actual + "]"));



        contenedor.append(new_l);

        $(".date").datetimepicker({
            todayHighlight: true
        });
        inicio_select_productos();

        count_direcciones(e);
        total_productos(e);
        inicio_sorted_pedido();
        return false;
    });


    $(contenedor).on('click', '.add_producto', function() {
        var cantidad = $('.cantidad_producto', $(this).parents('.add')).val();
        var producto = $('.lista_productos', $(this).parents('.add')).select2('data');
        var direccion = $(this).parents('.direccion');
        var exito = true;
        for (let index = 0; index < cantidad; index++) {
            exito = add_producto(producto, 1, new_row.clone(), id_producto, id_producto_actual, direccion);
            if (!exito) {
                break;
            }
        }

        inicio_select_productos();

        // add_producto(producto, cantidad, new_r,id_producto,id_producto_actual);
        count_productos(direccion);
        return false;
    });
    $(contenedor).on('change', '.direccion_entrega', function() {
        var direccion = $(this).parents('.datos_direccion');
        $('.direccion_precio', direccion).val($('option:selected', this).data('precio'));
        total_productos(e);
    });
}

function add_producto(producto, cantidad, new_r, id_producto, id_producto_actual, direccion) {
    var stock = $(producto[0].element).data('stock') - cantidad;
    var idpro = $(producto[0].element).val();
    if (stock < 0) {
        notificacion('Oh no!', 'Producto ' + $(producto[0].element).text() + ' agotado', 'error');
        return false;
    } else {
        $('.lista_productos option[value=' + idpro + ']').data('stock', stock);
        $('.lista_productos option[value=' + idpro + ']', new_line_direcciones)[0].dataset.stock = stock;
    }

    do {
        id_producto_actual++;
    } while (typeof(id_producto[id_producto_actual]) != 'undefined');
    id_producto[id_producto_actual] = id_producto_actual;

    var iddireccionpedido = $('.iddireccionpedido', direccion).val();

    $('.titulo', new_r).text($(producto[0].element).text());
    $('.imagen', new_r).prop('src', $(producto[0].element).data('foto'));
    $('.precio_unitario', new_r).val($(producto[0].element).data('precio'));
    $('.precio', new_r).val($(producto[0].element).data('precio') * cantidad);

    var idproducto = $('.idproducto', new_r);
    idproducto.prop('name', idproducto.prop('name').replace("[]", "[" + iddireccionpedido + "]"));
    idproducto.prop('name', idproducto.prop('name').replace("[]", "[" + id_producto_actual + "]"));
    idproducto.val(idpro);


    var idproductopedido = $('.idproductopedido', new_r);
    idproductopedido.prop('name', idproductopedido.prop('name').replace("[]", "[" + iddireccionpedido + "]"));
    idproductopedido.prop('name', idproductopedido.prop('name').replace("[]", "[" + id_producto_actual + "]"));
    idproductopedido.val(id_producto_actual);

    var producto_cantidad = $('.producto_cantidad', new_r);
    producto_cantidad.prop('name', producto_cantidad.prop('name').replace("[]", "[" + iddireccionpedido + "]"));
    producto_cantidad.prop('name', producto_cantidad.prop('name').replace("[]", "[" + id_producto_actual + "]"));
    producto_cantidad.val(cantidad);

    var producto_mensaje = $('.producto_mensaje', new_r);
    producto_mensaje.prop('name', producto_mensaje.prop('name').replace("[]", "[" + iddireccionpedido + "]"));
    producto_mensaje.prop('name', producto_mensaje.prop('name').replace("[]", "[" + id_producto_actual + "]"));

    var producto_atributo = $('.producto_atributo', new_r);
    producto_atributo.prop('name', producto_atributo.prop('name').replace("[]", "[" + iddireccionpedido + "]"));
    producto_atributo.prop('name', producto_atributo.prop('name').replace("[]", "[" + id_producto_actual + "]"));
    producto_atributo.prop('required', true);


    $('.lista_productos_pedido', direccion).append(new_r);

    $('textarea.autosize').autosize({
        append: "\n"
    });
    inicio_select_atributos();

    total_productos($('.grupo_pedido'));
    inicio_sorted_pedido();
    return true;
}

$('body').on('change', '.lista_productos', function() {
    $('.add_producto', $(this).parent().parent()).removeClass('disabled');
});

$('body').on('change', '.producto_cantidad', function() {
    var cantidad = $(this).val();
    var precio = $('.precio_unitario', $(this).parents('.producto')).val();
    $('.precio', $(this).parents('.producto')).val(precio * cantidad);
    total_productos($('.grupo_pedido'));
});

$('body').on('click', '.quitar_producto', function() {
    var direccion = $(this).parents('.direccion');
    var producto = $(this).parents('.datos_producto');
    var idproducto = $('.idproducto', producto).val();
    var cantidad = parseInt($('.producto_cantidad', producto).val());
    var stock = parseInt($('.lista_productos option[value=' + idproducto + ']', new_line_direcciones)[0].dataset.stock);
    producto.remove();
    $('.lista_productos option[value=' + idproducto + ']').data('stock', stock + cantidad);
    $('.lista_productos option[value=' + idproducto + ']', new_line_direcciones)[0].dataset.stock = stock + cantidad;
    count_productos(direccion);
    total_productos($('.grupo_pedido'));
});

$('body').on('click', '.quitar_direccion', function() {
    var direccion = $(this).parents('.linea');
    $('.quitar_producto', direccion).each(function() {
        $(this).click();
    });
    direccion.remove();
    count_direcciones($('.grupo_pedido'));
    total_productos($('.grupo_pedido'));
    inicio_sorted_pedido();
});


function total_productos(e) {
    var total = 0;
    var direcciones = $('.direcciones_pedido .direccion', e);
    $(direcciones).each(function() {
        var total_direccion = parseInt($('.direccion_precio', this).val());
        if (total_direccion && total_direccion != '') {
            total += total_direccion;
        }
        $('.lista_productos_pedido .datos_producto', this).each(function() {
            var cantidad = parseInt($('.producto_cantidad', this).val());
            var precio = parseInt($('.precio_unitario', this).val());
            total += (cantidad * precio);
        });
    });
    $('#total').val(total);
}

function count_direcciones(e) {
    setTimeout(function() {
        var n = $('.direcciones_pedido .campo', e).length;
        if (n > 0) {
            $('.name', e).val(n);
        } else {
            $('.name', e).val('');
        }
    }, 100);
}

function count_productos(e) {
    setTimeout(function() {
        var n = $('.lista_productos_pedido .datos_producto', e).length;
        if (n > 0) {
            $('.cantidad_productos', e).val(n);
        } else {
            $('.cantidad_productos', e).val('');
        }
    }, 100);
}


function inicio_sorted_pedido() {
    var idinicial = 0;
    var idfinal = 0;
    
    $(".grupo_pedido .lista_productos_pedido").sortable({
        connectWith: ".lista_productos_pedido",
        cursor: "move",
        axis:"y",
        placeholder: "placeholder_producto",
        tolerance: "pointer",
        forcePlaceholderSize :true,
        handle: '.handle',
        revert: true,
        scrollSensitivity: 120,
        scrollSpeed: 15,
        start: function(event, ui) {
            $('.producto').hide();
        },
        stop: function(event, ui) {
          $('.producto').show();
            mover(ui.item, 200, 0);
        },
        receive: function(event, ui) {
            var direccion = $(ui.sender).parents('.direccion');
            idinicial = $('.iddireccionpedido', direccion).val();
            var direccion = $(ui.item).parents('.direccion');
            idfinal = $('.iddireccionpedido', direccion).val();
            cambiar_id_productopedido(ui.item, idinicial, idfinal);
            count_productos(direccion);
        }
    });
}

function cambiar_id_productopedido(e, idinicial, idfinal) {
    $('.idproducto', e).prop('name', $('.idproducto', e).prop('name').replace("datos_direcciones[" + idinicial + "]", "datos_direcciones[" + idfinal + "]"));
    $('.idproductopedido', e).prop('name', $('.idproductopedido', e).prop('name').replace("datos_direcciones[" + idinicial + "]", "datos_direcciones[" + idfinal + "]"));
    $('.producto_cantidad', e).prop('name', $('.producto_cantidad', e).prop('name').replace("datos_direcciones[" + idinicial + "]", "datos_direcciones[" + idfinal + "]"));
    $('.producto_mensaje', e).prop('name', $('.producto_mensaje', e).prop('name').replace("datos_direcciones[" + idinicial + "]", "datos_direcciones[" + idfinal + "]"));
    $('.producto_atributo', e).prop('name', $('.producto_atributo', e).prop('name').replace("datos_direcciones[" + idinicial + "]", "datos_direcciones[" + idfinal + "]"));
}