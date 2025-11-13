import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import ticker

from db import get_connection
from services.finance import get_monthly_revenue
from styles.ui_style import BG_MAIN, BG_TOOLBAR
from styles.treeview_utils import auto_fit_columns

class DoanhThuTab(tk.Frame):
    def __init__(self, parent, role):
        super().__init__(parent, bg=BG_MAIN)
        self.role = role
        self.tree = None
        self.canvas = None
        self.fig = None
        
        self._build_ui()
        self._load_years()

    def _build_ui(self):
        
        # --- Thanh công cụ (Toolbar) ---
        toolbar = tk.Frame(self, bg=BG_TOOLBAR)
        toolbar.pack(fill="x", padx=10, pady=(8,4))
        
        tk.Label(toolbar, text="Chọn năm:", bg=BG_TOOLBAR).pack(side="left", padx=(10,2))
        self.year_cb = ttk.Combobox(toolbar, width=8, state="readonly")
        self.year_cb.pack(side="left", padx=6)
        self.year_cb.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        tk.Button(toolbar, text="Tải lại dữ liệu", command=self.load_data).pack(side="left", padx=6)

        # --- Khu vực nội dung (chia 2 phần) ---
        content_frame = tk.Frame(self, bg=BG_MAIN)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        content_frame.grid_columnconfigure(0, weight=6) # Biểu đồ
        content_frame.grid_columnconfigure(1, weight=4) # Bảng
        content_frame.grid_rowconfigure(0, weight=1)

        # --- Phần 1: Biểu đồ (Bên trái) ---
        chart_frame = tk.Frame(content_frame, bg="white", relief="sunken", bd=1)
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor=BG_MAIN)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # --- Phần 2: Bảng Treeview (Bên phải) ---
        tree_frame = tk.Frame(content_frame)
        tree_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.tree = ttk.Treeview(tree_frame, columns=("Thang", "DoanhThu", "ThayDoi"), show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.heading("Thang", text="Tháng")
        self.tree.heading("DoanhThu", text="Doanh thu")
        self.tree.heading("ThayDoi", text="Tăng trưởng (%)")

    def _load_years(self):
        """Tải danh sách các năm vào Combobox."""
        current_year = datetime.datetime.now().year
        years = [str(y) for y in range(current_year, current_year - 6, -1)]
        self.year_cb["values"] = years
        self.year_cb.set(str(current_year))
        self.load_data() 

    def load_data(self):
        """Tải dữ liệu doanh thu, cập nhật cả bảng và biểu đồ."""
        try:
            year = int(self.year_cb.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Năm không hợp lệ.")
            return

        rows = get_monthly_revenue(year) 
        
        all_months = pd.DataFrame(index=range(1, 13))
        all_months.index.name = "Thang"
        
        if rows:
            df_db = pd.DataFrame(rows, columns=["Thang", "DoanhThu"]).set_index("Thang")
            df = all_months.join(df_db).fillna(0)
        else:
            df = all_months
            df["DoanhThu"] = 0
            
        df = df.reset_index()

        df["PrevMonth"] = df["DoanhThu"].shift(1) 
        df["ThayDoi"] = ((df["DoanhThu"] - df["PrevMonth"]) / df["PrevMonth"]) * 100
        df["ThayDoi"] = df["ThayDoi"].replace([float('inf'), float('-inf')], None) 

        self._update_chart(df)
        self._update_treeview(df)

    def _update_chart(self, df):
        """Vẽ lại biểu đồ cột."""
        self.ax.clear()
        
        months = df["Thang"]
        revenue = df["DoanhThu"]
        
        self.ax.bar(months, revenue, color="#4CAF50", width=0.6)
        
        self.ax.set_title(f"Doanh thu hàng tháng năm {self.year_cb.get()}", fontsize=12)
        self.ax.set_ylabel("Doanh thu (VNĐ)")
        self.ax.set_xlabel("Tháng")
        self.ax.set_xticks(months)
        
        self.ax.get_yaxis().set_major_formatter(
            ticker.FuncFormatter(lambda x, p: format(int(x), ','))
        )
        
        self.fig.tight_layout()
        self.canvas.draw()

    def _update_treeview(self, df):
        """Cập nhật dữ liệu cho bảng Treeview."""
        self.tree.delete(*self.tree.get_children())
        
        for index, row in df.iterrows():
            doanh_thu_str = f"{row['DoanhThu']:,.0f}"
            
            thay_doi_str = "—"
            if pd.notna(row['ThayDoi']):
                thay_doi_str = f"{row['ThayDoi']:.2f}%"

            self.tree.insert("", "end", values=(
                int(row['Thang']), 
                doanh_thu_str,
                thay_doi_str
            ))
        
        auto_fit_columns(self.tree)