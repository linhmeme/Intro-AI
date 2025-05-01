window.addEventListener('load', () => {
  fetch('/reset_roads', { method: 'POST' })
  .then(res => res.json())
  .then(data => {
      console.log(data.message);
  })
  .catch(err => console.error('Lỗi reset roads:', err));
});

let startPoint = null;
let endPoint = null;
let routePolyline = null;
let map = L.map("map").setView([21.0085, 105.8185], 15); // Tọa độ Thịnh Quang

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
        color: "red", // ✅ Màu vàng nổi bật
        weight: 5, // ✅ Tăng độ dày
        opacity: 0.5, // ✅ Đậm hoàn toàn
        dashArray: "1", // ✅ Thêm nét đứt cho ranh giới nhìn khác biệt (tuỳ chọn)
      },
    }).addTo(map);
  });

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

  let addingCondition = false;
  let addConditionButton = null;
  function filterRoutesByVehicle() {
    const selectedVehicle = document.getElementById('vehicle').value;

    fetch('/filter_routes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ vehicle: selectedVehicle })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
    })
    .catch(err => console.error('Lỗi khi lọc các đoạn đường:', err));
  }

// Hàm thêm điều kiện cho các đoạn đường
function addCondition() {
  if (!addConditionButton) {
      addConditionButton = document.querySelector('button[onclick="addCondition()"]');
  }

  addingCondition = !addingCondition;

  if (addingCondition) {
      addConditionButton.textContent = "Huỷ thêm điều kiện";
      alert("🛠️ Đã bật chế độ thêm điều kiện.\nClick vào các đoạn đường để nhập (cấm hoặc không cấm).");
  } else {
      addConditionButton.textContent = "Thêm điều kiện";
      alert("✅ Đã huỷ chế độ thêm điều kiện. Bạn có thể chọn điểm xuất phát và điểm đến.");
  }
}

// Hàm xử lý khi click vào đoạn đường
function onEachFeature(feature, layer) {
  layer.on('click', function (e) {
      if (!addingCondition) return;

      const edgeId = feature.properties.id;
      const currentCondition = feature.properties.condition || "normal";
      const newCondition = prompt("Nhập condition cho đoạn đường:\n - 'normal' (được đi)\n - 'not allowed' (cấm đi)", currentCondition);

      if (newCondition === "normal" || newCondition === "not allowed") {
          // Gửi yêu cầu cập nhật condition vào backend (Flask API)
          fetch('/update_condition', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  edge_id: edgeId,
                  condition: newCondition,
                  vehicle: document.getElementById('vehicle').value  // Sử dụng phương tiện người dùng chọn
              })
          })
          .then(res => res.json())
          .then(data => {
              alert(data.message);
              feature.properties.condition = newCondition; // Cập nhật condition tại chỗ
              layer.setStyle({ color: getColorByCondition(newCondition) }); // Đổi màu đoạn đường
          })
          .catch(err => console.error('Lỗi khi gửi dữ liệu:', err));
      } else {
          alert("❌ Chỉ được nhập 'normal' hoặc 'not allowed'!");
      }
  });
}

// Chỉnh màu đường tùy theo condition
function getColorByCondition(condition) {
  switch (condition) {
      case 'not allowed': return 'black';  // Màu đen cho đường cấm
      case 'normal': return 'green';      // Màu xanh cho đường bình thường
      default: return 'gray';
  }
}

console.log("Map loaded:", map);
