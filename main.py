import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox, ttk
import json
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont
from style import light, dark

theme = light
current_letter = None
image_label = None
visits = {}

RUSSIAN_ALPHABET = list("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")


def load_visits():
    try:
        with open("visits.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {letter: 0 for letter in RUSSIAN_ALPHABET}


def save_visits():
    with open("visits.json", "w", encoding="utf-8") as f:
        json.dump(visits, f)


def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл data.json не найден!")
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Ошибка", "Ошибка в формате файла data.json!")
        return {}


def change_theme():
    global theme
    theme = dark if theme == light else light
    update_theme()


def create_placeholder_image(letter, text, size=(400, 280)):
    img = Image.new("RGB", size, color="white")
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        r = int(255 - (100 * y / size[1]))
        g = int(50 + (150 * y / size[1]))
        b = int(200 - (50 * y / size[1]))
        for x in range(size[0]):
            wave = int(20 * (1 + 0.5 * (x / size[0])))
            draw.point((x, y), fill=(min(255, r + wave), min(255, g), min(255, b)))
    try:
        font_large = ImageFont.truetype("arial.ttf", 50)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    for offset in range(3, 0, -1):
        draw.text(
            (size[0] // 2 - 15 + offset, 15 + offset),
            letter,
            fill=(50, 50, 50),
            font=font_large,
        )
    draw.text((size[0] // 2 - 15, 15), letter, fill="white", font=font_large)
    meme_name = (
        text.split(" — ")[0]
        if " — " in text
        else (
            text.split()[0] + " " + text.split()[1]
            if len(text.split()) > 1
            else text.split()[0]
        )
    )
    name_x = max(5, (size[0] - len(meme_name) * 8) // 2)
    draw.text((name_x + 2, 77), meme_name, fill="black", font=font_medium)
    draw.text((name_x, 75), meme_name, fill="yellow", font=font_medium)
    words = text.split()
    if len(words) > 8:
        short_text = " ".join(words[3:8]) + "..."
    else:
        short_text = " ".join(words[3:]) if len(words) > 3 else "Мем"
    lines = []
    current_line = ""
    for word in short_text.split():
        if len(current_line + word) < 28:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    y_offset = 105
    for line in lines[:3]:
        line_x = max(5, (size[0] - len(line) * 6) // 2)
        draw.text((line_x + 1, y_offset + 1), line, fill="black", font=font_small)
        draw.text((line_x, y_offset), line, fill="white", font=font_small)
        y_offset += 16
    for i in range(3):
        colors = ["#FF1493", "#00FFFF", "#FFFF00"]
        draw.rectangle(
            (i, i, size[0] - i - 1, size[1] - i - 1), outline=colors[i], width=1
        )
    draw.text((11, size[1] - 24), "НЕТ ИЗОБРАЖЕНИЯ", fill="black", font=font_small)
    draw.text((10, size[1] - 25), "НЕТ ИЗОБРАЖЕНИЯ", fill="#FF1493", font=font_small)
    return img


def setup_images_folder():
    if not os.path.exists("images"):
        os.makedirs("images")


def check_image_exists(image_path):
    if not image_path:
        return False
    base_path = os.path.splitext(image_path)[0]
    extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]
    for ext in extensions:
        full_path = base_path + ext
        if os.path.exists(full_path):
            return full_path
    return False


def update_theme():
    win.config(bg=theme["bg"])
    text.config(bg=theme["bg"], fg=theme["fg"])
    image_frame.config(bg=theme["bg"])
    stats_label.config(bg=theme["bg"], fg=theme["fg"])
    for letter, btn in buttons.items():
        if letter == current_letter:
            btn.config(bg=theme["btn_active"], fg=theme["btn_active_fg"])
        else:
            btn.config(bg=theme["btn_bg"], fg=theme["fg"])
    theme_btn.config(bg=theme["btn_bg"], fg=theme["fg"])
    buttons_frame.config(bg=theme["bg"])
    if image_label:
        image_label.config(bg=theme["bg"])
    style = ttk.Style()
    style.configure("TFrame", background=theme["bg"])
    style.configure("TPanedwindow", background=theme["bg"])
    left_canvas.config(bg="white", highlightbackground="white")
    content_frame.config(style="TFrame")


def show_letter(letter):
    global current_letter, image_label
    current_letter = letter
    for btn_letter, btn in buttons.items():
        if btn_letter == letter:
            btn.config(bg=theme["btn_active"], fg=theme["btn_active_fg"])
        else:
            btn.config(bg=theme["btn_bg"], fg=theme["fg"])
    entry_text = data.get(letter, {}).get("text", "Нет информации.")
    text.delete(1.0, tk.END)
    text.insert(tk.END, f"{letter}:\n{entry_text}")
    image_path = data.get(letter, {}).get("image", "")
    if image_label:
        image_label.destroy()
    actual_image_path = check_image_exists(image_path)
    if actual_image_path:
        try:
            img = Image.open(actual_image_path)
            img = img.resize((400, 280), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            image_label = tk.Label(image_frame, image=photo, bg=theme["bg"])
            image_label.image = photo
            image_label.pack()
        except Exception:
            placeholder = create_placeholder_image(letter, entry_text)
            photo = ImageTk.PhotoImage(placeholder)
            image_label = tk.Label(image_frame, image=photo, bg=theme["bg"])
            image_label.image = photo
            image_label.pack()
    else:
        placeholder = create_placeholder_image(letter, entry_text)
        photo = ImageTk.PhotoImage(placeholder)
        image_label = tk.Label(image_frame, image=photo, bg=theme["bg"])
        image_label.image = photo
        image_label.pack()
    visits[letter] += 1
    save_visits()
    update_stats()
    update_plot()


def on_button_hover(event, letter):
    if letter != current_letter:
        event.widget.config(bg=theme["btn_hover"])


def on_button_leave(event, letter):
    if letter != current_letter:
        event.widget.config(bg=theme["btn_bg"])


def update_stats():
    total = sum(visits.values())
    most_visited = max(visits.items(), key=lambda x: x[1])
    stats_label.config(
        text=f"Всего посещений: {total} | Самая популярная: {most_visited[0]} ({most_visited[1]})"
    )


def update_plot():
    ax.clear()
    letters = RUSSIAN_ALPHABET
    values = [visits.get(letter, 0) for letter in letters]
    bars = ax.bar(letters, values, color="#66ccff")
    ax.set_title("История посещений букв", fontsize=10, pad=5)
    ax.tick_params(axis="x", rotation=90, labelsize=6)
    ax.tick_params(axis="y", labelsize=6)
    ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 5)
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=6,
            )
    fig.tight_layout()
    plot_canvas.draw()


data = load_data()
visits = load_visits()

win = tk.Tk()
win.title("МЕМОПЕДИЯ 2025")
win.geometry("900x700")

style = ttk.Style()
style.configure("TFrame", background="white")
style.configure("TPanedwindow", background="white")

main_paned = ttk.PanedWindow(win, orient=tk.HORIZONTAL)
main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

left_frame = ttk.Frame(main_paned, style="TFrame")
main_paned.add(left_frame, weight=3)

right_frame = ttk.Frame(main_paned)
main_paned.add(right_frame, weight=1)

left_canvas = tk.Canvas(left_frame, bg="white", highlightbackground="white")
scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=left_canvas.yview)
content_frame = ttk.Frame(left_canvas, style="TFrame")

content_frame.bind(
    "<Configure>", lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
)

left_canvas.create_window((0, 0), window=content_frame, anchor="nw")
left_canvas.configure(yscrollcommand=scrollbar.set)

left_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

header = tk.Label(
    content_frame, text="МЕМОПЕДИЯ", font=("Impact", 28), fg="#000000", bg="white"
)
header.pack(pady=10)

stats_label = tk.Label(content_frame, text="", font=("Arial", 10), bg="white")
stats_label.pack()

setup_images_folder()

text = tk.Text(content_frame, wrap="word", font=("Arial", 14), height=5, bg="white")
text.pack(pady=5, fill=tk.X, padx=10)

image_frame = tk.Frame(content_frame, bg="white")
image_frame.pack(pady=5)

buttons_frame = tk.Frame(content_frame, bg="white")
buttons_frame.pack(pady=5)

buttons = {}
row = 0
col = 0
for letter in RUSSIAN_ALPHABET:
    if letter not in visits:
        visits[letter] = 0
    if letter in data:
        b = tk.Button(
            buttons_frame,
            text=letter,
            width=3,
            height=2,
            font=("Arial", 12, "bold"),
            command=lambda l=letter: show_letter(l),
            relief="raised",
            borderwidth=2,
        )
        b.grid(row=row, column=col, padx=2, pady=2)
        b.bind("<Enter>", lambda event, l=letter: on_button_hover(event, l))
        b.bind("<Leave>", lambda event, l=letter: on_button_leave(event, l))
        buttons[letter] = b
        col += 1
        if col > 10:
            col = 0
            row += 1

theme_btn = tk.Button(
    content_frame,
    text="🌙 Сменить тему",
    command=change_theme,
    font=("Arial", 11),
    padx=15,
    pady=5,
    bg="white",
)
theme_btn.pack(pady=5)

graph_frame = ttk.Frame(right_frame)
graph_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

fig = plt.Figure(figsize=(4, 6), dpi=70)
ax = fig.add_subplot(111)
plot_canvas = FigureCanvasTkAgg(fig, master=graph_frame)
plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

update_theme()
show_letter(RUSSIAN_ALPHABET[0])
update_stats()

win.protocol("WM_DELETE_WINDOW", lambda: [save_visits(), win.destroy()])
win.mainloop()
