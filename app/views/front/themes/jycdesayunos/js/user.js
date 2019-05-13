function inicio_user(){
    if($('.user-pedidos-detalle .content').length>0){
        mover('.user-pedidos-detalle .content', 400, 500);
    }
}
var logueado=false;
function inicio_login() {
    var modulo = "cuenta/";
    var url = create_url(modulo + "verificar", null, path);
    post_basic(url, "", function(data) {
        if (typeof(data) != 'object') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                console.log(e, data);
                data = {};
            }
        }
        
        var b=$('<span> / </span>');
        if (data.exito) {
            logueado=true;
            var a = $('<a href="' + path + modulo + 'datos">Bienvenido ' + data.mensaje + '</a>');
            var c = $('<button class="logout">Salir</button>');
            $('#carro-header .accion').text('Comprar').prop('href', path + 'pedido/step/1');
            $('#carro-header .accion-2').hide();
        } else {
            logueado=false;
            var a = $('<a href="' + create_url(modulo + 'login', null, path) + '">Login</a>');
            var c = $('<a href="' + create_url(modulo + 'registro', null, path) + '">Registro</a>');

            $('#carro-header .accion').text('Ingresa').prop('href', create_url(modulo + 'login', {
                next_url: 'pedido/step/1'
            }, path));
            $('#carro-header .accion-2').text('Registrate').prop('href', create_url(modulo + 'registro', {
                next_url: 'pedido/step/1'
            }, path)).show();
        }
        $('.cuenta-header').empty().append(a).append(b).append(c);
        inicio_cart();
    });
}


$(document).on('submit', 'form.update-datos', function() {
    var modulo = "cuenta/";
    var url = create_url(modulo + "datos_process", null, path);
    var data = $(this).serializeObject();
    post(url, data, "Modificando datos", null, function(datos) {
        if (datos.exito) {
            if (datos.redirect) {
                var url = create_url(modulo + "logout", null, path);
                post(url, {}, "", null, function() {
                    inicio_login();
                    var url = create_url(modulo + "login", null, path);
                    go_url(url);
                });
            }
        }
    });
    return false;
});

$(document).on('submit', 'form.registro', function() {
    var modulo = "cuenta/";
    var extra = createObjFromURI();
    if (extra.next_url) {
        extra = {
            next_url: extra.next_url
        };
    } else {
        extra = {};
    }
    var url = create_url(modulo + "registro_process", {}, path);
    var data = $(this).serializeObject();
    post(url, data, "Enviando datos de registro", null, function(datos) {
        if (datos.exito) {
            var url = create_url(modulo + "direccion", extra, path);
            inicio_login();
            go_url(url);
        }
    });
    return false;
});
$(document).on('submit', 'form.login', function() {
    var modulo = "cuenta/";
    var extra = createObjFromURI();
    if (extra.next_url) {
        extra = {
            next_url: extra.next_url
        };
    } else {
        extra = {};
    }
    var url = create_url(modulo + "login_process", extra, path);
    var data = $(this).serializeObject();
    post(url, data, "Enviando datos de login", null, function(datos) {
        if (datos.exito) {
            if (datos.next_url) {
                var url = create_url(datos.next_url, {}, path);
            } else {
                var url = create_url(modulo + "datos", {}, path);
            }
            inicio_login();
            go_url(url);
        }
    });
    return false;
});
$(document).on('submit', 'form.recuperar', function() {
    var modulo = "cuenta/";
    var url = create_url(modulo + "recuperar_process", {}, path);
    var data = $(this).serializeObject();
    post(url, data, "Recuperando tu contraseña");
    return false;
});
$(document).on('submit', 'form.direccion', function() {
    var modulo = "cuenta/";
    var extra = createObjFromURI();
    if (extra.next_url) {
        extra = {
            next_url: extra.next_url
        };
    } else {
        extra = {};
    }
    var url = create_url(modulo + "direccion_process", extra, path);
    var data = $(this).serializeObject();
    post(url, data, "Guardando tu direccion", null, function(datos) {
        if (datos.exito) {
            if (datos.next_url) {
                var url = create_url(datos.next_url, {}, path);
            } else {
                var url = create_url(modulo + "direcciones", {}, path);
            }
            go_url(url);
        }
    });
    return false;
});

$(document).on('click', '.cuenta-header .logout', function() {
    var modulo = "cuenta/";
    var url = create_url(modulo + "logout", {}, path);
    post(url, {}, "", null, function() {
        inicio_login();
    });
});