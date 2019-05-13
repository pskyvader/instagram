function inicio_map() {
    if (typeof(google) == 'undefined' || typeof(google.maps) == 'undefined') {
        $.getScript('https://maps.googleapis.com/maps/api/js?callback=inicio_map&key=' + googlemaps_key);
    } else {
        $('div.form-group.map').each(function() {
            var t = $(this);
            generar_mapa(t);
            $(t).on('click', '.buscar_mapa', function(e) {
                e.preventDefault();
                buscar_direccion(t);
            });
        });
    }
}

function generar_mapa(e) {
    var coordenadas = {
        lat: ($('.lat', e).val() != '') ? parseFloat($('.lat', e).val()) : -33.4488897,
        lng: ($('.lng', e).val() != '') ? parseFloat($('.lng', e).val()) : -70.6692655
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
        content: '<div id="mapcontent">' + '<p> <b>' + $('#titulo').val() + '</b><br/>' + $('.direccion', e).val() + '</p></div>'
    });
    google.maps.event.addListener(marker, 'click', function() {
        infowindow.open(map, marker);
    });
    google.maps.event.addListener(marker, 'dragend', function() {
        geocodePosition(marker.getPosition(), e);
    });
}



function geocodePosition(pos, e) {
    geocoder = new google.maps.Geocoder();
    geocoder.geocode({
        latLng: pos
    }, function(results, status) {
        if (status == 'OK') {
            $('.lat', e).val(pos.lat());
            $('.lng', e).val(pos.lng());
            $('.direccion', e).val(results[0].formatted_address);
        } else {
            setTimeout(function() {
                geocodePosition(pos, e);
            }, 1000);
        }
    });
}

function buscar_direccion(e) {
    var direccion = $('.direccion', e).val().trim();
    var elemento = $('.mapa', e)[0];
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({
        'address': direccion
    }, function(results, status) {
        if (status == 'OK') {
            $('.lat', e).val(results[0].geometry.location.lat);
            $('.lng', e).val(results[0].geometry.location.lng);
            $('.direccion', e).val(results[0].formatted_address);
            generar_mapa(e);
        } else {
            setTimeout(function() {
                buscar_direccion(e);
            }, 1000);
        }
    });
}