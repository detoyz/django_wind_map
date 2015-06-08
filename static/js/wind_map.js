/**
 * Created by Ciuv on 27-May-15.
 */
var global_map;
var markers = [];
var post_count = 0;

function initialize() {
    // Create the map.
    var mapOptions = {
        zoom: 2,
        minZoom: 2,
        maxZoom: 10,
        center: new google.maps.LatLng(36.9, 9.6),
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        streetViewControl: false,
        panControl: false,
        mapTypeControl: false,
        zoomControlOptions:
        {
            style: "SMALL"
        }
    };
    global_map = new google.maps.Map(document.getElementById('map_canvas'), mapOptions);
    var styles = [
      {
        "elementType": "labels",
        "stylers": [
          { "visibility": "off" }
        ]
      },
      {
        "featureType": "landscape.natural",
        "elementType": "geometry",
        "stylers": [
          { "color": "#DBDBDB" },
          { "lightness": 35 }
        ]
      },
      {
        "featureType": "administrative.country",
        "elementType": "geometry",
        "stylers": [
          { "lightness": 60 }
        ]
      },
      {
        "featureType": "road",
        "stylers": [
          { "color": "#DBDBDB" },
          { "lightness": -20 }
        ]
      },
      {
        "featureType": "poi",
        "stylers": [
          { "color": "#DBDBDB" },
          { "lightness": 35 }
        ]
      }
    ];
    global_map.setOptions({styles: styles});
    google.maps.event.addListener(global_map, 'zoom_changed', draw_map);
    google.maps.event.addListener(global_map, 'dragend', draw_map);
}

google.maps.event.addDomListener(window, 'load', initialize);

function draw_map(){
    post_count++;
    clearOverlays();
    var current_zoom = global_map.getZoom();
    var current_bounds = global_map.getBounds();
    var lat_dist;
    var left = current_bounds.getSouthWest().F;
    var right = current_bounds.getNorthEast().F;
    if (left > 0 && right < 0) {
        lat_dist =(180 - left) + (180 - Math.abs(right));
    }else if (current_zoom == 2 && left < 0 && right < 0) {
        lat_dist = (180-left)+(180-Math.abs(right))
    }else if (current_zoom == 2 && left > 0 && right > 0) {
        lat_dist = (180-left)+180+right
    }else{
        lat_dist = left-right;
    }
    var object = {
        get_data: true,
        zoom: current_zoom,
        top: current_bounds.getNorthEast().A,
        bot: current_bounds.getSouthWest().A,
        left: current_bounds.getSouthWest().F,
        right: current_bounds.getNorthEast().F,
        lon_dist: Math.abs(current_bounds.getNorthEast().A - current_bounds.getSouthWest().A),
        lat_dist: Math.abs(lat_dist),
        post_count: post_count
    };
    $.ajaxSetup({
        headers: { "X-CSRFToken":ajGetCookie('csrftoken') }
    });
    $.ajax({
        url: "",
        type: 'POST',
        data: JSON.stringify(object),
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        },
        success: function rps(res) {
            var data = res.data;
            if (res.post_count == post_count) {
                for (var i = 0; i < data.length; i++) {
                    var marker = new google.maps.Marker({
                        position: new google.maps.LatLng(data[i].latitude, data[i].longitude),
                        map: global_map,
                        clickable: false,
                        icon: {
                            path: data[i].path,
                            scale: 0.55,
                            strokeWeight: 1.75,
                            rotation: data[i].direction
                        }
                    });
                    markers.push(marker);
                }
            }else{
                return
            }
        }
    });
}

function ajGetCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim(); //jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function clearOverlays() {
    if (markers.length > 0) {
        for (var j = 0; j < markers.length; j++ ) {
            markers[j].setMap(null);
        }
    }
    markers=[];
}


