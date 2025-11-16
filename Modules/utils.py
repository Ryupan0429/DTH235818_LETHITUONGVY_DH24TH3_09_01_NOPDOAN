import tkinter as tk
from tkinter import ttk
import re 

def create_treeview_frame(parent):
    # Tạo một Frame chứa Treeview và các thanh cuộn.
    frame = tk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    tree = ttk.Treeview(frame, show="headings", selectmode="extended")
    
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    return frame, tree

# ===================================================================
# TIỆN ÍCH SORT CHO TREEVIEW
# ===================================================================

def setup_sortable_treeview(tree, columns_info, sort_state_ref):
    # Thiết lập tiêu đề và lệnh sort cho Treeview.
    tree["columns"] = list(columns_info.keys())
    for col_id, header_text in columns_info.items():
        tree.heading(col_id, text=header_text, 
                     command=lambda c=col_id: on_heading_click(tree, c, columns_info, sort_state_ref))
        tree.column(col_id, anchor="w")

def on_heading_click(tree, col, columns_info, sort_state_ref):
    # Xử lý khi click vào tiêu đề cột để sort.
    prev_state = sort_state_ref.get(col, None)
    
    new_state = not prev_state if prev_state is not None else False
    
    sort_state_ref.clear()
    sort_state_ref[col] = new_state
    
    sort_treeview_column(tree, col, new_state)
    
    for c_id, h_text in columns_info.items():
        if c_id == col:
            h_text += " ▲" if not new_state else " ▼"
        tree.heading(c_id, text=h_text, 
                     command=lambda c=c_id: on_heading_click(tree, c, columns_info, sort_state_ref))

def sort_treeview_column(tree, col, reverse):
    # Sắp xếp dữ liệu trong Treeview (in-memory).
    
    data_list = [(tree.set(k, col), k) for k in tree.get_children("")]
    
    def natural_sort_key(s):
        # Tách chuỗi thành (văn bản, số) để sắp xếp tự nhiên
        s_lower = str(s).lower()
        try:
            # Thử sắp xếp bằng số (cho cột Giá, Số lượng)
            return ("", float(s_lower.replace(",", "")))
        except (ValueError, TypeError):
            # Nếu lỗi, dùng re để tách số (cho cột Mã SP, Mã HĐ...)
            parts = re.split(r'(\d+)', s_lower)
            key_parts = []
            for part in parts:
                if part.isdigit():
                    key_parts.append(int(part))
                else:
                    key_parts.append(part)
            return tuple(key_parts)

    data_list.sort(key=lambda t: natural_sort_key(t[0]), reverse=reverse)

    for index, (_, k) in enumerate(data_list):
        tree.move(k, "", index)

def reset_sort_headings(tree, columns_info, sort_state_ref):
    # Reset tất cả tiêu đề cột về trạng thái không sort
    sort_state_ref.clear()
    for col_id, header_text in columns_info.items():
        tree.heading(col_id, text=header_text, 
                     command=lambda c=col_id: on_heading_click(tree, c, columns_info, sort_state_ref))