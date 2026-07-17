import customtkinter as ctk
from tkinter import Canvas
import cv2
from PIL import Image, ImageTk, ImageDraw
import mediapipe as mp
import numpy as np
import random
import math

# ==========================
# THEME PALETTES
# ==========================
THEMES = {
    "THANOS": {
        "panel_border": "#6C3FC8",
        "accent": "#F0A830",
        "accent_dim": "#A06A10",
        "glow": "#9B6EE0",
        "btn_fg": "#6C3FC8",
        "btn_hover": "#8A58E8",
        "sky_top": "#0D0D2B",
        "sky_bottom": "#2D1B4E",
        "title": "∞  INFINITY SNAP",
        "subtitle": "Perfectly balanced. As all things should be.",
        "badge_text": "THANOS MODE",
        "action_desc": "Touch thumb + middle finger to ERASE life",
        "status_waiting": "Waiting for snap...",
        "status_active": "⚡ The snap echoes...",
        "status_done": "💀 Half of all life... erased.",
        "particle_colors": ["#D4A017", "#A0522D", "#8B7355", "#C8B560", "#E8C87A"]
    },
    "IRONMAN": {
        "panel_border": "#B31010",
        "accent": "#FFD700",
        "accent_dim": "#B8860B",
        "glow": "#00F0FF",
        "btn_fg": "#B31010",
        "btn_hover": "#E62020",
        "sky_top": "#051329",
        "sky_bottom": "#0A2540",
        "title": "⎊  THE BLIP",
        "subtitle": "And I... am Iron Man.",
        "badge_text": "STARK INDUSTRIES MODE",
        "action_desc": "Touch thumb + middle finger to RESTORE life",
        "status_waiting": "Waiting for blip...",
        "status_active": "🤖 Initializing Nano Gauntlet...",
        "status_done": "❤️ Everyone comes home.",
        "particle_colors": ["#00F0FF", "#39FF14", "#FF007F", "#FFD700", "#FFFFFF"]
    }
}

BG_DARK = "#06060A"
BG_PANEL = "#0E0E16"
BG_CARD = "#141422"
WHITE = "#F0F0F5"
ASH = "#6C6C7C"
RED_SOUL = "#E03131"
GREEN_SOUL = "#2F9E44"

# ==========================
# WINDOW INITIALIZATION
# ==========================
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Cosmic Balance Engine")
app.geometry("1280x760")
app.configure(fg_color=BG_DARK)

app.resizable(True, True)
app.columnconfigure(1, weight=1)
app.rowconfigure(0, weight=1)

current_mode = "THANOS"

# ==========================
# UI LAYOUT
# ==========================
left_panel = ctk.CTkFrame(app, fg_color=BG_PANEL, corner_radius=16, border_width=1, border_color=THEMES[current_mode]["panel_border"])
left_panel.grid(row=0, column=0, padx=(16, 8), pady=16, sticky="nsew")
left_panel.grid_propagate(False)
left_panel.configure(width=320)

title_label = ctk.CTkLabel(left_panel, text=THEMES[current_mode]["title"], font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color=THEMES[current_mode]["accent"])
title_label.pack(pady=(24, 4))

subtitle_label = ctk.CTkLabel(left_panel, text=THEMES[current_mode]["subtitle"], font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"), text_color=ASH, wraplength=260)
subtitle_label.pack(pady=(0, 20))

identity_btn = ctk.CTkButton(left_panel, text="🚀 BECOME IRON MAN", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), fg_color="#B31010", hover_color="#E62020", text_color=WHITE, corner_radius=8, height=40)
identity_btn.pack(fill="x", padx=24, pady=(0, 20))

cam_border = ctk.CTkFrame(left_panel, width=270, height=200, fg_color=BG_DARK, corner_radius=12, border_width=1, border_color=THEMES[current_mode]["panel_border"])
cam_border.pack(pady=(0, 16))
cam_border.pack_propagate(False)

webcam_label = ctk.CTkLabel(cam_border, text="")
webcam_label.place(relx=0.5, rely=0.5, anchor="center")

gesture_card = ctk.CTkFrame(left_panel, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color="#232335")
gesture_card.pack(fill="x", padx=24, pady=(0, 16))

gesture_icon_label = ctk.CTkLabel(gesture_card, text="👋", font=ctk.CTkFont(size=24))
gesture_icon_label.pack(side="left", padx=(16, 12), pady=12)

gesture_text_label = ctk.CTkLabel(gesture_card, text="Show your hand", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=WHITE, anchor="w")
gesture_text_label.pack(fill="x", pady=(10, 2))

gesture_sub_label = ctk.CTkLabel(gesture_card, text=THEMES[current_mode]["action_desc"], font=ctk.CTkFont(family="Segoe UI", size=10), text_color=ASH, anchor="w")
gesture_sub_label.pack(fill="x", pady=(0, 10))

dist_label = ctk.CTkLabel(left_panel, text="NEURAL PINCH PROXIMITY", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=ASH)
dist_label.pack(anchor="w", padx=26, pady=(0, 4))

dist_bar = ctk.CTkProgressBar(left_panel, height=8, corner_radius=4, fg_color="#181826", progress_color=THEMES[current_mode]["glow"])
dist_bar.pack(fill="x", padx=26, pady=(0, 4))
dist_bar.set(0)

dist_value_label = ctk.CTkLabel(left_panel, text="— px", font=ctk.CTkFont(family="Courier New", size=11, weight="bold"), text_color=ASH)
dist_value_label.pack(anchor="e", padx=26, pady=(0, 12))

stats_box = ctk.CTkFrame(left_panel, fg_color="transparent")
stats_box.pack(fill="x", padx=24, pady=10)

def create_metric_node(parent, key_text, initial_val, text_color):
    node = ctk.CTkFrame(parent, fg_color="transparent")
    node.pack(fill="x", pady=3)
    ctk.CTkLabel(node, text=key_text, font=ctk.CTkFont(family="Segoe UI", size=12), text_color=ASH).pack(side="left")
    value_lbl = ctk.CTkLabel(node, text=initial_val, font=ctk.CTkFont(family="Courier New", size=13, weight="bold"), text_color=text_color)
    value_lbl.pack(side="right")
    return value_lbl

total_val = create_metric_node(stats_box, "Total structures", "50", WHITE)
alive_val = create_metric_node(stats_box, "Active objects", "50", GREEN_SOUL)
dusted_val = create_metric_node(stats_box, "Dusted entities", "0", RED_SOUL)
snaps_val = create_metric_node(stats_box, "Gauntlet Activations", "0", THEMES[current_mode]["accent"])

status_label = ctk.CTkLabel(left_panel, text=THEMES[current_mode]["status_waiting"], font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=THEMES[current_mode]["accent"])
status_label.pack(pady=(16, 8))

reset_btn = ctk.CTkButton(left_panel, text="↺  REBUILD MATRIX", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), fg_color=THEMES[current_mode]["btn_fg"], hover_color=THEMES[current_mode]["btn_hover"], text_color=WHITE, corner_radius=8, height=36)
reset_btn.pack(fill="x", padx=24, pady=(0, 20))

right_panel = ctk.CTkFrame(app, fg_color=BG_PANEL, corner_radius=16, border_width=2, border_color=THEMES[current_mode]["panel_border"])
right_panel.grid(row=0, column=1, padx=(8, 16), pady=16, sticky="nsew")
right_panel.columnconfigure(0, weight=1)
right_panel.rowconfigure(1, weight=1)

mode_badge = ctk.CTkLabel(right_panel, text=THEMES[current_mode]["badge_text"], font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=THEMES[current_mode]["accent"])
mode_badge.grid(row=0, column=0, padx=20, pady=12, sticky="w")

snap_count_badge = ctk.CTkLabel(right_panel, text="TOTAL RE-ALIGNMENTS: 0", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), text_color=ASH)
snap_count_badge.grid(row=0, column=0, padx=20, pady=12, sticky="e")

canvas = Canvas(right_panel, bg="#0D0D2B", highlightthickness=0)
canvas.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

# ==========================
# SYSTEM DATA & CACHE STRUCTURE
# ==========================
city_objects = []
active_particles = {}  # Map canvas item ids -> particle details
dissolve_queue = []
dissolve_tick = 0
snapping_active = False
snap_count = 0
snap_ready = False
no_hand_frame_count = 0

sky_rectangles = []
star_ids = []
planet_id = None
ground_ids = []

# Generate dataset schema
for _ in range(50):
    city_objects.append({
        "type": random.choice(["house", "house", "tree", "tree", "skyscraper"]),
        "x_pct": random.uniform(0.02, 0.94),
        "y_pct": random.uniform(0.42, 0.78),
        "alive": True,
        "scale": random.uniform(0.75, 1.25),
        "canvas_ids": []  # Holds canvas vector handles
    })
# Sort layout back-to-front by depth mapping
city_objects.sort(key=lambda o: o["y_pct"])

# ==========================
# CACHED GRAPHICS PIPELINE (HIGH SPEED)
# ==========================
def build_static_environment():
    """Calculates coordinates, paints background elements and city elements only once."""
    global planet_id, ground_ids
    canvas.delete("all")
    sky_rectangles.clear()
    star_ids.clear()
    ground_ids.clear()
    
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w < 10 or h < 10:
        return

    theme = THEMES[current_mode]
    steps = 16  # Balanced background segments
    for i in range(steps):
        t = i / steps
        r = int(int(theme["sky_top"][1:3], 16) * (1 - t) + int(theme["sky_bottom"][1:3], 16) * t)
        g = int(int(theme["sky_top"][3:5], 16) * (1 - t) + int(theme["sky_bottom"][3:5], 16) * t)
        b = int(int(theme["sky_top"][5:7], 16) * (1 - t) + int(theme["sky_bottom"][5:7], 16) * t)
        seg_id = canvas.create_rectangle(0, int(i * h / steps), w, int((i + 1) * h / steps), fill=f"#{r:02x}{g:02x}{b:02x}", outline="")
        sky_rectangles.append((seg_id, i / steps))

    # Static Stars matrix
    random.seed(1138)
    for _ in range(60):
        sx, sy = random.randint(0, w), random.randint(0, int(h * 0.4))
        r = random.uniform(0.6, 1.8)
        star_ids.append(canvas.create_oval(sx-r, sy-r, sx+r, sy+r, fill="#FFFFFF", outline=""))

    planet_id = canvas.create_oval(w - 140, 40, w - 60, 120, fill="#F5F3E7", outline="#FFFFFF", width=1)
    ground_y = int(h * 0.82)
    ground_ids.append(canvas.create_rectangle(0, ground_y, w, h, fill="#120D1A", outline=""))
    ground_ids.append(canvas.create_rectangle(0, ground_y - 4, w, ground_y + 12, fill="#1F1A2E", outline=""))

    # Spawn and paint structural geometry onto layout
    for obj in city_objects:
        obj["canvas_ids"].clear()
        ox = int(obj["x_pct"] * w)
        oy = int(obj["y_pct"] * h)
        sc = obj["scale"]

        if obj["type"] == "house":
            bw, bh = int(50 * sc), int(45 * sc)
            w_id = canvas.create_rectangle(ox, oy, ox+bw, oy+bh, fill="#BA6629", outline="#2B1D15")
            r_id = canvas.create_polygon(ox-4, oy, ox + (bw//2), oy-int(28*sc), ox+bw+4, oy, fill="#941C1C", outline="#3B1010")
            d_id = canvas.create_rectangle(ox+int(bw*0.35), oy+int(bh*0.4), ox+int(bw*0.65), oy+bh, fill="#3D2114", outline="")
            w1_id = canvas.create_rectangle(ox+int(bw*0.1), oy+int(bh*0.15), ox+int(bw*0.3), oy+int(bh*0.35), fill="#FFE066", outline="")
            w2_id = canvas.create_rectangle(ox+int(bw*0.7), oy+int(bh*0.15), ox+int(bw*0.9), oy+int(bh*0.35), fill="#FFE066", outline="")
            obj["canvas_ids"].extend([w_id, r_id, d_id, w1_id, w2_id])

        elif obj["type"] == "tree":
            tw, th = int(10 * sc), int(35 * sc)
            t_id = canvas.create_rectangle(ox + int(10*sc), oy, ox + int(10*sc) + tw, oy + th, fill="#5C3818", outline="")
            l1_id = canvas.create_oval(ox, oy - int(15*sc), ox + int(30*sc), oy + int(15*sc), fill="#1E6B27", outline="")
            l2_id = canvas.create_oval(ox + int(5*sc), oy - int(25*sc), ox + int(25*sc), oy, fill="#1E6B27", outline="")
            obj["canvas_ids"].extend([t_id, l1_id, l2_id])

        elif obj["type"] == "skyscraper":
            sw, sh = int(45 * sc), int(120 * sc)
            h_id = canvas.create_rectangle(ox, oy-sh, ox+sw, oy, fill="#25334D", outline="#141E30")
            obj["canvas_ids"].append(h_id)
            for wy in range(oy-sh+8, oy-10, int(16*sc)):
                for wx in [ox+int(6*sc), ox+int(18*sc), ox+int(30*sc)]:
                    w_color = "#66E0FF" if current_mode == "IRONMAN" else "#FFD666"
                    wc = w_color if random.random() > 0.4 else "#0F1622"
                    win_id = canvas.create_rectangle(wx, wy, wx+int(8*sc), wy+int(10*sc), fill=wc, outline="")
                    obj["canvas_ids"].append(win_id)
        
        # Apply current state logic instantly
        refresh_object_visual_state(obj)

def refresh_object_visual_state(obj):
    """Dynamically applies color states or hides objects without deleting vector elements."""
    alive = obj["alive"]
    if obj["type"] == "house":
        c_wall = "#BA6629" if alive else "#3D312A"
        c_roof = "#941C1C" if alive else "#471D1D"
        c_win = "#FFE066" if alive else "#1E1E26"
        if len(obj["canvas_ids"]) >= 5:
            canvas.itemconfig(obj["canvas_ids"][0], fill=c_wall)
            canvas.itemconfig(obj["canvas_ids"][1], fill=c_roof)
            canvas.itemconfig(obj["canvas_ids"][2], fill="#3D2114" if alive else "#1A100C")
            canvas.itemconfig(obj["canvas_ids"][3], fill=c_win)
            canvas.itemconfig(obj["canvas_ids"][4], fill=c_win)
            
    elif obj["type"] == "tree":
        c_trunk = "#5C3818" if alive else "#24180E"
        c_leaves = "#1E6B27" if alive else "#1A261C"
        if len(obj["canvas_ids"]) >= 3:
            canvas.itemconfig(obj["canvas_ids"][0], fill=c_trunk)
            canvas.itemconfig(obj["canvas_ids"][1], fill=c_leaves)
            canvas.itemconfig(obj["canvas_ids"][2], fill=c_leaves)
            
    elif obj["type"] == "skyscraper":
        c_hull = "#25334D" if alive else "#151B26"
        if obj["canvas_ids"]:
            canvas.itemconfig(obj["canvas_ids"][0], fill=c_hull)
            w_color = "#66E0FF" if current_mode == "IRONMAN" else "#FFD666"
            for win_id in obj["canvas_ids"][1:]:
                canvas.itemconfig(win_id, fill=w_color if (alive and random.random() > 0.3) else "#090D14")

def trigger_ambient_sky_refresh():
    """Efficiently scales background palette without creating garbage collectors."""
    theme = THEMES[current_mode]
    for seg_id, t in sky_rectangles:
        r = int(int(theme["sky_top"][1:3], 16) * (1 - t) + int(theme["sky_bottom"][1:3], 16) * t)
        g = int(int(theme["sky_top"][3:5], 16) * (1 - t) + int(theme["sky_bottom"][3:5], 16) * t)
        b = int(int(theme["sky_top"][5:7], 16) * (1 - t) + int(theme["sky_bottom"][5:7], 16) * t)
        canvas.itemconfig(seg_id, fill=f"#{r:02x}{g:02x}{b:02x}")

def dynamic_particle_injection(x, y, colors, count=12):
    """Injects fast tracking items directly into canvas subsystem memory."""
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 4.5)
        sz = random.randint(2, 5)
        p_id = canvas.create_oval(x-sz, y-sz, x+sz, y+sz, fill=random.choice(colors), outline="")
        active_particles[p_id] = {
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed - random.uniform(1, 3),
            "life": random.randint(15, 30),
            "size": sz
        }

# ==========================
# LOGIC CONTROLLER MATRIX
# ==========================
def execute_cosmic_shift():
    global snapping_active, snap_count
    if snapping_active:
        return

    if current_mode == "THANOS":
        targets = [o for o in city_objects if o["alive"]]
        if not targets: return
        random.shuffle(targets)
        targets = targets[:max(1, len(targets) // 2)]
    else:
        targets = [o for o in city_objects if not o["alive"]]
        if not targets: return
        random.shuffle(targets)

    snapping_active = True
    snap_count += 1
    
    w, h = canvas.winfo_width(), canvas.winfo_height()
    spread_interval = max(1, 60 // len(targets))
    
    for idx, obj in enumerate(targets):
        dissolve_queue.append((dissolve_tick + (idx * spread_interval), obj))

    snap_count_badge.configure(text=f"TOTAL RE-ALIGNMENTS: {snap_count}")
    snaps_val.configure(text=str(snap_count))
    status_label.configure(text=THEMES[current_mode]["status_active"], text_color="#FF5505")
    gesture_icon_label.configure(text="⚡")
    gesture_text_label.configure(text="ACTIVATED!")
    gesture_sub_label.configure(text="The timeline rearranges...")

def update_simulation_loop():
    global dissolve_tick, snapping_active
    dissolve_tick += 1
    w = canvas.winfo_width()
    h = canvas.winfo_height()

    active_dissolves = False
    still_pending = []

    for (tick, obj) in dissolve_queue:
        if dissolve_tick >= tick:
            obj["alive"] = (current_mode == "IRONMAN")
            refresh_object_visual_state(obj)
            cx = int(obj["x_pct"] * w) + 20
            cy = int(obj["y_pct"] * h) - 10
            dynamic_particle_injection(cx, cy, THEMES[current_mode]["particle_colors"])
            active_dissolves = True
        else:
            still_pending.append((tick, obj))
    dissolve_queue[:] = still_pending

    # Performance Optimized Metric Refresher
    if active_dissolves or dissolve_tick % 10 == 0:
        total = len(city_objects)
        alive = len([o for o in city_objects if o["alive"]])
        dusted = total - alive
        alive_val.configure(text=str(alive))
        dusted_val.configure(text=str(dusted))

    if active_dissolves and not dissolve_queue:
        status_label.configure(text=THEMES[current_mode]["status_done"], text_color=THEMES[current_mode]["accent"])
        gesture_icon_label.configure(text="❤️" if current_mode == "IRONMAN" else "💀")
        gesture_text_label.configure(text="Completed")
        gesture_sub_label.configure(text="Balance restabilized.")
        snapping_active = False

    # Low Overhead Particle Pipeline (Updates positions instead of deleting/creating)
    dead_particles = []
    for p_id, p in active_particles.items():
        p["vy"] += 0.15
        p["vx"] *= 0.96
        canvas.move(p_id, p["vx"], p["vy"])
        p["life"] -= 1
        if p["life"] <= 0:
            dead_particles.append(p_id)

    for p_id in dead_particles:
        canvas.delete(p_id)
        del active_particles[p_id]

    app.after(20, update_simulation_loop)

# ==========================
# THEME TRANSITION CONTROLLER
# ==========================
def toggle_cosmic_alignment():
    global current_mode, snap_ready
    current_mode = "IRONMAN" if current_mode == "THANOS" else "THANOS"
    theme = THEMES[current_mode]
    
    left_panel.configure(border_color=theme["panel_border"])
    right_panel.configure(border_color=theme["panel_border"])
    title_label.configure(text=theme["title"], text_color=theme["accent"])
    subtitle_label.configure(text=theme["subtitle"])
    cam_border.configure(border_color=theme["panel_border"])
    mode_badge.configure(text=theme["badge_text"], text_color=theme["accent"])
    dist_bar.configure(progress_color=theme["glow"])
    status_label.configure(text=theme["status_waiting"], text_color=theme["accent"])
    reset_btn.configure(fg_color=theme["btn_fg"], hover_color=theme["btn_hover"])
    snaps_val.configure(text_color=theme["accent"])
    
    if current_mode == "IRONMAN":
        identity_btn.configure(text="🔮 BECOME THANOS", fg_color="#6C3FC8", hover_color="#8A58E8")
    else:
        identity_btn.configure(text="🚀 BECOME IRON MAN", fg_color="#B31010", hover_color="#E62020")
        
    snap_ready = False
    gesture_icon_label.configure(text="👋")
    gesture_text_label.configure(text="Show your hand")
    gesture_sub_label.configure(text=theme["action_desc"])
    gesture_card.configure(border_color="#232335")
    
    trigger_ambient_sky_refresh()
    for obj in city_objects:
        refresh_object_visual_state(obj)

identity_btn.configure(command=toggle_cosmic_alignment)

def clean_reset():
    global snap_count, snapping_active, snap_ready
    snap_count = 0
    for p_id in list(active_particles.keys()):
        canvas.delete(p_id)
    active_particles.clear()
    dissolve_queue.clear()
    snapping_active = False
    snap_ready = False
    
    for obj in city_objects:
        obj["alive"] = True
        
    snap_count_badge.configure(text="TOTAL RE-ALIGNMENTS: 0")
    snaps_val.configure(text="0")
    status_label.configure(text=THEMES[current_mode]["status_waiting"], text_color=THEMES[current_mode]["accent"])
    
    trigger_ambient_sky_refresh()
    for obj in city_objects:
        refresh_object_visual_state(obj)

reset_btn.configure(command=clean_reset)

# ==========================
# COMPUTER VISION PROCESSOR
# ==========================
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.65, min_tracking_confidence=0.65)
cap = cv2.VideoCapture(0)

# Low-overhead frame counter downsampler
cv_frame_drop_counter = 0

def capture_stream_processor():
    global snap_ready, no_hand_frame_count, cv_frame_drop_counter
    success, frame = cap.read()
    if not success:
        app.after(20, capture_stream_processor)
        return

    cv_frame_drop_counter += 1
    # Process computer vision detection math every alternate frame to maximize CPU threading efficiency
    if cv_frame_drop_counter % 2 == 0:
        frame = cv2.flip(frame, 1)
        fh, fw, _ = frame.shape
        rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        analysis_results = hands_detector.process(rgb_img)
        
        hand_in_frame = False

        if analysis_results.multi_hand_landmarks:
            for hand_landmarks in analysis_results.multi_hand_landmarks:
                hand_in_frame = True
                no_hand_frame_count = 0
                
                t_tip = hand_landmarks.landmark[4]
                m_tip = hand_landmarks.landmark[12]
                
                t_vector = np.array([t_tip.x * fw, t_tip.y * fh])
                m_vector = np.array([m_tip.x * fw, m_tip.y * fh])
                spatial_distance = np.linalg.norm(t_vector - m_vector)
                
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style()
                )
                
                normalized_bar_val = max(0.0, min(1.0, spatial_distance / 180.0))
                dist_bar.set(normalized_bar_val)
                dist_value_label.configure(text=f"{int(spatial_distance)} px")
                
                theme = THEMES[current_mode]
                if spatial_distance < 35:
                    dist_bar.configure(progress_color=theme["accent"])
                elif spatial_distance < 75:
                    dist_bar.configure(progress_color="#FF5505")
                else:
                    dist_bar.configure(progress_color=theme["glow"])

                if spatial_distance < 24:
                    if not snap_ready:
                        snap_ready = True
                        gesture_icon_label.configure(text="🤌")
                        gesture_text_label.configure(text="Quantum Lock Ready")
                        gesture_sub_label.configure(text="Release fingers to activate")
                        gesture_card.configure(border_color=theme["accent"])
                        
                if snap_ready and spatial_distance > 60:
                    snap_ready = False
                    execute_cosmic_shift()
        else:
            no_hand_frame_count += 1
            if no_hand_frame_count > 8:
                dist_bar.set(0)
                dist_value_label.configure(text="— px")
                if not snap_ready and not snapping_active:
                    gesture_icon_label.configure(text="👋")
                    gesture_text_label.configure(text="System Searching...")
                    gesture_sub_label.configure(text=THEMES[current_mode]["action_desc"])
                    gesture_card.configure(border_color="#232335")

        # Process video panel image conversions smoothly
        converted_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((266, 196))
        rounded_alpha_mask = Image.new("L", converted_pil.size, 0)
        ImageDraw.Draw(rounded_alpha_mask).rounded_rectangle([0, 0, *converted_pil.size], radius=10, fill=255)
        converted_pil.putalpha(rounded_alpha_mask)
        
        tk_img = ImageTk.PhotoImage(converted_pil)
        webcam_label.configure(image=tk_img)
        webcam_label.image = tk_img
    
    app.after(15, capture_stream_processor)

# ==========================
# SYSTEM COLD START
# ==========================
canvas.bind("<Configure>", lambda e: build_static_environment())
capture_stream_processor()
update_simulation_loop()

app.mainloop()
cap.release()
