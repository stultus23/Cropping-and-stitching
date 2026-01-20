"""
现代化图片批处理工具
支持批量裁剪和拼接图片
作者：GitHub Copilot
日期：2026-01-20
"""

import os
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk


class ImageProcessor:
    """图像处理逻辑类"""
    
    @staticmethod
    def crop_image(img, left, top, right, bottom):
        """裁剪图片"""
        w, h = img.size
        r = max(left, w - right)
        b = max(top, h - bottom)
        if r <= left or b <= top:
            return None
        return img.crop((left, top, r, b))
    
    @staticmethod
    def stitch_images_grid(images, rows, cols, spacing, bg_color=(255, 255, 255)):
        """网格拼接图片"""
        if not images:
            return None
        
        # 自动计算行列数
        if rows <= 0 and cols <= 0:
            cols = math.ceil(math.sqrt(len(images)))
            rows = math.ceil(len(images) / cols)
        elif rows <= 0:
            rows = math.ceil(len(images) / cols)
        elif cols <= 0:
            cols = math.ceil(len(images) / rows)
        
        # 计算每个单元格大小
        cell_w = max(img.width for img in images)
        cell_h = max(img.height for img in images)
        
        # 计算输出图片大小
        out_w = cols * cell_w + spacing * (cols - 1) if cols > 0 else cell_w
        out_h = rows * cell_h + spacing * (rows - 1) if rows > 0 else cell_h
        out = Image.new('RGB', (out_w, out_h), bg_color)
        
        # 粘贴图片
        for idx, img in enumerate(images):
            if idx >= rows * cols:
                break
            r = idx // cols
            c = idx % cols
            
            # 等比例缩放以适应单元格
            ratio = min(cell_w / img.width, cell_h / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 计算居中位置
            offset_x = c * (cell_w + spacing) + (cell_w - resized_img.width) // 2
            offset_y = r * (cell_h + spacing) + (cell_h - resized_img.height) // 2
            out.paste(resized_img, (offset_x, offset_y))
        
        return out
    
    @staticmethod
    def stitch_images_horizontal(images, spacing, bg_color=(255, 255, 255)):
        """水平拼接图片"""
        if not images:
            return None
        
        max_h = max(img.height for img in images)
        resized = []
        total_w = spacing * (len(images) - 1)
        
        for img in images:
            new_w = int(img.width * (max_h / img.height))
            resized_img = img.resize((new_w, max_h), Image.Resampling.LANCZOS)
            resized.append(resized_img)
            total_w += new_w
        
        out = Image.new('RGB', (total_w, max_h), bg_color)
        x = 0
        for img in resized:
            out.paste(img, (x, 0))
            x += img.width + spacing
        
        return out
    
    @staticmethod
    def stitch_images_vertical(images, spacing, bg_color=(255, 255, 255)):
        """垂直拼接图片"""
        if not images:
            return None
        
        max_w = max(img.width for img in images)
        resized = []
        total_h = spacing * (len(images) - 1)
        
        for img in images:
            new_h = int(img.height * (max_w / img.width))
            resized_img = img.resize((max_w, new_h), Image.Resampling.LANCZOS)
            resized.append(resized_img)
            total_h += new_h
        
        out = Image.new('RGB', (max_w, total_h), bg_color)
        y = 0
        for img in resized:
            out.paste(img, (0, y))
            y += img.height + spacing
        
        return out


class ModernImageApp(ctk.CTk):
    """主应用程序类"""
    
    def __init__(self):
        super().__init__()
        
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 窗口配置
        self.title("图片批处理工具")
        self.geometry("1400x900")
        
        # 数据
        self.folder = os.path.abspath('.')
        self.files = []
        self.selected_files = set()  # 存储选中的文件索引
        self.thumbnail_cache = {}  # 缩略图缓存
        self.file_frames = []  # 文件卡片框架
        self.preview_img = None
        self.canvas_image = None
        self.crop_rect = None
        self.crop_start = None
        self.stitch_preview_img = None
        
        # 变量
        self.left_var = tk.IntVar(value=0)
        self.top_var = tk.IntVar(value=0)
        self.right_var = tk.IntVar(value=0)
        self.bottom_var = tk.IntVar(value=0)
        self.spacing_var = tk.IntVar(value=10)
        self.rows_var = tk.IntVar(value=0)
        self.cols_var = tk.IntVar(value=3)
        self.stitch_mode = tk.StringVar(value="grid")
        self.bg_color = "#FFFFFF"
        
        self.setup_ui()
        self.load_images(self.folder)
    
    def setup_ui(self):
        """构建 UI"""
        # 创建选项卡视图
        self.tabview = ctk.CTkTabview(self, width=1380, height=880)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 添加选项卡
        self.tab_files = self.tabview.add("📁 文件管理")
        self.tab_crop = self.tabview.add("✂️ 批量裁剪")
        self.tab_stitch = self.tabview.add("🧩 智能拼接")
        
        self.setup_files_tab()
        self.setup_crop_tab()
        self.setup_stitch_tab()
    
    def setup_files_tab(self):
        """文件管理选项卡"""
        # 左侧：控制面板
        left_frame = ctk.CTkFrame(self.tab_files, width=350)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        # 文件夹选择
        ctk.CTkLabel(left_frame, text="工作文件夹", font=("Arial", 16, "bold")).pack(pady=(10, 5))
        
        self.folder_label = ctk.CTkLabel(left_frame, text=self.folder, wraplength=320)
        self.folder_label.pack(pady=5)
        
        ctk.CTkButton(
            left_frame, 
            text="📁 选择文件夹", 
            command=self.choose_folder,
            width=320,
            height=40
        ).pack(pady=5)
        
        ctk.CTkButton(
            left_frame, 
            text="➕ 添加图片文件...", 
            command=self.add_images,
            width=320,
            height=40
        ).pack(pady=5)
        
        # 分隔线
        ctk.CTkLabel(left_frame, text="").pack(pady=5)
        
        # 操作按钮
        ctk.CTkLabel(left_frame, text="批量操作", font=("Arial", 16, "bold")).pack(pady=(10, 5))
        
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.pack(pady=5)
        
        ctk.CTkButton(btn_frame, text="全选", command=self.select_all, width=100).grid(row=0, column=0, padx=2)
        ctk.CTkButton(btn_frame, text="反选", command=self.invert_selection, width=100).grid(row=0, column=1, padx=2)
        ctk.CTkButton(btn_frame, text="清除", command=self.clear_selection, width=100).grid(row=0, column=2, padx=2)
        
        ctk.CTkButton(
            left_frame, 
            text="🗑️ 移除选中项", 
            command=self.remove_selected,
            width=320,
            height=40,
            fg_color="darkred",
            hover_color="red"
        ).pack(pady=10)
        
        # 统计信息
        self.stats_label = ctk.CTkLabel(left_frame, text="", font=("Arial", 14, "bold"))
        self.stats_label.pack(pady=10)
        
        # 提示信息
        help_frame = ctk.CTkFrame(left_frame)
        help_frame.pack(fill="x", padx=5, pady=10)
        ctk.CTkLabel(help_frame, text="💡 提示", font=("Arial", 12, "bold")).pack(pady=5)
        ctk.CTkLabel(help_frame, text="点击图片卡片选择\nCtrl+点击多选", font=("Arial", 10)).pack(pady=2)
        
        # 右侧：缩略图网格视图
        right_frame = ctk.CTkFrame(self.tab_files)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(right_frame, text="图片预览（点击选择）", font=("Arial", 16, "bold")).pack(pady=10)
        
        # 创建可滚动框架
        self.file_scroll_frame = ctk.CTkScrollableFrame(right_frame, width=950, height=750)
        self.file_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def setup_crop_tab(self):
        """裁剪选项卡"""
        # 左侧：控制面板
        left_frame = ctk.CTkFrame(self.tab_crop, width=400)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        ctk.CTkLabel(left_frame, text="裁剪模式", font=("Arial", 18, "bold")).pack(pady=10)
        
        # 模式 A：数值裁剪
        mode_a_frame = ctk.CTkFrame(left_frame)
        mode_a_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(mode_a_frame, text="模式 A：数值微调", font=("Arial", 14, "bold")).pack(pady=5)
        
        for label, var in [("左侧 (px):", self.left_var), ("上侧 (px):", self.top_var), 
                           ("右侧 (px):", self.right_var), ("下侧 (px):", self.bottom_var)]:
            row = ctk.CTkFrame(mode_a_frame)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label, width=100).pack(side="left", padx=5)
            entry = ctk.CTkEntry(row, textvariable=var, width=150)
            entry.pack(side="left", padx=5)
            entry.bind("<KeyRelease>", self.on_crop_values_changed)
        
        # 模式 B：可视化裁剪
        mode_b_frame = ctk.CTkFrame(left_frame)
        mode_b_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(mode_b_frame, text="模式 B：可视化裁剪", font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(mode_b_frame, text="在右侧预览区用鼠标拖拽画框", font=("Arial", 10)).pack(pady=2)
        
        ctk.CTkButton(
            mode_b_frame,
            text="加载预览图片",
            command=self.load_crop_preview,
            width=350
        ).pack(pady=5)
        
        ctk.CTkButton(
            mode_b_frame,
            text="重置裁剪区域",
            command=self.reset_crop_area,
            width=350
        ).pack(pady=5)
        
        # 操作按钮
        ctk.CTkLabel(left_frame, text="").pack(pady=10)
        
        ctk.CTkButton(
            left_frame,
            text="💾 批量裁剪并保存",
            command=self.crop_and_save_all,
            width=350,
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(pady=10)
        
        # 提示信息
        help_text = ctk.CTkTextbox(left_frame, height=150)
        help_text.pack(fill="x", padx=10, pady=10)
        help_text.insert("1.0", 
            "💡 使用提示：\n\n"
            "1. 在「文件管理」中选择要裁剪的图片\n"
            "2. 使用模式A输入像素值或模式B画框\n"
            "3. 两种模式会自动联动\n"
            "4. 点击「批量裁剪并保存」应用到所有选中图片\n"
            "5. 裁剪后的图片保存在 cropped 文件夹"
        )
        help_text.configure(state="disabled")
        
        # 右侧：预览画布
        right_frame = ctk.CTkFrame(self.tab_crop)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(right_frame, text="实时预览", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Canvas 用于显示和绘制
        self.crop_canvas = tk.Canvas(right_frame, bg="#2b2b2b", highlightthickness=0)
        self.crop_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 绑定鼠标事件
        self.crop_canvas.bind("<ButtonPress-1>", self.on_crop_mouse_down)
        self.crop_canvas.bind("<B1-Motion>", self.on_crop_mouse_drag)
        self.crop_canvas.bind("<ButtonRelease-1>", self.on_crop_mouse_up)
    
    def setup_stitch_tab(self):
        """拼接选项卡"""
        # 左侧：控制面板
        left_frame = ctk.CTkFrame(self.tab_stitch, width=400)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        ctk.CTkLabel(left_frame, text="拼接设置", font=("Arial", 18, "bold")).pack(pady=10)
        
        # 拼接模式
        mode_frame = ctk.CTkFrame(left_frame)
        mode_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(mode_frame, text="拼接模式：", font=("Arial", 14)).pack(pady=5)
        ctk.CTkRadioButton(mode_frame, text="网格布局", variable=self.stitch_mode, value="grid").pack(pady=2)
        ctk.CTkRadioButton(mode_frame, text="水平拼接", variable=self.stitch_mode, value="horizontal").pack(pady=2)
        ctk.CTkRadioButton(mode_frame, text="垂直拼接", variable=self.stitch_mode, value="vertical").pack(pady=2)
        
        # 网格设置
        grid_frame = ctk.CTkFrame(left_frame)
        grid_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(grid_frame, text="网格布局（仅网格模式）", font=("Arial", 12, "bold")).pack(pady=5)
        
        row = ctk.CTkFrame(grid_frame)
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text="行数 (0=自动):", width=120).pack(side="left", padx=5)
        ctk.CTkEntry(row, textvariable=self.rows_var, width=150).pack(side="left", padx=5)
        
        row = ctk.CTkFrame(grid_frame)
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text="列数 (0=自动):", width=120).pack(side="left", padx=5)
        ctk.CTkEntry(row, textvariable=self.cols_var, width=150).pack(side="left", padx=5)
        
        # 通用设置
        common_frame = ctk.CTkFrame(left_frame)
        common_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(common_frame, text="通用设置", font=("Arial", 12, "bold")).pack(pady=5)
        
        row = ctk.CTkFrame(common_frame)
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text="间距 (px):", width=120).pack(side="left", padx=5)
        ctk.CTkEntry(row, textvariable=self.spacing_var, width=150).pack(side="left", padx=5)
        
        row = ctk.CTkFrame(common_frame)
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text="背景颜色:", width=120).pack(side="left", padx=5)
        self.bg_color_btn = ctk.CTkButton(row, text=self.bg_color, command=self.choose_bg_color, width=150)
        self.bg_color_btn.pack(side="left", padx=5)
        
        # 图片来源
        source_frame = ctk.CTkFrame(left_frame)
        source_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(source_frame, text="图片来源", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.use_cropped_var = ctk.BooleanVar(value=True)
        self.use_selected_var = ctk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(source_frame, text="优先使用 cropped 文件夹", variable=self.use_cropped_var).pack(pady=2)
        ctk.CTkCheckBox(source_frame, text="仅拼接列表中选中的图片", variable=self.use_selected_var).pack(pady=2)
        
        # 操作按钮
        ctk.CTkLabel(left_frame, text="").pack(pady=5)
        
        ctk.CTkButton(
            left_frame,
            text="🔍 生成预览",
            command=self.generate_stitch_preview,
            width=350,
            height=45,
            font=("Arial", 15, "bold"),
            fg_color="blue",
            hover_color="darkblue"
        ).pack(pady=5)
        
        ctk.CTkButton(
            left_frame,
            text="💾 导出高清图片",
            command=self.export_stitch_image,
            width=350,
            height=45,
            font=("Arial", 15, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(pady=5)
        
        # 提示信息
        help_text = ctk.CTkTextbox(left_frame, height=100)
        help_text.pack(fill="x", padx=10, pady=10)
        help_text.insert("1.0",
            "💡 使用提示：\n\n"
            "1. 选择拼接模式和参数\n"
            "2. 点击「生成预览」查看效果\n"
            "3. 满意后点击「导出高清图片」保存"
        )
        help_text.configure(state="disabled")
        
        # 右侧：预览区域
        right_frame = ctk.CTkFrame(self.tab_stitch)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(right_frame, text="拼接预览", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.stitch_canvas = tk.Canvas(right_frame, bg="#2b2b2b", highlightthickness=0)
        self.stitch_canvas.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ==================== 文件管理功能 ====================
    
    def choose_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(initialdir=self.folder)
        if folder:
            self.folder = folder
            self.folder_label.configure(text=self.folder)
            self.load_images(self.folder)
    
    def load_images(self, folder):
        """加载图片文件"""
        valid = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
        try:
            files = [f for f in os.listdir(folder) if f.lower().endswith(valid)]
        except Exception:
            files = []
        files.sort()
        self.files = [os.path.join(folder, f) for f in files]
        self.selected_files.clear()
        self.thumbnail_cache.clear()
        
        # 更新缩略图网格显示
        self.refresh_file_grid()
        
        # 更新统计信息
        self.update_stats()
    
    def refresh_file_grid(self):
        """刷新文件网格显示"""
        # 清除旧的框架
        for frame in self.file_frames:
            frame.destroy()
        self.file_frames.clear()
        
        # 创建网格布局（每行4个）
        cols = 4
        for idx, file_path in enumerate(self.files):
            row = idx // cols
            col = idx % cols
            
            # 创建文件卡片
            file_frame = self.create_file_card(file_path, idx)
            file_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.file_frames.append(file_frame)
        
        # 配置列权重
        for c in range(cols):
            self.file_scroll_frame.grid_columnconfigure(c, weight=1)
    
    def create_file_card(self, file_path, index):
        """创建文件卡片"""
        # 主框架 - 移除固定高度，让其自适应内容
        is_selected = index in self.selected_files
        card_frame = ctk.CTkFrame(
            self.file_scroll_frame,
            width=220,
            fg_color=("#3a3a3a" if is_selected else "#2b2b2b"),
            border_width=3,
            border_color=("#1f6aa5" if is_selected else "#3a3a3a")
        )
        card_frame.pack_propagate(True)  # 允许框架根据内容自动调整大小
        
        # 存储索引和相关组件，用于后续更新
        card_frame.card_index = index
        card_frame.card_widgets = {}
        
        # 缩略图
        try:
            if file_path in self.thumbnail_cache:
                thumb = self.thumbnail_cache[file_path]
            else:
                img = Image.open(file_path)
                # 创建缩略图（保持宽高比）
                img.thumbnail((180, 180), Image.Resampling.LANCZOS)
                thumb = ImageTk.PhotoImage(img)
                self.thumbnail_cache[file_path] = thumb
            
            img_label = ctk.CTkLabel(card_frame, image=thumb, text="")
            img_label.image = thumb  # 保持引用
            img_label.pack(pady=(8, 3))
            card_frame.card_widgets['img_label'] = img_label
        except Exception as e:
            # 如果加载失败，显示占位符
            img_label = ctk.CTkLabel(card_frame, text="❌\n无法加载", font=("Arial", 12), height=100)
            img_label.pack(pady=(8, 3))
            card_frame.card_widgets['img_label'] = img_label
        
        # 文件名
        filename = os.path.basename(file_path)
        name_label = ctk.CTkLabel(
            card_frame,
            text=filename,
            wraplength=200,
            font=("Arial", 9),
            height=30  # 限制文件名区域高度
        )
        name_label.pack(pady=(0, 3), padx=5)
        card_frame.card_widgets['name_label'] = name_label
        
        # 选中标记（使用容器以便动态更新）
        check_container = ctk.CTkFrame(card_frame, fg_color="transparent", height=20)
        check_container.pack(pady=(0, 5), fill="x")
        check_container.pack_propagate(False)
        card_frame.card_widgets['check_container'] = check_container
        
        if is_selected:
            check_label = ctk.CTkLabel(check_container, text="✓ 已选中", font=("Arial", 9, "bold"), text_color="#4a9eff")
            check_label.pack()
            card_frame.card_widgets['check_label'] = check_label
        
        # 绑定点击事件
        def on_click(event):
            self.toggle_file_selection(index, event)
        
        card_frame.bind("<Button-1>", on_click)
        img_label.bind("<Button-1>", on_click)
        name_label.bind("<Button-1>", on_click)
        
        return card_frame
    
    def update_card_selection_state(self, index):
        """更新单个卡片的选中状态（无需重建）"""
        if index >= len(self.file_frames):
            return
        
        card_frame = self.file_frames[index]
        is_selected = index in self.selected_files
        
        # 更新边框和背景色
        card_frame.configure(
            fg_color=("#3a3a3a" if is_selected else "#2b2b2b"),
            border_color=("#1f6aa5" if is_selected else "#3a3a3a")
        )
        
        # 更新选中标记
        check_container = card_frame.card_widgets.get('check_container')
        if check_container:
            # 清除旧的选中标记
            if 'check_label' in card_frame.card_widgets:
                card_frame.card_widgets['check_label'].destroy()
                del card_frame.card_widgets['check_label']
            
            # 如果需要，添加新的选中标记
            if is_selected:
                check_label = ctk.CTkLabel(check_container, text="✓ 已选中", font=("Arial", 10, "bold"), text_color="#4a9eff")
                check_label.pack()
                card_frame.card_widgets['check_label'] = check_label
    
    def toggle_file_selection(self, index, event=None):
        """切换文件选择状态"""
        # 检查是否按住 Ctrl 键
        ctrl_pressed = event and (event.state & 0x4)
        
        # 记录之前的选中状态，用于确定需要更新哪些卡片
        old_selection = self.selected_files.copy()
        
        if not ctrl_pressed:
            # 单选模式：清除其他选择
            self.selected_files.clear()
        
        # 切换当前选择
        if index in self.selected_files:
            self.selected_files.remove(index)
        else:
            self.selected_files.add(index)
        
        # 只更新受影响的卡片，而不是刷新整个网格
        # 计算哪些卡片的状态发生了变化
        changed_indices = old_selection.symmetric_difference(self.selected_files)
        
        # 只更新变化的卡片
        for idx in changed_indices:
            self.update_card_selection_state(idx)
        
        # 更新统计信息
        self.update_stats()
    
    def add_images(self):
        """添加图片文件"""
        paths = filedialog.askopenfilenames(
            initialdir=self.folder,
            filetypes=[('图片文件', '*.jpg *.jpeg *.png *.bmp *.tiff *.webp')]
        )
        if not paths:
            return
        
        for p in paths:
            if p not in self.files:
                self.files.append(p)
        
        # 刷新网格显示
        self.refresh_file_grid()
        self.update_stats()
    
    def select_all(self):
        """全选"""
        self.selected_files = set(range(len(self.files)))
        self.refresh_file_grid()
        self.update_stats()
    
    def invert_selection(self):
        """反选"""
        all_indices = set(range(len(self.files)))
        self.selected_files = all_indices - self.selected_files
        self.refresh_file_grid()
        self.update_stats()
    
    def clear_selection(self):
        """清除选择"""
        self.selected_files.clear()
        self.refresh_file_grid()
        self.update_stats()
    
    def remove_selected(self):
        """移除选中项"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要移除的图片")
            return
        
        # 从后向前删除
        for idx in sorted(self.selected_files, reverse=True):
            if 0 <= idx < len(self.files):
                # 从缓存中删除
                if self.files[idx] in self.thumbnail_cache:
                    del self.thumbnail_cache[self.files[idx]]
                del self.files[idx]
        
        # 清空选择
        self.selected_files.clear()
        
        # 刷新显示
        self.refresh_file_grid()
        self.update_stats()
    
    def update_stats(self):
        """更新统计信息"""
        total = len(self.files)
        selected = len(self.selected_files)
        self.stats_label.configure(
            text=f"共 {total} 张图片\n已选中 {selected} 张"
        )
    
    def get_selected_files(self):
        """获取选中的文件"""
        if not self.selected_files:
            return []
        return [self.files[i] for i in sorted(self.selected_files) if 0 <= i < len(self.files)]
    
    # ==================== 裁剪功能 ====================
    
    def load_crop_preview(self):
        """加载裁剪预览图"""
        selected = self.get_selected_files()
        if not selected:
            if self.files:
                selected = [self.files[0]]
            else:
                messagebox.showwarning("警告", "没有可用的图片")
                return
        
        try:
            self.original_img = Image.open(selected[0])
            self.display_crop_preview()
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败：{e}")
    
    def display_crop_preview(self):
        """显示裁剪预览"""
        if not self.original_img:
            return
        
        # 获取画布大小
        canvas_w = self.crop_canvas.winfo_width()
        canvas_h = self.crop_canvas.winfo_height()
        
        if canvas_w <= 1 or canvas_h <= 1:
            self.crop_canvas.after(100, self.display_crop_preview)
            return
        
        # 计算缩放比例
        img_w, img_h = self.original_img.size
        scale = min(canvas_w / img_w, canvas_h / img_h, 1.0)
        
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        # 缩放图片
        display_img = self.original_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.canvas_image = ImageTk.PhotoImage(display_img)
        
        # 显示图片
        self.crop_canvas.delete("all")
        offset_x = (canvas_w - new_w) // 2
        offset_y = (canvas_h - new_h) // 2
        self.crop_canvas.create_image(offset_x, offset_y, anchor="nw", image=self.canvas_image)
        
        # 存储用于坐标转换的信息
        self.canvas_scale = scale
        self.canvas_offset = (offset_x, offset_y)
        self.canvas_size = (new_w, new_h)
        
        # 绘制裁剪框
        self.draw_crop_rect()
    
    def draw_crop_rect(self):
        """根据裁剪值绘制矩形框"""
        if not self.original_img or not hasattr(self, 'canvas_scale'):
            return
        
        img_w, img_h = self.original_img.size
        left = self.left_var.get()
        top = self.top_var.get()
        right = self.right_var.get()
        bottom = self.bottom_var.get()
        
        # 计算实际裁剪区域
        x1 = left
        y1 = top
        x2 = img_w - right
        y2 = img_h - bottom
        
        if x2 <= x1 or y2 <= y1:
            return
        
        # 转换到画布坐标
        scale = self.canvas_scale
        offset_x, offset_y = self.canvas_offset
        
        canvas_x1 = x1 * scale + offset_x
        canvas_y1 = y1 * scale + offset_y
        canvas_x2 = x2 * scale + offset_x
        canvas_y2 = y2 * scale + offset_y
        
        # 删除旧矩形
        self.crop_canvas.delete("crop_rect")
        
        # 绘制新矩形
        self.crop_canvas.create_rectangle(
            canvas_x1, canvas_y1, canvas_x2, canvas_y2,
            outline="red", width=2, tags="crop_rect"
        )
        
        # 绘制角点
        r = 5
        for x, y in [(canvas_x1, canvas_y1), (canvas_x2, canvas_y1), 
                     (canvas_x1, canvas_y2), (canvas_x2, canvas_y2)]:
            self.crop_canvas.create_oval(
                x-r, y-r, x+r, y+r,
                fill="red", tags="crop_rect"
            )
    
    def on_crop_mouse_down(self, event):
        """鼠标按下"""
        self.crop_start = (event.x, event.y)
    
    def on_crop_mouse_drag(self, event):
        """鼠标拖拽"""
        if not self.crop_start or not hasattr(self, 'canvas_offset'):
            return
        
        x1, y1 = self.crop_start
        x2, y2 = event.x, event.y
        
        # 确保左上到右下
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1
        
        # 绘制临时矩形
        self.crop_canvas.delete("temp_rect")
        self.crop_canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="yellow", width=2, tags="temp_rect"
        )
    
    def on_crop_mouse_up(self, event):
        """鼠标松开"""
        if not self.crop_start or not self.original_img or not hasattr(self, 'canvas_scale'):
            return
        
        x1, y1 = self.crop_start
        x2, y2 = event.x, event.y
        
        # 确保左上到右下
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1
        
        # 转换到图片坐标
        scale = self.canvas_scale
        offset_x, offset_y = self.canvas_offset
        
        img_x1 = int((x1 - offset_x) / scale)
        img_y1 = int((y1 - offset_y) / scale)
        img_x2 = int((x2 - offset_x) / scale)
        img_y2 = int((y2 - offset_y) / scale)
        
        # 限制范围
        img_w, img_h = self.original_img.size
        img_x1 = max(0, min(img_x1, img_w))
        img_y1 = max(0, min(img_y1, img_h))
        img_x2 = max(0, min(img_x2, img_w))
        img_y2 = max(0, min(img_y2, img_h))
        
        # 计算裁剪值
        self.left_var.set(img_x1)
        self.top_var.set(img_y1)
        self.right_var.set(img_w - img_x2)
        self.bottom_var.set(img_h - img_y2)
        
        # 清除临时矩形
        self.crop_canvas.delete("temp_rect")
        
        # 重绘裁剪框
        self.draw_crop_rect()
        
        self.crop_start = None
    
    def on_crop_values_changed(self, event):
        """裁剪值改变时更新预览"""
        self.draw_crop_rect()
    
    def reset_crop_area(self):
        """重置裁剪区域"""
        self.left_var.set(0)
        self.top_var.set(0)
        self.right_var.set(0)
        self.bottom_var.set(0)
        self.draw_crop_rect()
    
    def crop_and_save_all(self):
        """批量裁剪并保存"""
        selected = self.get_selected_files()
        if not selected:
            messagebox.showwarning("警告", "请先选择要裁剪的图片")
            return
        
        left = self.left_var.get()
        top = self.top_var.get()
        right = self.right_var.get()
        bottom = self.bottom_var.get()
        
        out_dir = os.path.join(self.folder, 'cropped')
        os.makedirs(out_dir, exist_ok=True)
        
        count = 0
        for path in selected:
            try:
                with Image.open(path) as img:
                    cropped = ImageProcessor.crop_image(img, left, top, right, bottom)
                    if cropped:
                        base = os.path.basename(path)
                        save_path = os.path.join(out_dir, base)
                        cropped.save(save_path, quality=95)
                        count += 1
            except Exception as e:
                print(f"处理 {path} 时出错：{e}")
        
        messagebox.showinfo("完成", f"成功裁剪 {count} 张图片\n保存位置：{out_dir}")
    
    # ==================== 拼接功能 ====================
    
    def choose_bg_color(self):
        """选择背景颜色"""
        from tkinter import colorchooser
        color = colorchooser.askcolor(initialcolor=self.bg_color)
        if color[1]:
            self.bg_color = color[1]
            self.bg_color_btn.configure(text=self.bg_color)
    
    def get_stitch_images(self):
        """获取要拼接的图片"""
        if self.use_selected_var.get():
            paths = self.get_selected_files()
            if not paths:
                messagebox.showwarning("警告", "未选择任何图片")
                return None
        else:
            folder = self.folder
            if self.use_cropped_var.get():
                cropped_folder = os.path.join(folder, 'cropped')
                if os.path.isdir(cropped_folder):
                    folder = cropped_folder
            
            valid = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
            paths = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(valid)]
            paths.sort()
            
            if not paths:
                messagebox.showwarning("警告", "未找到任何图片")
                return None
        
        try:
            images = [Image.open(p).convert('RGB') for p in paths]
            return images
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败：{e}")
            return None
    
    def generate_stitch_preview(self):
        """生成拼接预览"""
        images = self.get_stitch_images()
        if not images:
            return
        
        try:
            # 解析背景颜色
            bg_color = tuple(int(self.bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            spacing = self.spacing_var.get()
            mode = self.stitch_mode.get()
            
            # 生成拼接图
            if mode == "grid":
                rows = self.rows_var.get()
                cols = self.cols_var.get()
                result = ImageProcessor.stitch_images_grid(images, rows, cols, spacing, bg_color)
            elif mode == "horizontal":
                result = ImageProcessor.stitch_images_horizontal(images, spacing, bg_color)
            else:  # vertical
                result = ImageProcessor.stitch_images_vertical(images, spacing, bg_color)
            
            if not result:
                messagebox.showerror("错误", "拼接失败")
                return
            
            # 保存结果用于导出
            self.stitch_result = result
            
            # 显示预览（缩略图）
            canvas_w = self.stitch_canvas.winfo_width()
            canvas_h = self.stitch_canvas.winfo_height()
            
            if canvas_w <= 1 or canvas_h <= 1:
                canvas_w, canvas_h = 800, 600
            
            # 计算缩放比例
            scale = min(canvas_w / result.width, canvas_h / result.height, 1.0)
            preview_w = int(result.width * scale)
            preview_h = int(result.height * scale)
            
            preview = result.resize((preview_w, preview_h), Image.Resampling.LANCZOS)
            self.stitch_preview_img = ImageTk.PhotoImage(preview)
            
            # 显示
            self.stitch_canvas.delete("all")
            offset_x = (canvas_w - preview_w) // 2
            offset_y = (canvas_h - preview_h) // 2
            self.stitch_canvas.create_image(offset_x, offset_y, anchor="nw", image=self.stitch_preview_img)
            
            messagebox.showinfo("完成", f"预览已生成\n尺寸：{result.width} x {result.height} 像素")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成预览失败：{e}")
    
    def export_stitch_image(self):
        """导出拼接图片"""
        if not hasattr(self, 'stitch_result') or self.stitch_result is None:
            messagebox.showwarning("警告", "请先生成预览")
            return
        
        out_dir = os.path.join(self.folder, 'stitched')
        os.makedirs(out_dir, exist_ok=True)
        
        save_path = filedialog.asksaveasfilename(
            defaultextension='.jpg',
            filetypes=[('JPEG', '*.jpg'), ('PNG', '*.png')],
            initialfile='stitched.jpg',
            initialdir=out_dir
        )
        
        if save_path:
            try:
                self.stitch_result.save(save_path, quality=95)
                messagebox.showinfo("完成", f"图片已保存到：\n{save_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败：{e}")


def main():
    """主函数"""
    app = ModernImageApp()
    app.mainloop()


if __name__ == '__main__':
    main()
