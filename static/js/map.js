let startPoint = null;
let endPoint = null;
let routePolyline = null;
let map = L.map("map").setView([21.0092, 105.8223], 16);  // Tọa độ Thịnh Quang

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

fetch("/get_boundary")
.then(response => response.json())
.then(data => {
    const boundaryCoords = data.boundary.map(coord => [coord[1], coord[0]]); 
    
    L.polygon(boundaryCoords, {color: "red", weight: 3}).addTo(map);
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
    .then(data => {
        if(data.error) {
            alert(data.error)
                return;
        }
        //ve tuyen duong
        animateSearch(data);
        //hien thi huong dan duong di va thoi gian di chuyen
        showDirections(data.streets, data.distance);
    })
    .catch(error => console.error("Lỗi:", error));
}

function drawVisitedEdges(edges, color) {
    edges.forEach(([start, end]) => {
        L.polyline([start, end], { color: color, weight: 3, opacity: 0.7 }).addTo(visitedLayer);
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
            drawVisitedEdges([edgesForward[i]], "blue");
            i++;
        }

        if (edgesBackward.length > 0 && j < edgesBackward.length) {
            drawVisitedEdges([edgesBackward[j]], "red");
            j++;
        }

        if (i < edgesForward.length || j < edgesBackward.length) {
            setTimeout(drawVisited, 50);
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

function showDirections(streets, distance) {
    let directionsDiv = document.getElementById("directions");
    directionsDiv.innerHTML = "<h3>Hướng dẫn di chuyển</h3>";
    //hiển thị danh sách các con đường đi qua
    streets.forEach((street, index) => {
        directionsDiv.innerHTML += `<p>${index + 1}. Đi qua: <b>${street}</b></p>`;
    });
    //tinh thoi gian du kien dua vao phuong tien
    let vehicle = document.querySelector('input[name="vehicle"]:checked').value;
    let speed = vehicleSpeeds[vehicle]; //toc do km/h
    let time = distance / speed * 60; //chuyen doi sang phut

    directionsDiv.innerHTML += `<h4>Khoảng cách: ${distance.toFixed(2)} km</h4>`;
    directionsDiv.innerHTML += `<h4>Thời gian dự kiến: ${time.toFixed(0)} phút</h4>`;
}

//toc do trung binh cua phuong tien(km/h)
const vehicleSpeeds = {
    "walking": 5,
    "bicycle": 15,
    "motorbike": 35,
    "car": 50
};