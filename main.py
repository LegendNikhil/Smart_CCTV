import tkinter as tk
import tkinter.font as font
from in_out import in_out
from motion import noise
from rect_noise import rect_noise
from record import record
from PIL import Image, ImageTk, ImageEnhance
from find_motion import find_motion
from identify import maincall
import os

# --- Pillow resample compatibility ---
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = getattr(Image, "LANCZOS", Image.ANTIALIAS)

# --- Constants (base sizes) ---
BASE_WINDOW_W, BASE_WINDOW_H = 1080, 700
BASE_ICON_SIZE = (160, 160)
BASE_BTN_IMG_SIZE = (48, 48)
BASE_BTN_FONT_SIZE = 22
MIN_BTN_IMG = 24
MIN_ICON = 80
MIN_FONT = 9

def open_pil(path):
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGBA")
    # Add light neon glow around icons
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.35)
    return img

# --- Create Tk window ---
window = tk.Tk()
window.title("Smart CCTV - CV & ML")
try:
    window.iconphoto(False, tk.PhotoImage(file='mn.png'))
except Exception:
    pass

window.geometry(f'{BASE_WINDOW_W}x{BASE_WINDOW_H}')
window.configure(bg="#0A0F17")   # Futuristic dark background

# --- Main frame ---
frame1 = tk.Frame(window, padx=12, pady=12, bg="#0A0F17")
frame1.pack(fill='both', expand=True)

# Grid config
for c in range(3):
    frame1.columnconfigure(c, weight=1, uniform='col')

for r in range(6):
    frame1.rowconfigure(r, weight=1)

# --- Title ---
label_title = tk.Label(
    frame1,
    text="SMART CCTV",
    fg="#00E5FF",
    bg="#0A0F17"
)

label_font = font.Font(size=BASE_BTN_FONT_SIZE + 12, weight='bold', family='Helvetica')
label_title['font'] = label_font
label_title.grid(row=0, column=0, columnspan=3, sticky='n', pady=(10, 12))

# Neon underline effect
underline = tk.Frame(frame1, bg="#00E5FF", height=2)
underline.grid(row=0, column=0, columnspan=3, sticky="s", pady=(0, 4))

# --- Load images ---
pil_images = {
    'icon': open_pil('icons/spy.png'),
    'btn1': open_pil('icons/lamp.png'),
    'btn2': open_pil('icons/rectangle-of-cutted-line-geometrical-shape.png'),
    'btn3': open_pil('icons/security-camera.png'),
    'btn4': open_pil('icons/recording.png'),
    'btn5': open_pil('icons/exit.png'),
    'btn6': open_pil('icons/incognito.png'),
    'btn7': open_pil('icons/rec.png'),
}

def mk_photo(pil_img, size):
    if pil_img is None:
        return None
    if size[0] < 1 or size[1] < 1:
        size = (1, 1)
    return ImageTk.PhotoImage(pil_img.resize(size, RESAMPLE))

tk_images = {}

# --- Icon ---
icon_photo = mk_photo(pil_images['icon'], BASE_ICON_SIZE)
label_icon = tk.Label(frame1, image=icon_photo, bg="#0A0F17")
label_icon.image = icon_photo
label_icon.grid(row=1, column=0, columnspan=3, pady=(5, 18))

# --- Button styling ---
button_style = {
    "bg": "#101722",
    "fg": "#E6F0FF",
    "activebackground": "#152233",
    "activeforeground": "#00E5FF",
    "relief": "flat",
    "bd": 0,
    "highlightthickness": 2,
    "highlightcolor": "#00E5FF",
    "highlightbackground": "#00E5FF",
    "justify": "left",
    "compound": "left",
    "padx": 10
}

btn_font = font.Font(size=BASE_BTN_FONT_SIZE, weight="bold")

def neon_hover_in(event):
    event.widget.config(highlightcolor="#00FF9C", highlightbackground="#00FF9C")

def neon_hover_out(event):
    event.widget.config(highlightcolor="#00E5FF", highlightbackground="#00E5FF")

def build_button(parent, text, cmd, row, col):
    btn = tk.Button(parent, text=text, command=cmd)
    btn.configure(**button_style)
    btn['font'] = btn_font
    btn.grid(row=row, column=col, sticky='nsew', padx=8, pady=8)

    btn.bind("<Enter>", neon_hover_in)
    btn.bind("<Leave>", neon_hover_out)

    return btn

# Buttons
buttons = {}
buttons['btn1'] = build_button(frame1, "Monitor", find_motion, 2, 0)
buttons['btn7'] = build_button(frame1, "Identify", maincall, 2, 1)
buttons['btn2'] = build_button(frame1, "Rectangle", rect_noise, 2, 2)
buttons['btn3'] = build_button(frame1, "Noise", noise, 3, 0)
buttons['btn6'] = build_button(frame1, "In / Out", in_out, 3, 1)
buttons['btn4'] = build_button(frame1, "Record", record, 3, 2)
buttons['btn5'] = build_button(frame1, "Exit", window.quit, 4, 1)

# --- Resize handler ---
def on_resize(event=None):
    w = max(200, frame1.winfo_width())
    h = max(200, frame1.winfo_height())

    scale = min(w / BASE_WINDOW_W, h / BASE_WINDOW_H)

    icon_w = max(MIN_ICON, int(BASE_ICON_SIZE[0] * scale))
    icon_h = max(MIN_ICON, int(BASE_ICON_SIZE[1] * scale))
    btn_img_w = max(MIN_BTN_IMG, int(BASE_BTN_IMG_SIZE[0] * scale))
    btn_img_h = max(MIN_BTN_IMG, int(BASE_BTN_IMG_SIZE[1] * scale))

    if pil_images['icon']:
        new_icon = mk_photo(pil_images['icon'], (icon_w, icon_h))
        label_icon.configure(image=new_icon)
        label_icon.image = new_icon

    for key, btn in buttons.items():
        if key in pil_images and pil_images[key] is not None:
            new_img = mk_photo(pil_images[key], (btn_img_w, btn_img_h))
            tk_images[key] = new_img
            btn.configure(image=new_img)
            btn.image = new_img

    try:
        label_font.configure(size=max(MIN_FONT, int((BASE_BTN_FONT_SIZE + 12) * scale)))
        btn_font.configure(size=max(MIN_FONT, int(BASE_BTN_FONT_SIZE * scale)))
    except:
        pass

frame1.bind('<Configure>', on_resize)
window.minsize(640, 460)
window.mainloop()
