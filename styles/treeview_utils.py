import tkinter as tk
from tkinter import ttk, font

try:
    from styles.ui_style import FONT_NORMAL, FONT_BOLD
except ImportError:
    FONT_NORMAL = ("Segoe UI", 11)
    FONT_BOLD = ("Segoe UI", 11, "bold")


def create_treeview_frame(parent):
    """
    Tạo một Frame chứa Treeview và các thanh cuộn.
    Trả về (frame, tree).
    """
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    tree = ttk.Treeview(frame, show="headings")
    
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    return frame, tree

def auto_fit_columns(tree):
    """
    Tự động điều chỉnh độ rộng cột dựa trên
    các font tuple được import từ ui_style.
    """
    
    cell_font = font.Font(font=FONT_NORMAL)
    heading_font = font.Font(font=FONT_BOLD)

    for col in tree["columns"]:
        max_width = 0
        
        heading_text = tree.heading(col, "text")
        if heading_text:
            heading_width = heading_font.measure(heading_text)
            if heading_width > max_width:
                max_width = heading_width
            
        for iid in tree.get_children(""):
            cell_text = tree.set(iid, col)
            if cell_text:
                cell_width = cell_font.measure(cell_text)
                if cell_width > max_width:
                    max_width = cell_width
                    
        tree.column(col, width=max_width + 25, minwidth=50)