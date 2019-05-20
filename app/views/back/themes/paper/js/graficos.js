var chart_backgrounds = [
    'rgba(255, 99, 132, 0.2)',
    'rgba(54, 162, 235, 0.2)',
    'rgba(255, 206, 86, 0.2)',
    'rgba(75, 192, 192, 0.2)',
    'rgba(153, 102, 255, 0.2)',
    'rgba(255, 159, 64, 0.2)'
]
var chart_borders = [
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)'
]


function inicio_graficos() {
    chart_followers();
}

function chart_followers() {
    var url = create_url(modulo, 'get_followers');
    post_basic(url, {}, 'Adquiriendo usuarios', function(data) {
        //var data_response = generar_response(data, 'Usuarios');
        //generar_grafico($('#chart-seguidores'), data_response, 'bar');
        var sets = [];
        sets.push({ sets: ['Todos'], size: data['total'] });
        sets.push({ sets: ['Todos','Seguidores'], size: data['follower'] });
        sets.push({ sets: ['Todos','Siguiendo'], size: data['following'] });
        sets.push({ sets: ['Todos','Seguidores','Siguiendo'], size: data['both'] });
        
        var sets = [ {sets: ['A'], size: 12},
             {sets: ['B'], size: 12},
             {sets: ['A','B'], size: 2}];

        var chart = venn.VennDiagram();
        d3.select("#chart-seguidores").datum(sets).call(chart);

    });
}

function generar_response(initial_data, title) {
    var label = []
    var final_data = []
    var background = []
    var border = []
    var count_background = 0;
    var count_border = 0;
    $.each(initial_data, function(k, v) {
        label.push(k);
        final_data.push(v);
        if (typeof(chart_backgrounds[count_background]) == 'undefined') {
            count_background = 0;
        }
        background.push(chart_backgrounds[count_background]);
        if (typeof(chart_borders[count_border]) == 'undefined') {
            count_border = 0;
        }
        border.push(chart_borders[count_border]);
        count_background++;
        count_border++;
    })
    var data_response = {
        labels: label,
        datasets: [{
            label: title,
            data: final_data,
            backgroundColor: chart_backgrounds,
            borderColor: chart_borders,
            borderWidth: 1
        }]
    }
    return data_response

}



function generar_grafico(id, data, type) {
    var chart = new Chart(id, {
        type: type,
        data: data,
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });
    return chart;
}