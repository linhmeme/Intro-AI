let allowedLayer = null;
let selectedFeature = null; // Biến lưu đoạn đường người dùng chọn
let isAddingCondition = false;
let condition_cache = {}; // dùng ở JS

function filterRoutesByVehicle() {
    const selectedVehicle = document.getElementById('vehicle').value;
    currentVehicle = selectedVehicle;

    fetch('/filter_routes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ vehicle: selectedVehicle })
    })
    .then(res => res.json())
    .then(data => {
      console.log(data.message);
      updateAllowedRoutes(); // tải lại file vhc_allowed và hiển thị
    })
    .catch(err => console.error('Lỗi khi lọc các đoạn đường:', err));
  }
  
function updateAllowedRoutes() {
    if (allowedLayer) map.removeLayer(allowedLayer);
  
    fetch('/static/geojson/vhc_allowed.geojson?ts='+Date.now())
      .then(res => res.json())
      .then(data => {
        allowedLayer = L.geoJSON(data, {
          style: {
            color: "green",
            weight: 3,
            opacity: 0.9
          },
          onEachFeature: onEachFeature  // Gọi hàm khi nhấn vào các đoạn đường
        }).addTo(map);
      });
  }
  
// Hàm xử lý khi người dùng nhấn vào đoạn đường
function onEachFeature(feature, layer) {
    layer.on('click', function (e) {
        if (!isAddingCondition) return;
        selectedFeature = feature;  // Lưu lại feature (đoạn đường) người dùng chọn

        // Hiển thị dropdown
        let dropdown = document.getElementById('Condition');
        dropdown.style.display = 'block';  // Hiển thị dropdown

        // Đặt dropdown ở vị trí gần nơi người dùng nhấn trên bản đồ
        dropdown.style.position = 'absolute';
        dropdown.style.top = `${e.latlng.lat}px`;
        dropdown.style.left = `${e.latlng.lng}px`;

        // Cập nhật condition vào condition_cache khi người dùng chọn điều kiện
        dropdown.onchange = function () {
            let condition = dropdown.value;
            condition_cache[selectedFeature.properties.id] = condition;
            updateCondition(selectedFeature.properties.id, condition);

            // dropdown.style.display = 'none';

            // // Reset lại chế độ
            // isAddingCondition = false;
        };
    });
}

// Gửi yêu cầu tới API để cập nhật điều kiện vào condition_cache
function updateCondition(edge_id, condition) {
    fetch('/update_condition_temp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ edge_id: edge_id, condition: condition })
    })
    .then(res => res.json())
    .then(data => {
        console.log(data.message);
    })
    .catch(err => console.error('Lỗi khi cập nhật điều kiện:', err));
}

document.addEventListener("DOMContentLoaded", function () {
    const selected = document.getElementById("vehicle").value;
    currentVehicle = selected;
    filterRoutesByVehicle();  // gọi lần đầu khi mở trang
    // 🔁 Gọi lại khi người dùng đổi phương tiện
    document.getElementById('vehicle').addEventListener('change', filterRoutesByVehicle);
  });
  console.log("Đang lọc cho vehicle:", currentVehicle);

function addCondition() {
    console.log("Hàm addCondition được gọi");
    isAddingCondition = !isAddingCondition;
    
    if (isAddingCondition) {
      console.log("Chế độ thêm điều kiện đã bật");
      alert("Nhấn vào đoạn đường để thêm điều kiện.");
      document.getElementById('addCondition').innerText = "Tắt thêm điều kiện";
    } else {
      console.log("Chế độ thêm điều kiện đã tắt");
      alert("Chế độ thêm điều kiện đã tắt. Bạn có thể chọn điểm xuất phát và điểm đến.");
      document.getElementById('addCondition').innerText = "Thêm điều kiện";
  
      finalizeCondition();
    }
}

function finalizeCondition(){
  // Lấy phương tiện đã chọn và điều kiện đã thay đổi
  const vehicle = document.getElementById('vehicle').value;
  fetch('/finalize_conditions', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({
          vehicle: vehicle,
          conditions: condition_cache  // Gửi toàn bộ điều kiện đã thay đổi
      })
  })
  .then(response => response.json())
  .then(data => {
      console.log(data.message);  // In thông báo từ server
  })
  .catch(error => {
      console.error('Lỗi khi gọi finalize_conditions:', error);
  });
}