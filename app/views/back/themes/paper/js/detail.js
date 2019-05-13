var config_editor = {
    height: 400,
    on: {
        instanceReady: loadBootstrap
    }
};
var token = null;
var editor = null;
var url_list = '';
var timestamp = 13;

function inicio_detail() {
    if ($('div.form-group.image').length > 0) {
        inicio_image();
    }
    if ($('div.form-group.file').length > 0) {
        inicio_file();
    }
    url_list = $('form#formulario').data('list');
    token = $('input.token-campo');
    $(token).tokenfield({
        createTokensOnBlur: true
    });
    editor = $('textarea.editor');
    if (editor.length > 0) {
        //CKEDITOR.timestamp = timestamp;
        $(editor).each(function() {
            CKEDITOR.replace($(this).prop('name'), config_editor);
        });
    }
    var iconos = $('select.icons');
    if (iconos.length > 0) {
        $.get(path + 'icon.txt', function(data) {
            var data = data.split("\n");
            $(data).each(function(k, v) {
                v = v.trim();
                var selected = '';
                if (v == iconos.data('value')) {
                    selected = 'selected="selected"';
                }
                var option = $('<option value="' + v + '" ' + selected + '>' + v + '</option>');
                iconos.append(option);
            });
        });
        $("select.icons").select2({
            width: '100%',
            minimumInputLength: 0,
            templateResult: formato_icono,
            templateSelection: formato_icono
        });
    }
    if ($('div.form-group.multiple').length > 0) {
        inicio_multiple();
    }

    if ($('div.form-group.map').length > 0) {
        inicio_map();
    }
    inicio_pedido();

    if ($('form#formulario input.url-field').length > 0) {
        $('body').on('keyup', 'form#formulario input.url-field', function() {
            $($(this)).val(urlamigable($(this).val()));
        });
        $('body').on('blur', 'form#formulario input.url-field', function() {
            $($(this)).val(urlamigable($(this).val()));
        });

        $('body').on('keyup', 'form#formulario input[name=titulo]', function() {
            $('form#formulario input.url-field').first().val(urlamigable($(this).val()));
        });
        $('body').on('blur', 'form#formulario input[name=titulo]', function() {
            $('form#formulario input.url-field').first().val(urlamigable($(this).val()));
        });
    }
    $('body').on('change', '.recursive-input', function() {
        count_elementos($(this));
    });


    $('.daterange').daterangepicker({
        timePicker: true,
        timePicker24Hour: true,
        timePickerIncrement: 15,
        locale: {
            format: 'DD/MM/YYYY HH:mm'
        }
    });

    $(".date").datetimepicker({
        todayHighlight: true
    });

    $('.cpicker').colorpicker();
}


function count_elementos(e) {
    setTimeout(function() {
        var n = $('input:checked', e).length;
        if (n > 0) {
            $('.name', e).val(n);
        } else {
            $('.name', e).val('');
        }
    }, 100);
}

function generar(longitud) {
    var caracteres = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
    var pass = "";
    for (i = 0; i < longitud; i++) {
        pass += caracteres.charAt(Math.floor(Math.random() * caracteres.length));
    }
    return pass;
}
$('body').on('click', 'form#formulario a.generar_pass', function() {
    var pass = generar(8);
    $(this).siblings('input').val(pass).prop('type', 'text');
});



function formato_icono(icono) {
    if (!icono.id) {
        return icono.text;
    }
    var i = $('<span><i class="material-icons">' + icono.element.value + '</i>' + icono.element.value + '</span><span>');
    return i;
};
$(document).on('click', 'form#formulario button.active', function() {
    var info = {
        id: $(this).data('id'),
        campo: $(this).data('field'),
        active: $(this).data('active')
    };
    info.active = !(info.active);
    $(this).siblings('input').val(info.active);
    cambiar_estado(info);
    return false;
});

function loadBootstrap(event) {
    event.editor.balloonToolbars.create({
        buttons: 'Link,Unlink,Image',
        widgets: 'image'
    });
    var jQueryScriptTag = document.createElement('script');
    var bootstrapScriptTag = document.createElement('script');
    jQueryScriptTag.src = 'https://code.jquery.com/jquery-1.11.3.min.js';
    bootstrapScriptTag.src = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js';
    var editorHead = event.editor.document.$.head;
    editorHead.appendChild(jQueryScriptTag);
    jQueryScriptTag.onload = function() {
        editorHead.appendChild(bootstrapScriptTag);
    };
}
var permanecer = false;
$(document).on('click', '#guardar', function() {
    permanecer = false;
});
$(document).on('click', '#guardar-permanecer', function() {
    permanecer = true;
});
$(document).on('click', '#cancelar', function() {
    go_url(url_list);
});
var after_guardar = function(data) {
    if (permanecer && typeof(data.id) != 'undefined') {
        id = data.id;
        if ($('form#formulario input[name=id]').val() == "") {
            go_url(create_url(null, id), 'a');
        } else {
            go_url(create_url(null), 'a');
        }
    } else {
        go_url(url_list);
    }
};
$(document).on('submit', 'form#formulario', function(e) { // guardar formulario detalle
    habilitar(false);
    var error = false;
    error = validar($(this));
    if (!error) {
        barra(50);
        var data = $(this).serializeObject();
        post($(this).prop('action'), data, "Guardando", !0, null, after_guardar);
    } else {
        habilitar(true);
    }
    return false;
});

function validar(form) { //validar campos al editar elemento
    var requeridos = $(':input[required]', form);
    var nombres = '';
    var error = false;
    $(requeridos).each(function() {
        if ($(this).val() == '') {
            $(this).parent().parent().addClass('has-error');
            var n = $(this).data('campo');
            if (!n || n == '') n = $(this).prop('name');
            if (n == '') n = $(this).prop('id');
            nombres += "<br/><b>" + n + "</b>";
            error = true;
        } else if ($(this).prop('id') == 'rut') {
            var isValid = $.validateRut($(this).val());
            if (!isValid) {
                $(this).parent().parent().addClass('has-error');
                var n = $(this).prop('name');
                if (n == '') n = $(this).prop('id');
                nombres += "<br/><b>" + n + "</b>";
                error = true;
            }
        }
    });
    if (error) {
        var mensaje = 'Hay campos vacíos, debes llenar los campos obligatorios:' + nombres;
        notificacion('Oh No!', mensaje, 'error');
        mover('.has-error');
    }
    return error;
}