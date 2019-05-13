$('body').on('click', 'button.excel', {
    ext: '.xlsx'
}, preparar_excel);
$('body').on('click', 'button.csv', {
    ext: '.csv'
}, preparar_excel);
var worksheet = null;
var ext = '';

function preparar_excel(e) {
    var total_excel = parseInt($('#count_elementos').text());
    if (total_excel == 0) {
        notificacion('Oh no!', 'No existen datos para exportar', 'warning');
        return false;
    }
    ext = e.data.ext;
    worksheet = null;
    var limit = 20000;
    var page = 1;
    var url = create_url(modulo, 'excel');
    procesar_excel(url, page, limit, total_excel);
    setTimeout(function() {
        if (worksheet == null) {
            notificacion('Advertencia', 'La exportacion puede tomar un tiempo <br/> <b>por favor no cierres esta ventana<b/>', 'warning');
        }
    }, 3000);
}

function procesar_excel(url, page, limit, total_excel) {
    var info = {
        limit: ((page - 1) * limit),
        limit2: limit
    };
    if ((page * limit) >= total_excel) {
        var final = total_excel;
        var fin = true;
    } else {
        var final = (page * limit);
        var fin = false;
    }
    var mensaje = "Preparando documento, datos " + (info.limit + 1) + " a " + final + " de " + total_excel;
    var progress = ((info.limit) / total_excel) * 80;
    if (progress < 10) progress = 10;
    barra(progress);
    post_basic(url, info, mensaje, function(data) {
        if (typeof(data) != 'object') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                data = {
                    mensaje: data,
                    exito: false
                };
            }
        }
        if (!fin) {
            procesar_excel(url, page + 1, limit, total_excel);
            add_ws(data);
        } else {
            barra(80);
            add_ws(data);
            notificacion_footer('Exportando documento');
            setTimeout(function() {
                exportar_excel(data);
            }, 500);
        }
    });
}


function add_ws(data) {
    var skip = false;
    if (worksheet == null) {
        worksheet = XLSX.utils.json_to_sheet(data.exportar, {
            header: data.head,
            skipHeader: skip
        });
    } else {
        XLSX.utils.sheet_add_json(worksheet, data.exportar, {
            skipHeader: true,
            origin: -1
        });
    }
}

function exportar_excel(data) {
    var file = data.title;
    var filename = file + ext;
    var ws_name = "Hoja 1";
    var workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, ws_name);
    XLSX.writeFile(workbook, filename);
    notificacion('Confirmación', 'Documento Exportado', 'success');
    notificacion_footer(false);
    barra(100);
}