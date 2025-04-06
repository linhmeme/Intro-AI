import tkinter as tk
from PIL import Image, ImageTk
import json
import os 

node_coords = {}
node_names = []
node_count = 0

# Hàm vẽ node đã lưu
def draw_existing_nodes():
    global node_count
    for name in node_names:
        x, y = node_coords[name]
        canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
        canvas.create_text(x, y-10, text=name, fill="black")
        node_count += 1

# Hàm click để tạo node mới
def click_event(event):
    global node_count
    if node_count >= 26:
        node_name = chr(97 + (node_count - 26))  # a, b, c, ...
    else:
        node_name = chr(65 + node_count)  # A, B, C, ...
    x, y = event.x, event.y
    canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
    canvas.create_text(x, y-10, text=node_name, fill="black")
    node_coords[node_name] = [x, y]
    node_names.append(node_name)
    node_count += 1
    print(f"{node_name}: ({x}, {y})")

# Hàm lưu file
def save_nodes():
    with open("nodes.json", "w") as f:
        json.dump(node_coords, f, indent=4)
    print("✅ Đã lưu node vào nodes.json")

# Load ảnh bản đồ
map_path = "c:\\Users\\pc11w\\Downloads\\map.png"  
image = Image.open(map_path)

# Load node cũ nếu có
if os.path.exists("nodes.json"):
    with open("nodes.json") as f:
        node_coords = json.load(f)
        node_names = list(node_coords.keys())
        print("📌 Đã load node từ nodes.json")

# Giao diện
root = tk.Tk()
root.title("Chọn Node Trên Bản Đồ")
canvas = tk.Canvas(root, width=image.width, height=image.height)
canvas.pack()
tk_img = ImageTk.PhotoImage(image)
canvas.create_image(0, 0, anchor="nw", image=tk_img)
canvas.bind("<Button-1>", click_event)

# Vẽ node cũ
draw_existing_nodes()

# Nút lưu
save_button = tk.Button(root, text="Lưu Node", command=save_nodes)
save_button.pack()

root.mainloop()
