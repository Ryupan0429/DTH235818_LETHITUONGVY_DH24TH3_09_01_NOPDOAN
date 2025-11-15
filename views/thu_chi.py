import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import pandas as pd
import numpy as np 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import ticker

from db import get_connection
from Features.bao_cao_doanh_thu import get_revenue_data 
from Modules.ui_style import BG_MAIN, BG_TOOLBAR, create_button

class DoanhThuTab(tk.Frame):
    def __init__(self, parent, role):
        super().__init__(parent, bg=BG_MAIN)
        self.role = role
        self.tree = None
        self.canvas = None
        self.fig = None
        self.view_mode = tk.StringVar(value="Monthly") 
        
        self._build_ui()
        self._load_selectors() 
        self.load_data() 

    def _build_ui(self):
        
        toolbar = tk.Frame(self, bg=BG_TOOLBAR)
        toolbar.pack(fill="x", padx=10, pady=(8,4))
        
        mode_frame = tk.Frame(toolbar, bg=BG_TOOLBAR)
        tk.Radiobutton(mode_frame, text="Theo Ngày", variable=self.view_mode, value="Daily", 
                       bg=BG_TOOLBAR, command=self._on_mode_change).pack(side="left")
        tk.Radiobutton(mode_frame, text="Theo Tháng", variable=self.view_mode, value="Monthly", 
                       bg=BG_TOOLBAR, command=self._on_mode_change).pack(side="left", padx=10)
        tk.Radiobutton(mode_frame, text="Theo Năm", variable=self.view_mode, value="Yearly", 
                       bg=BG_TOOLBAR, command=self._on_mode_change).pack(side="left")
        mode_frame.pack(side="left", padx=10)

        self.selector_frame = tk.Frame(toolbar, bg=BG_TOOLBAR)
        self.selector_frame.pack(side="left", padx=10)
        
        tk.Label(self.selector_frame, text="Chọn Năm:", bg=BG_TOOLBAR).pack(side="left", padx=(10,2))
        self.year_cb = ttk.Combobox(self.selector_frame, width=8, state="readonly")
        self.year_cb.pack(side="left", padx=6)
        
        self.month_label = tk.Label(self.selector_frame, text="Chọn Tháng:", bg=BG_TOOLBAR)
        self.month_cb = ttk.Combobox(self.selector_frame, width=5, state="readonly",
                                     values=[str(i) for i in range(1, 13)])
        
        create_button(toolbar, "Xem", command=self.load_data, kind="primary").pack(side="left", padx=10)

        content_frame = tk.Frame(self, bg=BG_MAIN)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        content_frame.grid_columnconfigure(0, weight=6) 
        content_frame.grid_columnconfigure(1, weight=4) 
        content_frame.grid_rowconfigure(0, weight=1)

        chart_frame = tk.Frame(content_frame, bg="white", relief="sunken", bd=1)
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.fig = Figure(figsize=(5, 4), dpi=100, facecolor=BG_MAIN)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        tree_frame = tk.Frame(content_frame)
        tree_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.tree = ttk.Treeview(tree_frame, columns=("Ky", "DoanhThu", "ThayDoi"), show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.heading("Ky", text="Kỳ") 
        self.tree.heading("DoanhThu", text="Doanh thu")
        self.tree.heading("ThayDoi", text="Tăng trưởng (%)")

    def _load_selectors(self):
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        
        years = [str(y) for y in range(current_year, current_year - 6, -1)]
        self.year_cb["values"] = years
        self.year_cb.set(str(current_year))
        self.month_cb.set(str(current_month))
        
        self._on_mode_change() 

    def _on_mode_change(self):
        mode = self.view_mode.get()
        if mode == "Daily":
            self.month_label.pack(side="left", padx=(10,2))
            self.month_cb.pack(side="left", padx=6)
        else:
            self.month_label.pack_forget()
            self.month_cb.pack_forget()

    def load_data(self):
        mode = self.view_mode.get()
        
        try:
            year = int(self.year_cb.get())
            if mode == 'Daily':
                month = int(self.month_cb.get())
                param = (year, month) 
                title = f"Doanh thu các ngày trong Tháng {month}/{year}"
                period_label = "Ngày"
            elif mode == 'Monthly':
                param = year
                title = f"Doanh thu các tháng trong Năm {year}"
                period_label = "Tháng"
            else:
                param = year
                title = f"Doanh thu 5 năm (kết thúc {year})"
                period_label = "Năm"
                
        except ValueError:
            messagebox.showerror("Lỗi", "Năm/Tháng không hợp lệ.")
            return

        df = get_revenue_data(param, mode) 
        if df.empty:
            messagebox.showinfo("Thông báo", "Không có dữ liệu doanh thu cho kỳ này.", parent=self)
            self.ax.clear()
            self.canvas.draw()
            self.tree.delete(*self.tree.get_children())
            return
            
        df["Prev"] = df["Revenue"].shift(1) 
        prev_no_zero = df["Prev"].replace(0, np.nan) 
        df["ThayDoi"] = ((df["Revenue"] - df["Prev"]) / prev_no_zero) * 100
        df["ThayDoi"] = df["ThayDoi"].replace([float('inf'), float('-inf')], np.nan) 

        self._update_chart(df, title, period_label)
        self._update_treeview(df, period_label)

    def _update_chart(self, df, title, period_label):
        self.ax.clear()
        
        periods = df["Period"]
        revenue = df["Revenue"]
        
        self.ax.bar(periods, revenue, color="#4CAF50", width=0.6)
        
        self.ax.set_title(title, fontsize=12)
        self.ax.set_ylabel("Doanh thu (VNĐ)")
        self.ax.set_xlabel(period_label)
        
        if len(periods) > 12: # Nếu là chế độ 'Daily' (Nhiều nhãn)
            # Tự động chọn 10 nhãn đẹp nhất và là số nguyên
            self.ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=10))
        else: # Nếu là 'Monthly' hoặc 'Yearly'
            # Hiển thị tất cả các nhãn
            self.ax.set_xticks(periods)
            self.ax.get_xaxis().set_major_formatter(ticker.FormatStrFormatter('%d'))

        self.ax.get_yaxis().set_major_formatter(
            ticker.FuncFormatter(lambda x, p: format(int(x), ','))
        )
        
        self.fig.tight_layout()
        self.canvas.draw()

    def _update_treeview(self, df, period_label):
        self.tree.heading("Ky", text=period_label) 
        self.tree.delete(*self.tree.get_children())
        
        for index, row in df.iterrows():
            doanh_thu_str = f"{row['Revenue']:,.0f}"
            
            thay_doi_str = "—"
            if pd.notna(row['ThayDoi']): 
                thay_doi_str = f"{row['ThayDoi']:.2f}%"

            self.tree.insert("", "end", values=(
                int(row['Period']), 
                doanh_thu_str,
                thay_doi_str
            ))