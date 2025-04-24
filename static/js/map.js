let startPoint = null;
let endPoint = null;
let routePolyline = null;
let map = L.map("map").setView([21.0085, 105.8185], 15);  // Tọa độ Thịnh Quang

//fetch("/get_boundary")
fetch('/static/geojson/boundary.geojson')
.then(response => response.json())
.then(data => {
    L.geoJSON(data, {
        style: { color: 'black', weight: 8 }
      }).addTo(map);
});

// Load diện tích
fetch('/static/geojson/area.geojson')
.then(res => res.json())
.then(data => {
  L.geoJSON(data, {
    style: { color: '#666', fillColor: '#FFFFFF', fillOpacity: 0.8 }
  }).addTo(map);
});

// Load đường
// fetch('/static/geojson/roads.geojson')
// .then(res => res.json())
// .then(data => {
//     L.geoJSON(data, {
//     style: { color: '#f0f0f0', weight: 2 }
//     }).addTo(map);
// });

fetch('/static/geojson/edges.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            onEachFeature: onEachFeature
        }).addTo(map);
    });

// Load các nodes (nút giao)
fetch('/data/geojson/nodes.geojson')
.then(res => res.json())
.then(data => {
    L.geoJSON(data, {
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, {
                radius: 5,
                color: 'red',
                fillColor: 'red',
                fillOpacity: 1
            }).bindTooltip(feature.properties.id, {
                permanent: true,
                direction: 'top',
                className: 'node-label'
            });
        }
    }).addTo(map);
});

map.on("click", function(e) {
    if (!startPoint) {
        startPoint = L.marker(e.latlng, { draggable: true }).addTo(map).bindPopup("Xuất phát").openPopup();
    } else if (!endPoint) {
        endPoint = L.marker(e.latlng, { draggable: true }).addTo(map).bindPopup("Điểm đến").openPopup();
    }
});

let startMarker, endMarker, routeLayer, visitedLayer = null;

function findRoute() {
    if (!startPoint || !endPoint) {
        alert("Hãy chọn cả điểm xuất phát và điểm đến!");
        return;
    }
    
    let startCoords = [startPoint.getLatLng().lat, startPoint.getLatLng().lng];
    let endCoords = [endPoint.getLatLng().lat, endPoint.getLatLng().lng];
    let algorithm = document.getElementById("algorithm").value;

    fetch("/find_route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start: startCoords, end: endCoords, algorithm: algorithm })
    })
    .then(response => response.json())
    .then(data => animateSearch(data))
    .catch(error => console.error("Lỗi:", error));
}

function drawVisitedEdges(edges, color) {
    edges.forEach(([start, end]) => {
        L.polyline([start, end], { color: color, weight: 3, opacity: 1 }).addTo(visitedLayer);
    });
}

function animateSearch(data) {
    if (routeLayer) map.removeLayer(routeLayer);
    if (visitedLayer) map.removeLayer(visitedLayer);

    let edgesForward = data.edges_forward || [];
    let edgesBackward = data.edges_backward || [];
    let path = data.path || [];

    visitedLayer = L.layerGroup().addTo(map);
    routeLayer = L.layerGroup().addTo(map);

    let i = 0, j = 0;

    function drawVisited() {
        if (i < edgesForward.length) {
            drawVisitedEdges([edgesForward[i]], "#0b209c");
            i++;
        }

        if (edgesBackward.length > 0 && j < edgesBackward.length) {
            drawVisitedEdges([edgesBackward[j]], "#9c0b23");
            j++;
        }

        if (i < edgesForward.length || j < edgesBackward.length) {
            setTimeout(drawVisited, 10);
        } else {
            drawFinalPath(path);
        }
    }

    drawVisited();
}

function drawFinalPath(path) {
    if (path.length > 1) {
        L.polyline(path, { color: "green", weight: 5 }).addTo(routeLayer);
    }
}

function onEachFeature(feature, layer) {
    layer.on('click', function (e) {
        const edgeId = feature.properties.id;
        const currentCondition = feature.properties.condition || "none";
        const newCondition = prompt("Nhập condition cho đoạn đường (flooded, congestion...)", currentCondition);
        
        if (newCondition !== null) {
            fetch('/update-condition', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    edge_id: edgeId,
                    condition: newCondition
                })
            })
            .then(res => res.json())
            .then(data => alert(data.message))
            .catch(err => console.error('Error:', err));
        }
    });
}
console.log("Map loaded:", map);
