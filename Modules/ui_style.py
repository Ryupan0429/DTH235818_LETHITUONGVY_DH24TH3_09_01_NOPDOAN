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

# ===================================================================
# MÀU SẮC
# ===================================================================
BG_MAIN = "#f7fbf8"
BG_TOOLBAR = "#e8f8e9"
BTN_PRIMARY_BG = "#b9e89b"
BTN_DANGER_BG = "#f7c6c6"
BTN_SECONDARY_BG = "#d0d0d0"
BTN_ACCENT_BG = "#e0cfff"

# =Dùng màu của ttk thay vì định nghĩa màu riêng
# ===================================================================
# HÀM ÁP DỤNG STYLE
# ===================================================================

def style_ttk(root):
    """Áp dụng style TTK và font chữ toàn cục."""
    
    root.option_add("*Font", FONT_NORMAL)

    s = ttk.Style()
    s.theme_use('vista') # Dùng theme 'vista' hoặc 'xpnative' cho đẹp
    
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
    
    # Định nghĩa các style cho Button
    s.configure("Primary.TButton", font=FONT_BOLD, background=BTN_PRIMARY_BG)
    s.map("Primary.TButton", background=[('active', '#9cd475')])
    
    s.configure("Danger.TButton", font=FONT_NORMAL, background=BTN_DANGER_BG)
    s.map("Danger.TButton", background=[('active', '#f5a8a8')])
    
    s.configure("Accent.TButton", font=FONT_NORMAL, background=BTN_ACCENT_BG)
    s.map("Accent.TButton", background=[('active', '#c9a3ff')])

# ===================================================================
# HÀM TIỆN ÍCH
# ===================================================================

def create_button(parent, text, command, kind="secondary", width=None, style=None):
    """
    Tạo Button (sử dụng ttk.Button).
    """
    
    style_map = {
        "primary": "Primary.TButton",
        "danger": "Danger.TButton",
        "accent": "Accent.TButton",
        "secondary": "TButton" # Mặc định của TButton
    }
    
    style_to_use = style_map.get(kind, "TButton")
    if style:
        style_to_use = style

    btn = ttk.Button(
        parent, 
        text=text, 
        command=command, 
        width=width,
        style=style_to_use
    )
    return btn

def center(win, w, h):
    """Căn giữa cửa sổ."""
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x, y = (sw - w)//2, (sh - h)//2
    win.geometry(f"{w}x{h}+{x}+{y}")