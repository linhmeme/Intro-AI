let startPoint = null;
let endPoint = null;
let routePolyline = null;
let map = L.map("map").setView([21.0085, 105.8185], 15); // Tọa độ Thịnh Quang

// 🌍 Thêm lớp nền từ OpenStreetMap
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  //attribution: "© OpenStreetMap contributors",
}).addTo(map);


// Load Vector Tile
/* L.vectorGrid.protobuf("http://localhost:8080/data/map/{z}/{x}/{y}.pbf", {
  vectorTileLayerStyles: {
    // Style từng loại lớp (layers)
    points: { radius: 5, color: "#FF0000", fillColor: "#FF0000", fillOpacity: 0.8 },
    lines: { color: "#0000FF", weight: 2 },
    multilinestrings: { color: "#00FF00", weight: 2 },
    multipolygons: { color: "#00FFFF", fillColor: "#00FFFF", fillOpacity: 0.4 },
    other_relations: { color: "#FFA500", weight: 2 }
  },
  maxZoom: 18,
  attribution: "Bản đồ Phường Thịnh Quang"
}).addTo(map); */



// Load boundary
fetch("/static/geojson/boundary.geojson")
  .then((response) => response.json())
  .then((data) => {
    L.geoJSON(data, {
      style: {
        color: "red", // ✅ Màu vàng nổi bật
        weight: 5, // ✅ Tăng độ dày
        opacity: 0.5, // ✅ Đậm hoàn toàn
        dashArray: "1", // ✅ Thêm nét đứt cho ranh giới nhìn khác biệt (tuỳ chọn)
      },
    }).addTo(map);
  });


/* // Load diện tích
fetch("/static/geojson/area.geojson")
  .then((res) => res.json())
  .then((data) => {
    L.geoJSON(data, {
      style: { color: "#666", fillColor: "#0d0d2d", fillOpacity: 0.8 },
    }).addTo(map);
  });

// Load roads
fetch("/static/geojson/roads.geojson")
  .then((res) => res.json())
  .then((data) => {
    L.geoJSON(data, {
      style: { color: "#f0f0f0", weight: 2 },
    }).addTo(map);
  }); */

map.on("click", function (e) {
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

  fetch("/find_route", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      start: startCoords,
      end: endCoords,
      algorithm: algorithm,
    }),
  })
    .then((response) => response.json())
    .then((data) => animateSearch(data, startCoords, endCoords))
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

  // ✅ Vẽ đoạn nối từ vị trí người dùng → node thực tế
  if (startNode && userStart) {
    L.polyline([userStart, startNode], {
      color: "yellow",
      weight: 4,
      dashArray: "5,10",
    }).addTo(snapLayer);
  }
  if (endNode && userEnd) {
    L.polyline([userEnd, endNode], {
      color: "yellow",
      weight: 4,
      dashArray: "5,10",
    }).addTo(snapLayer);
  }

  let i = 0,
    j = 0;

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
