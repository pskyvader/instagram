function inicio_list() {
    inicio_sitemap();
    // Sortable rows
    var table = $('.sorted_table').sortable_jquery({
        containerSelector: 'table',
        handle: 'td.move',
        itemPath: '> tbody',
        itemSelector: 'tr',
        placeholder: '<tr class="placeholder"/>',
        distance: 20,
        tolerance: 2,
        onDrop: function($item, container, _super) {
            var $clonedItem = $('<tr/>').css({
                height: 0
            });
            $item.before($clonedItem);
            $clonedItem.animate({
                'height': $item.height()
            });
            $item.animate($clonedItem.position(), function() {
                $clonedItem.detach();
                _super($item, container);
            });
            var data = table.sortable_jquery("serialize").get();
            update_orden(data);
        }
    });
    $('.panel .table').basictable({
        breakpoint: 992,
    });
}

$('body').on('show.bs.modal', '.modal', function(e) {
    var data = e.relatedTarget.dataset;
    var img = $('img', e.target);
    $('.modal-body > a', $(this)).prop('href', data.original);
    $(img).prop('src', data.zoom);
    //$('.modal .modal-body .cambiar-foto input[name="..."]').data('id', data.id);
    //$('.modal .modal-body .cambiar-foto .guardar_modal').data('id', data.id);
});
$('body').on('change', 'select[name=limit]', function() {
    var data = createObjFromURI();
    data.limit = $('option:selected', $(this)).val();
    data.page = 1;
    var url = create_url(null, null, data);
    go_url(url);
});
$('body').on('submit', 'form.search', function() {
    var data = createObjFromURI();
    if ($('input[name=search]', $(this)).val() != '') {
        data.search = $('input[name=search]', $(this)).val();
    }else{
        delete(data.search)
    }
    data.page = 1;
    var url = create_url(null, null, data);
    go_url(url);
    return false;
});
$('body').on('click', 'table button.eliminar', function() {
    $('.modal-eliminar #nombre_elemento').text($('tr[data-id="' + $(this).data('id') + '"] td[data-field=titulo]').text());
    $('.modal-eliminar input[name=id_eliminar]').val($(this).data('id'));
});
$('body').on('click', 'button.accion', function() {
    var accion = $(this).data('action');
    var id = $(this).data('id');
    var mensaje = $(this).data('mensaje');
    post(create_url(modulo, accion), {
        id: id
    }, mensaje);
});

function eliminar_elemento() {
    var id = $('.modal-eliminar input[name=id_eliminar]').val();
    var info = {
        id: id
    };
    $('tr[data-id="' + id + '"]').remove();
    post(create_url(modulo, 'eliminar'), info, "Eliminando", !1);
}
$('body').on('click', 'table button.active', function() {
    var info = {
        id: $(this).data('id'),
        campo: $(this).data('field'),
        active: $(this).data('active')
    };
    info.active = !(info.active);
    cambiar_estado(info);
    post(create_url(modulo, 'estado'), info, "Actualizando Estado", !1);
});

function cambiar_estado(info) {
    var btn = $('button.active[data-id="' + info.id + '"][data-field=' + info.campo + ']');
    var clase = (info.active) ? 'btn-success' : 'btn-danger';
    var icono = (info.active) ? 'fa-check' : 'fa-close';
    btn.data('active', info.active).removeClass('btn-success btn-danger').addClass(clase);
    $('i.fa', btn).removeClass('fa-check fa-close fa-question-circle').addClass(icono);
}