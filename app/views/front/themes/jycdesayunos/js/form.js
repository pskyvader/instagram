$(document).on('submit', '.contacto form', function(e) { // guardar formulario detalle
    var asunto = $('select[name=asunto] option:selected', this).val();
    if (asunto == '') {
        notificacion('Debes seleccionar un asunto', "error");
        return false;
    }
    habilitar(false);
    barra(50);
    var data = $(this).serializeObject();

    var f = $('input[type=file]', this);
    var archivo = [];
    if (f.length > 0) {
        $(f).each(function() {
            var files = $(this)[0].files;
            $(files).each(function(k, v) {
                archivo.push(v);
            });
        });
    }
    if (archivo.length == 0) archivo = null;

    post($(this).prop('action'), data, "Enviando mensaje", archivo, function(datos) {
        if (typeof(grecaptcha) != 'undefined' && datos.captcha) {
            grecaptcha.reset();
        }
    });
    return false;
});


function inicio_captcha() {
    if (typeof(grecaptcha) == 'undefined') {
        $.getScript('https://www.google.com/recaptcha/api.js');
    }else{
        grecaptcha.render("recaptcha");
    }
}

function habilitar(valor) {
    habilitado = (valor) ? false : true;
    elementos = $('form button');
    elementos.prop('disabled', habilitado).on("click", function() {
        return !habilitado;
    });
    if (habilitado) {
        elementos.css('opacity', '0.5');
        elementos.find('.fa-sync').remove();
        elementos.prepend('<i class="fas fa-sync fa-spin" style="position: absolute; left: 5px; top: calc(50% - 5px);"></i> ');
    } else {
        elementos.css('opacity', '1');
        elementos.find('.fa-sync').remove();
    }
}