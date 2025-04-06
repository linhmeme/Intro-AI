import json
from math import sqrt

def distance(p1, p2):
    return round(sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2), 2)

# Đọc node từ file
with open("nodes.json") as f:
    nodes = json.load(f)

graph = {}

print("Danh sách node:")
for name in nodes:
    print("-", name)

print("\nNhập cặp node muốn nối (vd: A B), nhập '.' để dừng:")

while True:
    inp = input("Nối 2 node: ").strip()
    if inp == ".":
        print("Kết thúc nhập liệu.")
        break 
    try:
        n1, n2 = inp.upper().split()
        if n1 in nodes and n2 in nodes:
            d = distance(nodes[n1], nodes[n2])
            # Hai chiều
            graph.setdefault(n1, {})[n2] = d
            graph.setdefault(n2, {})[n1] = d
            print(f"✓ Đã nối {n1} <--> {n2}, khoảng cách = {d}")
        else:
            print("⚠️ Node không tồn tại.")
    except Exception as e:
        print("❌ Lỗi cú pháp.")

# Lưu vào file
with open("graph.json", "w") as f:
    json.dump(graph, f, indent=4)
    print("✅ Đã lưu vào graph.json")
