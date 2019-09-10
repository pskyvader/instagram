// var wsUri = "ws://socket.mysitio.cl:8000/ws";
// var wsUri_start = "http://socket.mysitio.cl/";
var wsUri = ("ws://" + window.location.host + "/ws").replace('8080', '8001');
console.log(wsUri);
var intento = 0;
websocket = null;

function websocket_start(callback) {
    if (window.WebSocket !== undefined) {
        if (websocket == null) {
            websocket = new WebSocket(wsUri);
            websocket.onopen = function(evt) {
                onOpen(evt)
            };
            websocket.onclose = function(evt) {
                onClose(evt)
            };
            websocket.onmessage = function(evt) {
                onMessage(evt)
            };
            websocket.onerror = function(evt) {
                onError(evt)
            };
        }
    } else {
        console.log("sockets not supported");
        if (typeof(callback) != 'undefined') {
            callback();
        }
    }
}


function websocket_stop() {
    if (websocket != null) {
        websocket.close();
    }
}

function onOpen(evt) {
    //console.log("Log conectado");
}

function onClose(evt) {
    //console.log("Log desconectado");
    websocket = null;
}

function onMessage(evt) {
    var message = evt.data;
    try {
        message = JSON.parse(message)
        if (message.type == 'log') {
            if (typeof(message.data) == 'object') {
                var time = (message.time != undefined) ? message.time + ' - ' : '';
                data = message.data;
                if (data.porcentaje) {
                    barra(data.porcentaje);
                    if ($('#progreso_instagram').length > 0) {
                        $('#progreso_instagram').val(data.porcentaje).trigger('change');
                    }
                }
                if (data.mensaje) {
                    message = data.mensaje;
                } else {
                    message = ''
                }
                if (message != '') {
                    notificacion_footer(message);
                    if ($('#log_instagram').length > 0) {
                        p = $('<p></p>');
                        if (data && data.color) {
                            p.css('color', data.color);
                        }
                        if (data && data.bold) {
                            p.css('font-weight', 'bold');
                        } else {
                            p.css('font-weight', 'regular');
                        }
                        $('#log_instagram').prepend(p.append(time + message));
                        if ($('#log_instagram p').length > 500) {
                            $('#log_instagram p').each(function(k, v) {
                                if (k > 100) {
                                    $(v).remove();
                                }
                            });
                        }
                    }
                }

            } else {

            }
        }
    } catch (error) {}
}

function onError(evt, callback) {
    websocket = null;
    console.log("Error al conectar log");
    notificacion_footer("Error al conectar log");
    if (intento < 1) {
        intento++;
        websocket_start();
    } else {
        if (typeof(callback) != 'undefined') {
            callback();
        }
    }
}

function addMessage(message) {
    websocket.send(message);
    notificacion_footer(message);
}