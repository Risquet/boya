var buoys;
var zoom = 7;

function setupMap(buoys) {
    var southWest = L.latLng(19.8554808619, -84.9749110583),
        northEast = L.latLng(23.1886107447, -74.1780248685),
        bounds = L.latLngBounds(southWest, northEast);

    var center = [23.1351, -82.3326];
    var map = L.map("map", {
        center: center,
        zoom: zoom,
        zoomControl: false,
        // maxBounds: bounds,
        minZoom: 7,
        maxZoom: 18,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    }).addTo(map);
    map.attributionControl.setPrefix('')
    map.on('click', function (e) {
        console.log(e)
    });

    buoys.forEach((buoy) => {
        if (buoy.active) {
            var marker = L.marker([buoy.lat, buoy.lon]).addTo(map);
            marker.bindPopup(`<b>Boya Metoceánica</b><br>${buoy.name}.`, { closeButton: false, autoClose: false, closeOnClick: false }).openPopup();
            marker.on('click', function (e) {
                if (map.getZoom() < 14) {
                    map.flyTo([buoy.lat, buoy.lon], 14);
                } else {
                    document.location.href = `/buoys/${buoy.id}/`;
                }
            });
        }
    });
}

function getBuoys() {
    $.ajax({
        url: `/api/buoys/`,
        type: 'GET',
        dataType: 'json',
        success: function (response) {
            if (response.messageType == 'success') {
                buoys = response.data.results;
                setupMap(buoys);
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}

$(document).ready(() => {
    getBuoys();
});