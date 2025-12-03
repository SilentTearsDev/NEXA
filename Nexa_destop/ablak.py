import tkinter as tk
import keyboard
window = tk.Tk()
window.title("Nexa Desktop Assistant")
window.configure(bg="black")
window.geometry("1000x500")

# ======================
# FELSŐ RÉSZ (bal panel + chat + cím)
# ======================
top_frame = tk.Frame(window, bg="black")
top_frame.pack(side="top", fill="both", expand=True)

# ---- BAL OLDALI SZÜRKE BOX ----
left_box = tk.Frame(top_frame, bg="#303030", width=140)
left_box.pack(side="left", fill="y")
left_box.pack_propagate(False)

placeholder_label = tk.Label(
    left_box,
    text="N",
    font=("Perfect DOS VGA 437 Win", 72),
    bg="#303030",
    fg="#641e4c"
)
placeholder_label.pack(pady=10)

# ---- JOBB OLDALI TARTALOM (CÍM + CHAT) ----
content_frame = tk.Frame(top_frame, bg="black")
content_frame.pack(side="left", fill="both", expand=True)

# Cím
title = tk.Label(
    content_frame,
    text="Nexa Desktop Assistant",
    bg="black",
    fg="white",
    font=("Perfect DOS VGA 437 Win", 24)
)
title.pack(pady=20)

# CHAT TERÜLET
chat_frame = tk.Frame(content_frame, bg="black")
chat_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

chat_box = tk.Text(
    chat_frame,
    bg="black",
    fg="white",
    font=("Perfect DOS VGA 437 Win", 18),
    relief="flat",
    wrap="word",
    insertbackground="white"
)
chat_box.pack(fill="both", expand=True)

# kezdeti Nexa szöveg
chat_box.insert("end", "NEXA: Hello! I am online.\n")
chat_box.insert("end", "NEXA: How can I assist you today?\n\n")
chat_box.configure(state="disabled")

# ======================
# ALSÓ SZÜRKE TEXTBAR (MINDIG LÁTSZIK)
# ======================
bottom_bar = tk.Frame(window, bg="white", height=70)
bottom_bar.pack(side="bottom", fill="x")

entry_bg = tk.Frame(bottom_bar, bg="#202020")
entry_bg.pack(side="left", fill="x", expand=True, padx=20, pady=12)

entry = tk.Entry(
    entry_bg,
    bg="#202020",
    fg="white",
    font=("Perfect DOS VGA 437 Win", 18),
    relief="flat",
    insertbackground="white"
)
entry.insert(0, "Type your command here...")
entry.pack(fill="x", padx=10, pady=10)

# (opcionális) ENTER-re jelenjen meg a chatben is
def send_message(event):
    text = entry.get().strip()
    if not text:
        return
    chat_box.configure(state="normal")
    chat_box.insert("end", f"YOU: {text}\n")
    chat_box.insert("end", f"NEXA: I received your command: {text}\n\n")
    chat_box.configure(state="disabled")
    chat_box.see("end")
    entry.delete(0, "end")

entry.bind("<Return>", send_message)

window.mainloop()
