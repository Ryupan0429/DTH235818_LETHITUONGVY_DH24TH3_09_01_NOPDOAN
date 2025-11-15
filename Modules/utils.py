import tkinter as tk
from tkinter import ttk

def create_treeview_frame(parent):
    """
    Tạo một Frame chứa Treeview và các thanh cuộn.
    Trả về (frame, tree).
    """
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
# TIỆN ÍCH SORT CHO TREEVIEW (DÙNG CHUNG)
# ===================================================================

def setup_sortable_treeview(tree, columns_info, sort_state_ref):
    """
    Thiết lập tiêu đề và lệnh sort cho Treeview.
    - tree: Đối tượng ttk.Treeview
    - columns_info: Dict dạng {'col_id': 'Tên Hiển Thị'}
    - sort_state_ref: Một dict rỗng (self._sort_state) để lưu trạng thái sort
    """
    tree["columns"] = list(columns_info.keys())
    for col_id, header_text in columns_info.items():
        tree.heading(col_id, text=header_text, 
                     command=lambda c=col_id: on_heading_click(tree, c, columns_info, sort_state_ref))
        tree.column(col_id, anchor="w")

def on_heading_click(tree, col, columns_info, sort_state_ref):
    """
    Xử lý khi click vào tiêu đề cột để sort.
    """
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
    """
    Sắp xếp dữ liệu trong Treeview (in-memory).
    """
    data_list = [(tree.set(k, col), k) for k in tree.get_children("")]
    
    try:
        data_list.sort(key=lambda t: float(str(t[0]).replace(",", "")), reverse=reverse)
    except (ValueError, TypeError):
        data_list.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)

    for index, (_, k) in enumerate(data_list):
        tree.move(k, "", index)

def reset_sort_headings(tree, columns_info, sort_state_ref):
    """Reset tất cả tiêu đề cột về trạng thái không sort (dùng sau khi load_data)."""
    sort_state_ref.clear()
    for col_id, header_text in columns_info.items():
        tree.heading(col_id, text=header_text, 
                     command=lambda c=col_id: on_heading_click(tree, c, columns_info, sort_state_ref))