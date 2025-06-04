let allowedLayer = null;
let selectedFeature = null;
let currentVehicle = null; // Biến lưu đoạn đường người dùng chọn
let isAddingCondition = false;
let condition_cache = {}; // Lưu condition cho từng edge_id phía frontend

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
            color: "#6EC2F7",
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

      // Hiển thị bảng điều kiện
    document.getElementById('conditionOptions').style.display = 'grid';
      // Gán sự kiện click cho từng ô condition
    document.querySelectorAll('.condition-box').forEach(box => {
      box.onclick = function () {
        const condition = this.dataset.condition;
        const edge_id = String(selectedFeature.properties.id);  // Đảm bảo edge_id là string

        // ✅ Cập nhật vào biến toàn cục
        condition_cache[edge_id] = condition;

        // ✅ Gửi về backend để lưu tạm
        updateCondition(String(edge_id), condition);
        let color = "#00FF00";
        if (condition === "normal") color = "#00FF00"; 
        else if (condition === "jam") color = "#FF6666";
        else if (condition === "flooded") color = "#0099FF";
        else if (condition === "not allowed") color = "#FFD700";
        layer.setStyle({ color: color, weight: 5, opacity: 1 });

        document.getElementById('conditionOptions').style.display = 'none';
      };
  });
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

// Bắt sự kiện khi người dùng click vào các condition-box
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.condition-box').forEach(box => {
        box.addEventListener('click', function () {
            const condition = box.dataset.condition;

            if (selectedFeature) {
                const edge_id = selectedFeature.properties.id;
                condition_cache[edge_id] = condition;
                updateCondition(edge_id, condition);
                console.log(`Đã chọn điều kiện '${condition}' cho đoạn ${edge_id}`);
            } else {
                alert("Bạn cần nhấn vào đoạn đường trước khi chọn điều kiện.");
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const selected = document.getElementById("vehicle").value;
    currentVehicle = selected;
    filterRoutesByVehicle();  // gọi lần đầu khi mở trang
    // 🔁 Gọi lại khi người dùng đổi phương tiện
    document.getElementById('vehicle').addEventListener('change', () => {
      filterRoutesByVehicle();
      setTimeout(() => {
        finalizeCondition();
      }, 500);
    });
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
      alert("Chế độ thêm điều kiện đã tắt.");
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
  .catch(error => {
      console.error('Lỗi khi gọi finalize_conditions:', error);
  });
}


