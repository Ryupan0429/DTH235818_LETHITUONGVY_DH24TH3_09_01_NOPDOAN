import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import ticker
from Features.bao_cao_doanh_thu import get_thu_chi_data 
from Modules.ui_style import BG_MAIN, BG_TOOLBAR, create_button

class ThuChiTab(tk.Frame):
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

        self.tree = ttk.Treeview(tree_frame, columns=("Ky", "Thu", "Chi", "LoiNhuan"), show="headings")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.heading("Ky", text="Kỳ") 
        self.tree.heading("Thu", text="Tổng Thu (Bán)")
        self.tree.heading("Chi", text="Tổng Chi (Nhập)")
        self.tree.heading("LoiNhuan", text="Lợi Nhuận")
        
        self.tree.column("Thu", anchor="e")
        self.tree.column("Chi", anchor="e")
        self.tree.column("LoiNhuan", anchor="e")

    def _load_selectors(self):
        """Tải danh sách các năm/tháng vào Combobox."""
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        
        years = [str(y) for y in range(current_year, current_year - 6, -1)]
        self.year_cb["values"] = years
        self.year_cb.set(str(current_year))
        self.month_cb.set(str(current_month))
        
        self._on_mode_change() 

    def _on_mode_change(self):
        """Ẩn/Hiện bộ chọn Tháng khi đổi chế độ."""
        mode = self.view_mode.get()
        if mode == "Daily":
            self.month_label.pack(side="left", padx=(10,2))
            self.month_cb.pack(side="left", padx=6)
        else:
            self.month_label.pack_forget()
            self.month_cb.pack_forget()

    def load_data(self):
        """Tải dữ liệu thu/chi, cập nhật cả bảng và biểu đồ."""
        mode = self.view_mode.get()
        
        try:
            year = int(self.year_cb.get())
            if mode == 'Daily':
                month = int(self.month_cb.get())
                param = (year, month) 
                title = f"Thu Chi các ngày trong Tháng {month}/{year}"
                period_label = "Ngày"
            elif mode == 'Monthly':
                param = year
                title = f"Thu Chi các tháng trong Năm {year}"
                period_label = "Tháng"
            else: # Yearly
                param = year
                title = f"Thu Chi 5 năm (kết thúc {year})"
                period_label = "Năm"
                
        except ValueError:
            messagebox.showerror("Lỗi", "Năm/Tháng không hợp lệ.")
            return

        df = get_thu_chi_data(param, mode) 
        if df.empty:
            messagebox.showinfo("Thông báo", "Không có dữ liệu thu chi cho kỳ này.", parent=self)
            self.ax.clear()
            self.canvas.draw()
            self.tree.delete(*self.tree.get_children())
            return
            
        df["LoiNhuan"] = df["Thu"] - df["Chi"]
        self._update_chart(df, title, period_label, mode)
        self._update_treeview(df, period_label)

    def _update_chart(self, df, title, period_label, mode):
        """Vẽ lại biểu đồ cột (Thu và Chi)."""
        self.ax.clear()
        
        periods = df["Period"]
        thu = df["Thu"]
        chi = df["Chi"]
        
        x = np.arange(len(periods))  # Vị trí của các nhãn
        width = 0.35  # Độ rộng của cột

        # Vẽ cột Thu
        rects1 = self.ax.bar(x - width/2, thu, width, label='Tổng Thu (Bán)', color='#4CAF50')
        # Vẽ cột Chi
        rects2 = self.ax.bar(x + width/2, chi, width, label='Tổng Chi (Nhập)', color='#F44336')

        self.ax.set_title(title, fontsize=12)
        self.ax.set_ylabel("Tổng tiền (VNĐ)")
        self.ax.set_xlabel(period_label)
        self.ax.legend()
        
        self.ax.get_yaxis().set_major_formatter(
            ticker.FuncFormatter(lambda x, p: format(int(x), ','))
        )
    
        # Đặt vị trí (index) và nhãn (ngày/tháng/năm)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(periods)

        if mode == 'Daily':
            # Nếu là xem theo Ngày (có 30+ nhãn), tự động giảm số lượng nhãn
            self.ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10, integer=True))
        else:
            # Nếu là Tháng (12) hoặc Năm (5), hiển thị tất cả
            self.ax.get_xaxis().set_major_formatter(ticker.FormatStrFormatter('%d'))

        self.fig.tight_layout()
        self.canvas.draw()

    def _update_treeview(self, df, period_label):
        """Cập nhật dữ liệu cho bảng Treeview."""
        self.tree.heading("Ky", text=period_label) 
        self.tree.delete(*self.tree.get_children())
        
        for index, row in df.iterrows():
            thu_str = f"{row['Thu']:,.0f}"
            chi_str = f"{row['Chi']:,.0f}"
            loinhuan_str = f"{row['LoiNhuan']:,.0f}"
            
            # Tô màu cho Lợi nhuận
            tag = "profit" if row['LoiNhuan'] >= 0 else "loss"

            self.tree.insert("", "end", values=(
                int(row['Period']), 
                thu_str,
                chi_str,
                loinhuan_str
            ), tags=(tag,))
        
        # Cấu hình màu sắc
        self.tree.tag_configure("profit", foreground="green")
        self.tree.tag_configure("loss", foreground="red")