var is_online = true;
var habilitado_online = true;
var tiempo = 120000;
var tiempo_offline = 2500;
var timer_online = setTimeout(online, tiempo);

function online() {
    // Sólo hacer el fetch si navigator.onLine es true
    if (navigator.onLine) {
        fetch(path + 'ping').then(function(response) {
            if (!response.ok) {
                if (is_online) {
                    tiempo = tiempo_offline;
                }
                is_online = false;
            } else {
                if (!is_online) {
                    is_online = true;
                }
            }
            habilitar_online();
        }).catch(function(error) {
            if (is_online) {
                tiempo = tiempo_offline;
            }
            is_online = false;
            habilitar_online();
        });
    } else {
        if (is_online) {
            tiempo = tiempo_offline;
        }
        is_online = false;
        habilitar_online();
    }
}

function habilitar_online() {
    if (is_online) {
        tiempo = 120000;
        if (!habilitado_online) {
            habilitar(is_online);
            habilitado_online = true;
            notificacion('Conectado', 'Conexión activa', 'success');
        }
    } else {
        tiempo = tiempo * 2;
        if (tiempo > 120000) tiempo = 120000;
        habilitado_online = false;
        habilitar(is_online);
        notificacion('Sin Conexion', 'No tienes conexion, verificando conexion en ' + (tiempo / 1000) + ' segundos', 'error', {
            button: 'Reintentar',
            function() {
                clearTimeout(timer_online);
                tiempo = tiempo_offline;
                online();
            }
        });
    }
    timer_online = setTimeout(online, tiempo);
}