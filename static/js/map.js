let startPoint = null;
let endPoint = null;
let routePolyline = null;
 // Tọa độ Thịnh Quang
let map = L.map("map", {
  maxZoom: 19,
  minZoom: 16.45,
  zoomControl: true,
  maxBounds: [
    [21.0020, 105.8120], // Góc dưới trái (SW)
    [21.0150, 105.8250]  // Góc trên phải (NE)
  ],
  maxBoundsViscosity: 1.0 // Càng gần 1.0 thì càng khó kéo ra ngoài
}).setView([21.0085, 105.8185], 16.5); // Tâm bản đồ Thịnh Quang

// 🌍 Thêm lớp nền từ OpenStreetMap
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  //attribution: "© OpenStreetMap contributors",
}).addTo(map);

// Load boundary
fetch("/static/geojson/boundary.geojson")
  .then((response) => response.json())
  .then((data) => {
    L.geoJSON(data, {
      style: {
        color: "red", 
        weight: 5, 
        opacity: 0.5, 
        dashArray: "1",
      },
    }).addTo(map);
  });

  map.on("click", function (e) {
    if (isAddingCondition) return;
    if (!startPoint) {
      startPoint = L.marker(e.latlng, { draggable: true })
        .addTo(map)
        .bindPopup("Xuất phát")
        .openPopup();
    } else if (!endPoint) {
      endPoint = L.marker(e.latlng, { draggable: true })
        .addTo(map)
        .bindPopup("Điểm đến")
        .openPopup();
    }
  });
  
  let startMarker,
    endMarker,
    routeLayer,
    visitedLayer = null;
  let snapLayer = null; // ✅ Thêm layer riêng cho snapping

  function findRoute() {
    if (!startPoint || !endPoint) {
      alert("Hãy chọn cả điểm xuất phát và điểm đến!");
      return;
    }
  
    let startCoords = [startPoint.getLatLng().lat, startPoint.getLatLng().lng];
    let endCoords = [endPoint.getLatLng().lat, endPoint.getLatLng().lng];
    let algorithm = document.getElementById("algorithm").value;
    let vehicle = document.getElementById("vehicle").value;
  
    fetch("/find_route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        start: startCoords,
        end: endCoords,
        algorithm: algorithm,
        vehicle: vehicle,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Dữ liệu trả về từ backend:", data);
        animateSearch(data, startCoords, endCoords);
        displayRouteInfo(data);
      })
      .catch((error) => console.error("Lỗi:", error));
  }
  
  function drawVisitedEdges(edges, color) {
    edges.forEach(([start, end]) => {
      L.polyline([start, end], { color: color, weight: 3, opacity: 1 }).addTo(
        visitedLayer
      );
    });
  }
  
  function animateSearch(data, userStart, userEnd) {
    if (routeLayer) map.removeLayer(routeLayer);
    if (visitedLayer) map.removeLayer(visitedLayer);
    if (snapLayer) map.removeLayer(snapLayer);
  
    let edgesForward = data.edges_forward || [];
    let edgesBackward = data.edges_backward || [];
    let path = data.path || [];
    let startNode = data.start_node; // ✅ lấy node thực từ server
    let endNode = data.end_node;
  
    visitedLayer = L.layerGroup().addTo(map);
    routeLayer = L.layerGroup().addTo(map);
    snapLayer = L.layerGroup().addTo(map);
    // Vẽ đoạn nối từ vị trí người dùng → node thực tế
    if (startNode && userStart) {
      L.polyline([userStart, startNode], {
        color: "red",
        weight: 4,
        //dashArray: "5,10",
      }).addTo(snapLayer);

      L.polyline([userEnd, endNode], {
        color: "red",
        weight: 4,
        //dashArray: "5,10",
      }).addTo(snapLayer);
    }
  
    let i = 0,
      j = 0;
  
    function drawVisited() {
      if (i < edgesForward.length) {
        drawVisitedEdges([edgesForward[i]], "green");
        i++;
      }
  
      if (edgesBackward.length > 0 && j < edgesBackward.length) {
        drawVisitedEdges([edgesBackward[j]], "purple");
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

  function animateCarOnRoute(path) {
    if (!path || path.length < 2) return;

    if (window.carMarker) {
        map.removeLayer(window.carMarker);
        window.carMarker = null;
    }

    const vehicle = document.getElementById("vehicle").value;

    let iconUrl = "";
    if (vehicle === "car") {
        iconUrl = "https://cdn-icons-png.flaticon.com/512/744/744465.png"; 
    } else if (vehicle === "motor") {
        iconUrl = "https://cdn-icons-png.flaticon.com/512/7910/7910762.png"; 
    } else if (vehicle === "foot") {
        iconUrl = "https://cdn-icons-png.flaticon.com/512/1668/1668531.png"; 
    }

    const vehicleIcon = L.icon({
        iconUrl: iconUrl,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
    });

    let i = 0;
    window.carMarker = L.marker(path[0], {icon: vehicleIcon}).addTo(map);

    function moveCar() {
        if (i < path.length) {
            window.carMarker.setLatLng(path[i]);
            i++;
            window.carTimer = setTimeout(moveCar, 200);
        }
    }
    moveCar();
}
  
  function drawFinalPath(path) {
    if (path.length > 1) {
      L.polyline(path, { color: "red", weight: 5 }).addTo(routeLayer);
    } else{
      alert("Không tìm thấy tuyến đường hợp lệ!");
    }
  }

function displayRouteInfo(result) {
  document.getElementById("total_length").innerText =
      "Tổng quãng đường: " + (result.total_length / 1000).toFixed(1) + " km";
  document.getElementById("total_travel_time").innerText =
      "Thời gian di chuyển: " + Math.round(result.total_travel_time * 60) + " phút";
}