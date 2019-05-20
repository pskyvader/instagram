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
    post(create_url(modulo, 'get_followers'), {
        id: id
    }, mensaje, false, null, function(data){
        
        var data_response = {
            labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
            datasets: [{
                label: '# of Votes',
                data: [12, 19, 3, 5, 2, 3],
                backgroundColor: chart_backgrounds,
                borderColor: chart_borders,
                borderWidth: 1
            }]
        }
        generar_grafico($('#chart-seguidores'), data_response, 'bar');
    });
}



function generar_grafico(id,data,type) {
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