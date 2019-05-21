var chartColors = {
    red: 'rgba(255, 99, 132, 0.2)',
    orange: 'rgba(255, 159, 64, 0.2)',
    yellow: 'rgba(255, 205, 86, 0.2)',
    green: 'rgba(75, 192, 192, 0.2)',
    blue: 'rgba(54, 162, 235, 0.2)',
    purple: 'rgba(153, 102, 255, 0.2)',
    grey: 'rgba(201, 203, 207, 0.2)'
};

function inicio_graficos() {
    chart_followers();
    chart_hashtag();
    chart_total();
    $('.progress-bar').css('width', "50%");
}


function chart_total() {
    var url = create_url(modulo, 'get_total');
    post_basic(url, {}, 'Adquiriendo Totales', function(data) {
        var data_follows = generar_response(data.follows, 'Siguiendo', 'red');
        var data_unfollows = generar_response(data.unfollows, 'No siguiendo', 'blue');
        var data_start_follow = generar_response(data.start_follow, 'Seguidor', 'yellow');
        var data_stop_follow = generar_response(data.stop_follow, 'Dejo de seguir', 'green');

        var datasets = [
            data_follows.datasets[0],
            data_unfollows.datasets[0]
        ];
        var datasets2 = [
            data_start_follow.datasets[0],
            data_stop_follow.datasets[0]
        ];

        data_follows.datasets = datasets;
        generar_grafico($('#chart-total'), data_follows, 'line');

        data_start_follow.datasets = datasets2;
        generar_grafico($('#chart-total-seguidores'), data_start_follow, 'line');

    });
}


function chart_hashtag() {
    var url = create_url(modulo, 'get_hashtag_users');
    post_basic(url, {}, 'Adquiriendo hashtag', function(data) {
        var data_followers = generar_response(data.followers, 'Seguidores');
        generar_grafico($('#chart-hashtag-followers'), data_followers, 'pie');

        var data_eficiencia = generar_response(data.eficiencia, 'Eficiencia', 'yellow');
        generar_grafico($('#chart-hashtag-eficiencia'), data_eficiencia, 'bar');


        var data_following = generar_response(data.following, 'Siguiendo', 'blue');
        var data_removed = generar_response(data.removed, 'No siguiendo', 'green');
        var datasets = [
            data_following.datasets[0],
            data_removed.datasets[0],
            data_followers.datasets[0]
        ];
        data_followers.datasets = datasets;
        var options = {
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    stacked: true
                }]
            }
        };
        generar_grafico($('#chart-hashtag'), data_followers, 'bar', options);
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
    var progress = $(id).siblings()[0];
    $(progress).show().css('width', '75%');
    var chart = venn.VennDiagram().width(width);
    var div = d3.select(id).datum(sets).call(chart);
    div.selectAll(".venn-circle path").style("fill-opacity", .5).style("stroke-width", 3).style("stroke-opacity", 1);
    div.selectAll("text").style("fill", "white");
    var tooltip = d3.select(id).append("div").attr("class", "venntooltip");
    $(progress).css('width', '100%');
    $(progress).slideUp();
    $.each(div.selectAll("path")._groups[0], function(k, v) {
        $(v).css('fill', randomColor({
            luminosity: 'dark'
        }));
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





function generar_response(initial_data, title, hue) {
    var label = []
    var final_data = []
    var color = []
    var border = []
    $.each(initial_data, function(k, v) {
        label.push(k);
        final_data.push(v);

        if (typeof(hue) != 'undefined') {
            //color_base = randomColor({ luminosity: 'bright', hue: hue, format: 'rgba', alpha: 0.2 });
            color_base = chartColors[hue];
            color_border = color_base.replace("0.2", "1");
        } else {
            color_base = randomColor({
                luminosity: 'bright',
                format: 'rgba',
                alpha: 0.2
            });
            color_border = color_base.replace("0.2", "1");
        }
        color.push(color_base);
        border.push(color_border);
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

function generar_grafico(id, data, type, options_extra) {
    var progress = $(id).siblings()[0];
    $(progress).show();
    var options = {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        },
        animation: {
            onProgress: function(animation) {
                $(progress).css('width', 50 + 50 * (animation.animationObject.currentStep / animation.animationObject.numSteps) + '%');
            },
            onComplete: function() {
                $(progress).slideUp();
            }
        },
        elements: {
            point: {
                radius: 4,
                hoverRadius: 5,
                hitRadius: 10,
            }
        }
    };

    if (typeof(options_extra) != 'undefined') {
        var options = $.extend(true, options, options_extra);
    }


    

    var chart = new Chart(id, {
        type: type,
        data: data,
        options: options
    });
    return chart;
}