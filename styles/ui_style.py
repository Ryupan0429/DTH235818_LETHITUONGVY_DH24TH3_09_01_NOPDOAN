import tkinter as tk
from tkinter import ttk, font

# ===================================================================
# FONT CHỮ
# ===================================================================
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 11
FONT_SIZE_TITLE = 12

FONT_NORMAL = (FONT_FAMILY, FONT_SIZE_NORMAL)
FONT_BOLD = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_TITLE = (FONT_FAMILY, FONT_SIZE_TITLE, "bold")
FONT_H1 = (FONT_FAMILY, 16, "bold")
FONT_ICON = (FONT_FAMILY, 11) 

# ===================================================================
# MÀU SẮC
# ===================================================================
BG_MAIN = "#f7fbf8"
BG_TOOLBAR = "#e8f8e9"
BTN_PRIMARY_BG = "#b9e89b"
BTN_DANGER_BG = "#f7c6c6"
BTN_SECONDARY_BG = "#d0d0d0"
BTN_ACCENT_BG = "#e0cfff"

# ===================================================================
# HÀM ÁP DỤNG STYLE
# ===================================================================

def style_ttk(root):
    """Áp dụng style TTK và font chữ toàn cục."""
    
    root.option_add("*Font", FONT_NORMAL)

    s = ttk.Style()
    
    s.configure(".", font=FONT_NORMAL)
    
    s.configure("Treeview", 
                rowheight=28, 
                font=FONT_NORMAL)
    s.configure("Treeview.Heading", 
                font=FONT_BOLD, 
                padding=(5, 8))
    
    s.configure("TCombobox", 
                font=FONT_NORMAL)
    
    s.configure("TNotebook.Tab", 
                font=FONT_BOLD, 
                padding=(10, 5))

# ===================================================================
# HÀM TIỆN ÍCH
# ===================================================================

def create_button(parent, text, command, kind="primary", width=None, font=None):
    """
    Tạo Button với style đơn giản (dùng Tk Button).
    """
    
    if font is None:
        font = FONT_NORMAL

    colors = {
        "primary": BTN_PRIMARY_BG,
        "secondary": BTN_SECONDARY_BG,
        "danger": BTN_DANGER_BG,
        "accent": BTN_ACCENT_BG
    }
    
    btn = tk.Button(
        parent, 
        text=text, 
        command=command, 
        font=font, 
        bg=colors.get(kind, BTN_SECONDARY_BG),
        fg="black",
        relief="flat",
        padx=8,  # Trả về padx
        pady=4,  # Trả về pady
        width=width
    )
    
    btn.bind("<Enter>", lambda e: e.widget.config(relief="solid", bd=1))
    btn.bind("<Leave>", lambda e: e.widget.config(relief="flat", bd=0))
    
    return btn

def center(win, w, h):
    """Căn giữa cửa sổ."""
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = (sw - w)//2, (sh - h)//2
    win.geometry(f"{w}x{h}+{x}+{y}")