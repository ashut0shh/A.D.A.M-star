import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
import random

# === CONFIG ===
IMAGE_PATH = r'C:/Users/ashutosh sriram/OneDrive/Desktop/reference.png'
BOARD_SIZE = 300
ROWS, COLS = 3, 3
SNAP_MARGIN = 40

# === Load and Resize Image ===
ref_img = cv2.imread(IMAGE_PATH)
if ref_img is None:
    raise FileNotFoundError("Image not found")
ref_img = cv2.resize(ref_img, (BOARD_SIZE, BOARD_SIZE))
ref_rgb = cv2.cvtColor(ref_img, cv2.COLOR_BGR2RGB)
ref_pil = Image.fromarray(ref_rgb)

tile_w, tile_h = BOARD_SIZE // COLS, BOARD_SIZE // ROWS

# === Tkinter Setup ===
root = tk.Tk()
root.title("Astrix Puzzle")
root.state("zoomed")  # Fullscreen (on Windows)
root.configure(bg="white")

# === Main Layout ===
left_frame = tk.Frame(root, bg="white")
left_frame.pack(side="left", padx=20, pady=20)

right_frame = tk.Frame(root, bg="white")
right_frame.pack(side="left", padx=20)

# === Puzzle Canvas ===
canvas_height = BOARD_SIZE + tile_h * ROWS + 20
canvas = tk.Canvas(left_frame, width=BOARD_SIZE, height=canvas_height, bg="lightgray")
canvas.pack()

# === Puzzle Grid ===
for i in range(ROWS + 1):
    canvas.create_line(0, i * tile_h, BOARD_SIZE, i * tile_h)
    canvas.create_line(i * tile_w, 0, i * tile_w, BOARD_SIZE)

# === Reference Image Display ===
tk.Label(right_frame, text="Reference", font=("Arial", 14), bg="white").pack()
ref_tk = ImageTk.PhotoImage(ref_pil)
tk.Label(right_frame, image=ref_tk).pack(pady=10)

# === Prepare Puzzle Tiles ===
tiles = []
for i in range(ROWS):
    for j in range(COLS):
        box = (j * tile_w, i * tile_h, (j + 1) * tile_w, (i + 1) * tile_h)
        tile_img = ref_pil.crop(box)
        tile = {
            'image': tile_img,
            'correct_pos': (i, j),
            'tk': ImageTk.PhotoImage(tile_img)
        }
        tiles.append(tile)

shuffled = tiles.copy()
random.shuffle(shuffled)

# === Drag and Drop State ===
tile_ids = {}
tile_positions = {}

drag_data = {
    "tile_id": None,
    "offset_x": 0,
    "offset_y": 0,
    "last_mouse": None,
    "shake_distance": 0.0,
    "first_screen_x": 0,
    "first_screen_y": 0
}

# === Coordinate Utilities ===
def grid_to_pixel(row, col):
    return col * tile_w, row * tile_h

def pixel_to_grid(x, y):
    return y // tile_h, x // tile_w

def is_in_board(x, y):
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

# === Mouse Handlers ===
def on_press(event):
    tile_id = canvas.find_closest(event.x, event.y)[0]
    x, y = canvas.coords(tile_id)
    drag_data['tile_id'] = tile_id
    drag_data['offset_x'] = event.x - x
    drag_data['offset_y'] = event.y - y
    drag_data['last_mouse'] = (event.x, event.y)
    drag_data['shake_distance'] = 0.0
    drag_data['first_screen_x'] = event.x_root
    drag_data['first_screen_y'] = event.y_root

def on_motion(event):
    if drag_data['tile_id']:
        x = event.x - drag_data['offset_x']
        y = event.y - drag_data['offset_y']
        canvas.coords(drag_data['tile_id'], x, y)

        current_mouse = (event.x, event.y)
        if drag_data['last_mouse']:
            dx = current_mouse[0] - drag_data['last_mouse'][0]
            dy = current_mouse[1] - drag_data['last_mouse'][1]
            dist = (dx**2 + dy**2) ** 0.5
            drag_data['shake_distance'] += dist
        drag_data['last_mouse'] = current_mouse

def on_release(event):
    if drag_data['tile_id']:
        tile_id = drag_data['tile_id']
        x, y = canvas.coords(tile_id)
        tile_cx, tile_cy = x + tile_w // 2, y + tile_h // 2

        if is_in_board(tile_cx, tile_cy):
            row, col = pixel_to_grid(tile_cx, tile_cy)
            row = max(0, min(ROWS - 1, row))
            col = max(0, min(COLS - 1, col))
            cell_x, cell_y = grid_to_pixel(row, col)
            center_x, center_y = cell_x + tile_w // 2, cell_y + tile_h // 2
            dist = ((tile_cx - center_x) ** 2 + (tile_cy - center_y) ** 2) ** 0.5

            if dist <= SNAP_MARGIN:
                canvas.coords(tile_id, cell_x, cell_y)
                tile_positions[tile_id] = (row, col)
            else:
                tile_positions[tile_id] = None
        else:
            tile_positions[tile_id] = None

        dx = event.x_root - drag_data['first_screen_x']
        dy = event.y_root - drag_data['first_screen_y']
        displacement = (dx ** 2 + dy ** 2) ** 0.5
        shake = drag_data['shake_distance']
        shake_ratio = shake / displacement if displacement != 0 else 0
        print(f"[Tile Drag] Displacement: {displacement:.2f}px | Shake: {shake:.2f}px | Shake Ratio: {shake_ratio:.2f}")

        drag_data['tile_id'] = None
        drag_data['last_mouse'] = None

# === Place Tiles in Tray Area ===
for idx, tile in enumerate(shuffled):
    row = idx // COLS
    col = idx % COLS
    x = col * tile_w
    y = BOARD_SIZE + 10 + row * tile_h
    tile_id = canvas.create_image(x, y, anchor='nw', image=tile['tk'])
    tile_ids[tile_id] = tile
    tile_positions[tile_id] = None
    canvas.tag_bind(tile_id, "<ButtonPress-1>", on_press)
    canvas.tag_bind(tile_id, "<B1-Motion>", on_motion)
    canvas.tag_bind(tile_id, "<ButtonRelease-1>", on_release)

# === Check Button and Label ===
def check_puzzle():
    for tile_id, tile_data in tile_ids.items():
        correct = tile_data['correct_pos']
        current = tile_positions.get(tile_id)
        if current != correct:
            result_label.config(text="❌ Not solved yet", fg="red")
            return
    result_label.config(text="✅ Puzzle solved!", fg="green")

check_btn = tk.Button(left_frame, text="Check Puzzle", font=("Arial", 12), command=check_puzzle)
check_btn.pack(pady=10)

result_label = tk.Label(left_frame, text="", font=("Arial", 12), bg="white")
result_label.pack()

root.mainloop()
                                             