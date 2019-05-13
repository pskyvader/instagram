var template_cart = null;
var modulo_carro = "carro/";

function inicio_cart() {
    if (template_cart == null) {
        var tc = $('#template_cart-item');
        template_cart = $('li', tc);
        tc.remove();
    }
    var modulo = modulo_carro;
    var url = create_url(modulo + "current_cart", {}, path);
    post_basic(url, "", function(data) {
        if (typeof(data) != 'object') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                console.log(e, data);
                data = {};
            }
        }
        generar_cart(data);
    });
}


function generar_cart(data) {
    var elementos = [];
    var cantidad = 0;
    var total_productos = "$0";
    var total_envio = "Por definir";
    var total = "$0";
    if (typeof(data) == 'object' && Object.keys(data).length > 0) {
        total_productos = data.subtotal;
        total_envio = data.total_direcciones;
        total = data.total;
        if (data.productos && Object.keys(data.productos).length > 0) {
            $(data.productos).each(function(k, v) {
                cantidad += parseInt(v.cantidad);
                var e = template_cart.clone();

                e.html(
                    e.html().replace(/{url_producto}/ig, v.url)
                    .replace(/{imagen_producto}/ig, v.foto)
                    .replace(/{titulo_producto}/ig, v.titulo)
                    .replace(/{precio_producto}/ig, v.precio)
                    .replace(/{cantidad_producto}/ig, v.cantidad)
                    .replace(/{id}/ig, v.idpedidoproducto)
                    .replace('data-src', 'src')
                    .replace('data-href', 'href')
                );
                elementos.push(e);
            });
        } else {
            elementos = $('<li><div class="media">Carro vacío</div></li>');
        }
    } else {
        elementos = $('<li><div class="media">Carro vacío</div></li>');
    }
    $('#carro-header .carro-cantidad').text(cantidad);
    $('#carro-header .carro-total-productos').text(total_productos);
    $('#carro-header .carro-envio').text(total_envio);
    $('#carro-header .carro-total').text(total);

    $('#carro-header .carro-productos .lista-productos').empty().prepend(elementos);
}

function add_wish(id) {
    console.log(id);
}

function add_cart(id, cantidad) {
    if (!cantidad) cantidad = 1;
    cantidad = parseInt(cantidad);
    if (cantidad < 1) cantidad = 1;

    var modulo = modulo_carro;
    var url = create_url(modulo + "add_cart", {}, path);
    post_basic(url, {
        id: id,
        cantidad: cantidad
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
            if (logueado) {
                notificacion(data.mensaje, 'success', create_url('pedido/step/1', {}, path));
            } else {
                notificacion(data.mensaje, 'success', create_url('cuenta/registro', {
                    next_url: 'pedido/step/1'
                }, path));
            }
        } else {
            notificacion(data.mensaje, 'error');
        }
        generar_cart(data.carro);
        /*mover('#carro-header .dropdown-toggle', 200);
        setTimeout(function() {
            $('#carro-header .dropdown-toggle').click();
        }, 200);*/
    });
}



function remove_cart(id, e) {
    var modulo = modulo_carro;
    var url = create_url(modulo + "remove_cart", {}, path);
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
                e.parents('.producto').remove();
                $('[data-toggle="tooltip"]').tooltip();
                var total = 0;
                $('.order .producto .card-price').each(function() {
                    total += parseInt($(this).text().substring(1).replace(".", ""));
                });
                if (total == 0) {
                    var mensaje = $('<div class="alert alert-danger" role="alert"> Tu carro está vacío. Por favor agrega productos para continuar tu compra </div>');
                    $('.order .content').html(mensaje);
                }
                $('.precio_subtotal').text(formato_precio(total, 0));
                var envio = parseInt($('.precio_envio').text().substring(1).replace(".", ""));
                if (isNaN(envio)) {
                    envio = 0;
                }
                $('.precio_total').text(formato_precio(total + envio, 0));
            }
        } else {
            notificacion(data.mensaje, 'error');
        }
        generar_cart(data.carro);

    });
}