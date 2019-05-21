function inicio_graficos() {
    chart_followers();
    chart_hashtag();
}


function chart_hashtag() {
    var url = create_url(modulo, 'get_hashtag_users');
    post_basic(url, {}, 'Adquiriendo hashtag', function(data) {
        var data_response = generar_response(data, 'Usuarios');
        generar_grafico($('#chart-hashtag'), data_response, 'bar');
    });
}

function chart_followers() {
    var url = create_url(modulo, 'get_followers');
    post_basic(url, {}, 'Adquiriendo usuarios', function(data) {
        var sets = [{
                sets: ['Seguidores'],
                label: 'Seguidores',
                size: data['follower']
            },
            {
                sets: ['Siguiendo'],
                label: 'Siguiendo',
                size: data['following']
            },
            {
                sets: ['Seguidores', 'Siguiendo'],
                label: 'Seguidores y Siguiendo',
                size: data['both']
            },
            {
                sets: ['Favoritos'],
                label: 'Favoritos',
                size: data['favoritos']
            },
        ];


        generar_venn(sets, "#chart-seguidores", 'Usuarios');
        $(window).on('resize', function() {
            var width = $("#chart-seguidores").innerWidth();
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
    $.each(div.selectAll("path")._groups[0], function(k, v) {
        $(v).css('fill', randomColor({luminosity: 'light',count: 1}));
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
    var color=[]
    var border=[]
    $.each(initial_data, function(k, v) {
        label.push(k);
        final_data.push(v);
        color.push(randomColor({luminosity: 'light',format:'rgba',alpha:1}));
        border.push(randomColor({luminosity: 'light',format:'rgba',alpha:0.2}));
    });
    
    var data_response = {
        labels: label,
        datasets: [{
            label: title,
            data: final_data,
            backgroundColor: color,
            borderColor: border,
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