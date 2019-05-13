function inicio_map() {
    if (typeof(google) == 'undefined' || typeof(google.maps) == 'undefined') {
        $.getScript('https://maps.googleapis.com/maps/api/js?callback=inicio_map&key=' + googlemaps_key);
    } else {
        $('.map').each(function() {
            var t = $(this);
            generar_mapa(t);
        });
    }
}

function generar_mapa(e) {
    var coordenadas = {
        lat: ($('.lat', e).lenght==1 && $('.lat', e).val() != '') ? parseFloat($('.lat', e).val()) : -33.4488897,
        lng: ($('.lng', e).lenght==1 && $('.lng', e).val() != '') ? parseFloat($('.lng', e).val()) : -70.6692655
    }
    var mapa = $('.mapa', e)[0];
    var color = '';
    var $map_zoom = 15;
    var $marker_url = '';
    var map = new google.maps.Map(mapa, {
        center: coordenadas,
        zoom: $map_zoom,
        panControl: true,
        zoomControl: true,
        mapTypeControl: true,
        streetViewControl: true,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        scrollwheel: true,
        styles: [{
            "stylers": [{
                "hue": color
            }, {
                "saturation": 10
            }, {
                "gamma": 2.15
            }, {
                "lightness": 12
            }]
        }]
    });
    var marker = new google.maps.Marker({
        position: coordenadas,
        map: map,
        visible: true,
        icon: $marker_url,
        draggable: true
    });
    var infowindow = new google.maps.InfoWindow({
        maxWidth: 320,
        content: '<div id="mapcontent">' + '<p> <b>' + $('.titulo',e).val() + '</b><br/>' + $('.direccion', e).val() + '</p></div>'
    });
    google.maps.event.addListener(marker, 'click', function() {
        infowindow.open(map, marker);
    });
}