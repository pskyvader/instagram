function inicio_multiple() {
    inicio_sorted();
    $('div.form-group.multiple').each(function() {
        multiple($(this));
    });
}

function inicio_sorted() {
    $(".sorted_multiple").sortable({
        cursor: "move",
        placeholder: "placeholder",
        forcePlaceholderSize: true,
        handle: '.move',
        revert: true,
        scrollSensitivity: 120,
        scrollSpeed: 30,
    });
}

function multiple(e) {
    var new_line = $('.new_line', e).clone();
    $('.new_line', e).remove();
    var count = $('input[name=count]', e).val();
    $('input[name=count]', e).remove();
    $('.campo.fields .active', e).each(function() {
        multiple_active($(this));
    });
    $(e).on('click', '.agregar_editar', function() {
        var new_l = new_line.clone();
        multiple_active($('.active', new_l));
        $(this).parent().parent().after(new_l);
        //$('.sorted_multiple',$(this).parents('.multiple')).append(new_l);
        count++;
        inicio_sorted();
        return false;
    });
    $(e).on('click', '.quitar_editar', function() {
        $(this).parents('.campo').remove();
        count--;
        if (count == 0) {
            $('.new_field', e).show();
        }
        return false;
    });
}

function multiple_active(active) {
    if (typeof(active) != 'undefined' && active.length > 0) {
        var n = parseInt(Math.random() * 100000);
        active[0].dataset.field = active.data('field') + n;
        active.data('field', active.data('field') + n);
        var input = active.siblings();
        input.prop('id', input.prop('id') + n);
    }
}