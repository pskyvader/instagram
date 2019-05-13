function inicio_file() {
    $('.file_multiple').each(function() {
        inicio_file_multiple($(this));
    });
    $('.file_individual').each(function() {
        var t = $(this);
        $(t).on('change', 'input[name="..."]', function(e) {
            habilitar(false);
            if (e.target.files.length > 0) {
                if (max_size > 0 && e.target.files[0].size > max_size) {
                    notificacion('Oh no!', "Tamaño de archivo demasiado grande.<br/>Tamaño de archivo maximo " + max_size_format, 'error');
                    habilitar(true);
                } else {
                    post(create_url(modulo, 'upload_file'), {}, "Subiendo Archivo", !1, e.target.files, after_guardar_file, t);
                }
            }
        });
        $('body').on('click', '.eliminar_file', function() {
            $('#eliminar_editar_file', t).data('id', $(this).data('id'));
        });
    });
}

var after_guardar_file = function(data, t) {
    $('.tmp', t).val(data.archivos[0].name);
    $('.name', t).val(data.archivos[0].name);
    $('.original_name', t).val(data.archivos[0].original_name);
};


function eliminar_file(campo) {
    $('input[name="file[' + campo + '][0][url]"]').val('');
    $('input[name="file[' + campo + '][0][tmp]"]').val('');
    $('input[name="' + campo + '"]').val('');
    $('img.' + campo).remove();
    $('.eliminar_file[data-id=' + campo + ']').hide();
}


function inicio_file_multiple(e) {
    var url = create_url(modulo, 'upload_file');
    var multiple = false;
    var parallel = 3;
    var new_line = $('.new_line', e).clone();
    $('.new_line', e).remove();
    $(".multiple_file", e).addClass('dropzone');
    var archivos_temporal = [];
    var id = [];
    var id_actual = 0;
    $('.file_list .campo.fields', e).each(function() {
        id[$('.id', this).val()] = $('.id', this).val();
    });
    $(".multiple_file", e).dropzone({
        addRemoveLinks: true,
        paramName: 'file',
        createfileThumbnails: false,
        url: url,
        parallelUploads: parallel,
        uploadMultiple: multiple,
        init: function() {
            this.on("addedfile", function(e) {
                    archivos_temporal.push(e.name), habilitar(!1), e.previewElement.addEventListener("click", function() {
                        this.removeFile(e);
                    });
                }),
                this.on("removedfile", function(e, i) {
                    var a = $.inArray(e.name, archivos_temporal); - 1 != a && archivos_temporal.splice(a, 1), 0 == archivos_temporal.length && habilitar(!0);
                }),
                this.on("success", function(file, datos) {
                    if (typeof(datos) != 'object') {
                        var datos = JSON.parse(datos);
                    }
                    if (typeof(datos['exito']) != 'undefined' && datos['exito']) {
                        var mensaje = 'filen ' + (($.isArray(datos['mensaje'])) ? datos['mensaje'].join('<br/>') : datos['mensaje']) + ' añadida correctamente';
                        notificacion_footer(mensaje);
                        $(datos['archivos']).each(function(k, v) {
                            if (file.name == v.original_name) {
                                do {
                                    id_actual++;
                                } while (typeof(id[id_actual]) != 'undefined');
                                id[id_actual] = id_actual;
                                var new_l = new_line.clone();
                                $('.file', new_l).prop('href', v.url).text(v.original_name);
                                $('.tmp', new_l).val(v.name);
                                $('.id', new_l).val(id_actual);
                                $('.original_name', new_l).val(v.original_name);
                                multiple_active($('.active', new_l));
                                $('.file_list').append(new_l);
                            }
                        });
                    } else {
                        notificacion('Oh no!', datos['mensaje'], 'error');
                    }
                    this.removeFile(file);
                }), this.on("complete", function(e, i) {
                    var a = $.inArray(e.name, archivos_temporal); - 1 != a && archivos_temporal.splice(a, 1), 0 == archivos_temporal.length && habilitar(!0)
                }),
                this.on('error', function(e, f) {
                    console.log(e, f);
                })
        }
    });
    $(".file_list.sorted_multiple").sortable_jquery({
        handle: ".move",
        vertical: !1,
        itemSelector: ".campo",
        placeholder: '<div class=" placeholder campo col-sm-2"><div class="move"></div></div>',
        containerSelector: ".sorted_multiple",
        distance: 30,
        tolerance: 0,
        onDragStart: function(e, i, a) {
            e.css({
                height: e.outerHeight() / 2,
                width: e.outerWidth() / 2
            }), e.addClass(i.group.options.draggedClass)
        }
    })
}