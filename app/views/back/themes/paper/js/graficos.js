var chart_backgrounds = [
    'rgb(214, 39, 40, 0.2)',
    'rgba(255, 206, 86, 0.2)',
    'rgba(75, 192, 192, 0.2)',
    'rgba(153, 102, 255, 0.2)',
    'rgba(255, 159, 64, 0.2)',
    'rgb(44, 160, 44, 0.2)',
    'rgba(54, 162, 235, 0.2)',
    'rgba(255, 99, 132, 0.2)'
]
var chart_borders = [
    'rgb(214, 39, 40, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
    'rgb(44, 160, 44, 1)',    
    'rgba(54, 162, 235, 1)',
    'rgba(255, 99, 132, 1)'
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
        sets.push({
            sets: ['Seguidores'],
            label: 'Seguidores',
            size: data['follower'],
        });
        sets.push({
            sets: ['Siguiendo'],
            label: 'Siguiendo',
            size: data['following'],
        });
        sets.push({
            sets: ['Seguidores', 'Siguiendo'],
            label: 'Seguidores y Siguiendo',
            size: data['both'],
        });
        sets.push({
            sets: ['Favoritos'],
            label: 'Favoritos',
            size: data['favoritos'],
        });
        sets.push({
            sets: ['Seguidores','Favoritos'],
            label: 'Favoritos',
            size: data['favoritos-follower'],
        });
        sets.push({
            sets: ['Siguiendo','Favoritos'],
            label: 'Favoritos',
            size: data['favoritos-following'],
        });
        sets.push({
            sets: ['Seguidores', 'Siguiendo','Favoritos'],
            label: 'Favoritos',
            size: data['favoritos-follower-following'],
        });
        generar_venn(sets, "#chart-seguidores", 'Usuarios');
        $(window).on('resize', function(){
            var width = $("#chart-seguidores").empty().innerWidth();
            var chart = venn.VennDiagram().width(width);
            d3.select("#chart-seguidores").datum(sets).call(chart);
        });
    });
}






function generar_venn(sets, id, title) {
    var width = $(id).empty().innerWidth();
    var chart = venn.VennDiagram().width(width);
    var div = d3.select(id).datum(sets).call(chart);
    div.selectAll(".venn-circle path").style("fill-opacity", .5).style("stroke-width", 3).style("stroke-opacity", 1);
    div.selectAll("text").style("fill", "white");
    var tooltip = d3.select(id).append("div").attr("class", "venntooltip");
    var count = 0;
    $.each(div.selectAll("path")._groups[0], function(k, v) {
        if (typeof(chart_borders[count]) == 'undefined') {
            count = 0;
        }
        $(v).css('fill', chart_borders[count]);
        count++;
    });
    div.selectAll("g").on("mouseover", function(d, i) {
        venn.sortAreas(div, d);
        tooltip.transition().duration(40).style("opacity", 1);
        tooltip.text(d.size + " " + title + " " + d.label);
        var selection = d3.select(this).transition("tooltip").duration(400);
        var opacity = d.sets.length >= 1 ? .8 : 0;
        selection.select("path").style("stroke-width", 3).style("fill-opacity", opacity).style("stroke", "fff");
    }).on("mousemove", function() {
        tooltip.style("left", (d3.event.offsetX - 30) + "px").style("top", (d3.event.offsetY + 50) + "px");
    }).on("mouseout", function(d, i) {
        tooltip.transition().duration(100).style("opacity", 0);
        var selection = d3.select(this).transition("tooltip").duration(200);
        var opacity = d.sets.length == 1 ? .5 : 0;
        selection.select("path").style("stroke-width", 3).style("fill-opacity", opacity).style("stroke", "none");
    });
    return chart;
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