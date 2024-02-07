function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: YOUR_INITIAL_LATITUDE, lng: YOUR_INITIAL_LONGITUDE },
        zoom: INITIAL_ZOOM_LEVEL
    });

    // Call a function to add markers to the map
    addMarkers(map);
}

function addMarkers(map) {
    var locations = [
        { lat: 37.7749, lng: -122.4194, label: 'A' },
        // Add more locations as needed
    ];

    for (var i = 0; i < locations.length; i++) {
        var marker = new google.maps.Marker({
            position: { lat: locations[i].lat, lng: locations[i].lng },
            map: map,
            label: locations[i].label
        });
    }
}
