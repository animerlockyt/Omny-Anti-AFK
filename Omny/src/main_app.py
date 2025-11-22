import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import sys
import json
from PIL import Image, ImageTk
import psutil

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from anti_afk import AntiAFK
from game_detector import GameDetector
from notifications import show_action_notification, show_system_notification
import styles

class GradientFrame(tk.Canvas):
    def __init__(self, parent, width, height, colors, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.colors = colors
        self.bind("<Configure>", self._draw_gradient)
        
    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width() or self.width
        height = self.winfo_height() or self.height
        
        for i in range(height):
            # Плавный градиент от цвета 1 к цвету 2
            ratio = i / height
            r = int(self.colors[0][0] * (1 - ratio) + self.colors[1][0] * ratio)
            g = int(self.colors[0][1] * (1 - ratio) + self.colors[1][1] * ratio)
            b = int(self.colors[0][2] * (1 - ratio) + self.colors[1][2] * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.create_line(0, i, width, i, fill=color, tags="gradient")

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=50, 
                 bg_color=styles.COLORS["accent"], hover_color=styles.COLORS["accent_hover"],
                 text_color="white", corner_radius=15):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=styles.COLORS["bg_primary"])
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.text = text
        self.is_hovered = False
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw_button()
        
    def draw_button(self, is_hover=None):
        if is_hover is not None:
            self.is_hovered = is_hover
            
        self.delete("all")
        
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # Рисуем кнопку с градиентом
        gradient_colors = [
            (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)),
            (max(0, int(color[1:3], 16) - 20), max(0, int(color[3:5], 16) - 20), max(0, int(color[5:7], 16) - 20))
        ]
        
        for i in range(self.height):
            ratio = i / self.height
            r = int(gradient_colors[0][0] * (1 - ratio) + gradient_colors[1][0] * ratio)
            g = int(gradient_colors[0][1] * (1 - ratio) + gradient_colors[1][1] * ratio)
            b = int(gradient_colors[0][2] * (1 - ratio) + gradient_colors[1][2] * ratio)
            grad_color = f'#{r:02x}{g:02x}{b:02x}'
            self.create_line(0, i, self.width, i, fill=grad_color)
        
        # Закругленные углы
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, self.corner_radius,
                               fill="", outline=styles.COLORS["border_light"], width=1)
        
        # Текст с тенью
        self.create_text(self.width//2 + 1, self.height//2 + 1, text=self.text,
                font=styles.FONTS["button"], fill="#4a4a4a")
        self.create_text(self.width//2, self.height//2, text=self.text,
                        font=styles.FONTS["button"], fill=self.text_color)
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)
        
    def on_enter(self, event):
        self.is_hovered = True
        self.draw_button()
        
    def on_leave(self, event):
        self.is_hovered = False
        self.draw_button()
        
    def on_click(self, event):
        self.command()
        
    def update_text(self, new_text):
        self.text = new_text
        self.draw_button()

class StatusIndicator(tk.Canvas):
    def __init__(self, parent, size=100, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        highlightthickness=0, bg=styles.COLORS["bg_secondary"], **kwargs)
        self.size = size
        self.status = "offline"
        
    def set_status(self, status):
        self.status = status
        self.draw_indicator()
        
    def draw_indicator(self):
        self.delete("all")
        
        center = self.size // 2
        radius = self.size // 2 - 10
        
        if self.status == "online":
            # Онлайн - зеленый с анимацией пульсации
            color = "#00ff00"
            glow_color = "#88ff88"
            
            # Внешний glow эффект
            for i in range(3):
                r = radius + i * 3
                self.create_oval(center-r, center-r, center+r, center+r,
                               outline=glow_color, width=1, fill="")
            
        else:
            # Офлайн - красный
            color = "#ff4444"
            glow_color = "#ff8888"
        
        # Основной круг
        self.create_oval(center-radius, center-radius, center+radius, center+radius,
                        fill=color, outline=glow_color, width=2)
        
        # Внутренний круг
        inner_radius = radius - 15
        self.create_oval(center-inner_radius, center-inner_radius, 
                        center+inner_radius, center+inner_radius,
                        fill=styles.COLORS["bg_secondary"], outline="")
        
        # Иконка
        icon_text = "🎮" if self.status == "online" else "⏸️"
        self.create_text(center, center, text=icon_text, 
                        font=("Segoe UI", 20),
                        fill=color)

class OmnyAntiAFK:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Omny Anti-AFK • Premium")
        self.root.geometry("800x900")
        self.root.minsize(750, 800)  # Минимальный размер окна
        self.root.configure(bg=styles.COLORS["bg_primary"])
        
        # Загрузка настроек
        self.settings_file = "omny_settings.json"
        self.load_settings()
        
        self.anti_afk = AntiAFK()
        self.game_detector = GameDetector()
        self.is_running = False
        self.current_game = "No game detected"
        self.game_status = "offline"
        self.action_count = 0
        
        self.setup_styles()
        self.setup_ui()
        self.start_game_detection()
        self.center_window()
        
    def load_settings(self):
        """Загрузка настроек из файла"""
        self.settings = {
            "interval": 25.0,
            "active_keys": ["W", "A", "S", "D", "SPACE"],
            "press_method": "hold",
            "random_variation": True,
            "notifications": True,
            "valorant_mode": True,
            "auto_start": False
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except:
            pass
            
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except:
            pass
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Кастомные стили для ttk виджетов
        style.configure("Custom.Horizontal.TScale",
                       background=styles.COLORS["bg_secondary"],
                       troughcolor=styles.COLORS["bg_tertiary"],
                       bordercolor=styles.COLORS["border"],
                       lightcolor=styles.COLORS["accent"],
                       darkcolor=styles.COLORS["accent"])
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def start_game_detection(self):
        self.game_detector.start_monitoring(self.on_game_detected)
        
    def on_game_detected(self, game_name):
        if game_name:
            self.current_game = game_name
            self.game_status = "online"
            self.update_game_display()
            
            if self.settings["auto_start"] and not self.is_running and game_name == "VALORANT":
                self.root.after(2000, self.start_anti_afk)
                
        else:
            self.current_game = "No game detected"
            self.game_status = "offline"
            self.update_game_display()
            
            if self.is_running:
                self.stop_anti_afk()
                show_system_notification("Game Closed", "Anti-AFK has been stopped")
        
    def setup_ui(self):
        # Header с градиентом
        self.setup_header()
        
        # Статус игры
        self.setup_game_status()
        
        # Панель управления
        self.setup_control_panel()
        
        # Настройки с вкладками
        self.setup_settings_notebook()
        
        # Футер
        self.setup_footer()
        
    def setup_header(self):
        header_frame = tk.Frame(self.root, bg=styles.COLORS["bg_primary"], height=160)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Градиентный фон
        gradient_colors = [
            (15, 30, 60),    # Темно-синий
            (10, 20, 40)     # Еще темнее
        ]
        
        self.header_canvas = GradientFrame(header_frame, 800, 160, gradient_colors, 
                                         bg=styles.COLORS["bg_primary"])
        self.header_canvas.pack(fill='both', expand=True)
        
        # Текст поверх градиента
        self.header_canvas.create_text(400, 50, text="OMNY ANTI-AFK", 
                                     font=("Segoe UI", 32, "bold"), 
                                     fill=styles.COLORS["accent"])
        
        self.header_canvas.create_text(400, 85, text="PREMIUM GAME UTILITY • OPTIMIZED FOR VALORANT", 
                                     font=("Segoe UI", 12), 
                                     fill=styles.COLORS["text_secondary"])
        
        # Статистика
        self.stats_text = self.header_canvas.create_text(400, 120, 
                                                       text="Actions: 0 | Status: Ready", 
                                                       font=("Segoe UI", 11),
                                                       fill=styles.COLORS["accent_light"])
        
        # Декоративные элементы
        self.create_header_decorations()
                
    def create_header_decorations(self):
        """Создает декоративные элементы в header"""
        # Левая декоративная линия
        for i in range(0, 160, 4):
            alpha = i / 160
            color_intensity = int(255 * alpha)
            color = f'#{color_intensity:02x}{color_intensity:02x}ff'
            self.header_canvas.create_line(50, i, 80, i, fill=color)
        
        # Правая декоративная линия
        for i in range(0, 160, 4):
            alpha = 1 - (i / 160)
            color_intensity = int(255 * alpha)
            color = f'#ff{color_intensity:02x}{color_intensity:02x}'
            self.header_canvas.create_line(720, i, 750, i, fill=color)
        
    def setup_game_status(self):
        status_frame = tk.Frame(self.root, bg=styles.COLORS["bg_secondary"], 
                               height=120)
        status_frame.pack(fill='x', padx=40, pady=10)
        status_frame.pack_propagate(False)
        
        # Индикатор статуса
        self.status_indicator = StatusIndicator(status_frame, size=80)
        self.status_indicator.place(x=40, y=20)
        
        # Информация о игре
        info_frame = tk.Frame(status_frame, bg=styles.COLORS["bg_secondary"])
        info_frame.place(x=150, y=25)
        
        tk.Label(info_frame, text="DETECTED GAME", 
                font=("Segoe UI", 11, "bold"), 
                fg=styles.COLORS["text_secondary"],
                bg=styles.COLORS["bg_secondary"]).pack(anchor='w')
        
        self.game_name_label = tk.Label(info_frame, 
                                       text=self.current_game,
                                       font=("Segoe UI", 22, "bold"), 
                                       fg=styles.COLORS["accent"],
                                       bg=styles.COLORS["bg_secondary"])
        self.game_name_label.pack(anchor='w', pady=(2, 0))
        
        self.game_status_label = tk.Label(info_frame, 
                                         text="Status: Offline",
                                         font=("Segoe UI", 10),
                                         fg=styles.COLORS["text_secondary"],
                                         bg=styles.COLORS["bg_secondary"])
        self.game_status_label.pack(anchor='w')
        
        # Дополнительная информация
        stats_frame = tk.Frame(status_frame, bg=styles.COLORS["bg_secondary"])
        stats_frame.place(x=450, y=35)
        
        self.session_stats = tk.Label(stats_frame, 
                                     text="Session: 0 actions\nUptime: 00:00:00",
                                     font=("Segoe UI", 9),
                                     fg=styles.COLORS["text_muted"],
                                     bg=styles.COLORS["bg_secondary"],
                                     justify='left')
        self.session_stats.pack(anchor='e')
        
        self.update_game_display()
        
    def update_game_display(self):
        self.game_name_label.config(text=self.current_game)
        
        status_text = "Online" if self.game_status == "online" else "Offline"
        status_color = "#00ff00" if self.game_status == "online" else "#ff4444"
        self.game_status_label.config(text=f"Status: {status_text}", fg=status_color)
        
        # Обновляем индикатор
        self.status_indicator.set_status(self.game_status)
        
    def setup_control_panel(self):
        control_frame = tk.Frame(self.root, bg=styles.COLORS["bg_secondary"], 
                               height=140)
        control_frame.pack(fill='x', padx=40, pady=10)
        control_frame.pack_propagate(False)
        
        # Градиентный фон для панели управления
        control_gradient = GradientFrame(control_frame, 800, 140, 
                                       [(42, 82, 152), (26, 51, 102)],
                                       bg=styles.COLORS["bg_secondary"])
        control_gradient.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Кнопка запуска
        self.control_button = ModernButton(control_gradient, "🚀 START ANTI-AFK", 
                                         self.toggle_anti_afk,
                                         width=320, height=70,
                                         bg_color=styles.COLORS["success"],
                                         hover_color="#00cc66")
        self.control_button.place(relx=0.5, rely=0.4, anchor='center')
        
        # Статистика
        stats_frame = tk.Frame(control_gradient, bg='#1a2a4a')
        stats_frame.place(relx=0.5, rely=0.85, anchor='center')
        
        self.stats_label = tk.Label(stats_frame, 
                                   text="Actions: 0 | Interval: 25.0s | Mode: Ready",
                                   font=("Segoe UI", 10),
                                   fg=styles.COLORS["text_secondary"],
                                   bg='#1a2a4a')
        self.stats_label.pack()
        
    def setup_settings_notebook(self):
        # Основной контейнер для настроек
        settings_container = tk.Frame(self.root, bg=styles.COLORS["bg_primary"])
        settings_container.pack(fill='both', expand=True, padx=40, pady=10)
        
        # Создаем Notebook (вкладки)
        style = ttk.Style()
        style.configure("Omny.TNotebook", 
                       background=styles.COLORS["bg_primary"],
                       borderwidth=0)
        style.configure("Omny.TNotebook.Tab", 
                       background=styles.COLORS["bg_tertiary"],
                       foreground=styles.COLORS["text_primary"],
                       focuscolor=styles.COLORS["bg_secondary"],
                       padding=[25, 8],
                       font=("Segoe UI", 10, "bold"))
        
        style.map("Omny.TNotebook.Tab",
                 background=[("selected", styles.COLORS["accent"]),
                           ("active", styles.COLORS["bg_secondary"])],
                 foreground=[("selected", "white"),
                           ("active", styles.COLORS["text_primary"])])
        
        notebook = ttk.Notebook(settings_container, style="Omny.TNotebook")
        notebook.pack(fill='both', expand=True)
        
        # Создаем вкладки
        basic_frame = ttk.Frame(notebook, style="Omny.TFrame")
        advanced_frame = ttk.Frame(notebook, style="Omny.TFrame")
        valorant_frame = ttk.Frame(notebook, style="Omny.TFrame")
        
        self.create_basic_tab(basic_frame)
        self.create_advanced_tab(advanced_frame)
        self.create_valorant_tab(valorant_frame)
        
        notebook.add(basic_frame, text="⚙️ Basic Settings")
        notebook.add(advanced_frame, text="🔧 Advanced")
        notebook.add(valorant_frame, text="🎯 VALORANT")
        
        # Настраиваем стиль для фреймов вкладок
        style.configure("Omny.TFrame", background=styles.COLORS["bg_secondary"])
        
    def create_basic_tab(self, parent):
        # Интервал
        interval_frame = tk.Frame(parent, bg=styles.COLORS["bg_secondary"])
        interval_frame.pack(fill='x', pady=20, padx=20)
        
        tk.Label(interval_frame, text="ACTION INTERVAL", 
                font=("Segoe UI", 13, "bold"),
                fg=styles.COLORS["text_primary"],
                bg=styles.COLORS["bg_secondary"]).pack(anchor='w')
        
        tk.Label(interval_frame, text="Time between key presses (seconds)", 
                font=("Segoe UI", 10),
                fg=styles.COLORS["text_secondary"],
                bg=styles.COLORS["bg_secondary"]).pack(anchor='w', pady=(0, 10))
        
        self.interval_var = tk.DoubleVar(value=self.settings["interval"])
        
        # Кастомизированный слайдер
        interval_scale = ttk.Scale(interval_frame, from_=5, to=120, 
                                  orient='horizontal', variable=self.interval_var,
                                  style="Custom.Horizontal.TScale",
                                  length=650)
        interval_scale.pack(fill='x', pady=10)
        
        # Контейнер для значений
        values_frame = tk.Frame(interval_frame, bg=styles.COLORS["bg_secondary"])
        values_frame.pack(fill='x')
        
        tk.Label(values_frame, text="5s", 
                font=("Segoe UI", 9),
                fg=styles.COLORS["text_muted"],
                bg=styles.COLORS["bg_secondary"]).pack(side='left')
        
        self.interval_label = tk.Label(values_frame, 
                                      text=f"Current: {self.interval_var.get():.1f}s",
                                      font=("Segoe UI", 10, "bold"),
                                      fg=styles.COLORS["accent"],
                                      bg=styles.COLORS["bg_secondary"])
        self.interval_label.pack(side='left', padx=20)
        
        tk.Label(values_frame, text="120s", 
                font=("Segoe UI", 9),
                fg=styles.COLORS["text_muted"],
                bg=styles.COLORS["bg_secondary"]).pack(side='right')
        
        # Связываем изменение слайдера с обновлением
        self.interval_var.trace('w', self.on_interval_change)
        
        # Клавиши
        keys_frame = tk.Frame(parent, bg=styles.COLORS["bg_secondary"])
        keys_frame.pack(fill='x', pady=20, padx=20)
        
        tk.Label(keys_frame, text="ACTIVE KEYS", 
                font=("Segoe UI", 13, "bold"),
                fg=styles.COLORS["text_primary"],
                bg=styles.COLORS["bg_secondary"]).pack(anchor='w')
        
        keys_container = tk.Frame(keys_frame, bg=styles.COLORS["bg_secondary"])
        keys_container.pack(fill='x', pady=15)
        
        self.keys_vars = {}
        keys = [
            ('W', 'Move Forward'), 
            ('A', 'Move Left'), 
            ('S', 'Move Back'), 
            ('D', 'Move Right'), 
            ('SPACE', 'Jump')
        ]
        
        for i, (key, description) in enumerate(keys):
            frame = tk.Frame(keys_container, bg=styles.COLORS["bg_secondary"])
            frame.grid(row=0, column=i, padx=25, pady=5, sticky='w')
            
            var = tk.BooleanVar(value=key in self.settings["active_keys"])
            self.keys_vars[key] = var
            
            # Стилизованный чекбокс
            cb = tk.Checkbutton(frame, text=f" {key}", variable=var,
                              font=("Segoe UI", 11, "bold"),
                              fg=styles.COLORS["text_primary"],
                              bg=styles.COLORS["bg_secondary"],
                              selectcolor=styles.COLORS["accent"],
                              activebackground=styles.COLORS["bg_secondary"],
                              activeforeground=styles.COLORS["text_primary"],
                              command=self.on_keys_change)
            cb.pack(side='left')
            
            # Описание
            tk.Label(frame, text=description,
                   font=("Segoe UI", 9),
                   fg=styles.COLORS["text_secondary"],
                   bg=styles.COLORS["bg_secondary"]).pack(side='left', padx=(5, 0))
            
    def create_advanced_tab(self, parent):
        # Метод нажатий
        method_frame = tk.Frame(parent, bg=styles.COLORS["bg_secondary"])
        method_frame.pack(fill='x', pady=25, padx=20)
        
        tk.Label(method_frame, text="KEY PRESS METHOD", 
                font=("Segoe UI", 13, "bold"),
                fg=styles.COLORS["text_primary"],
                bg=styles.COLORS["bg_secondary"]).pack(anchor='w')
        
        self.method_var = tk.StringVar(value=self.settings["press_method"])
        
        methods_frame = tk.Frame(method_frame, bg=styles.COLORS["bg_secondary"])
        methods_frame.pack(fill='x', pady=15)
        
        methods = [
            ("Hold & Release (Recommended)", "Natural key press and release", "hold"),
            ("Quick Tap", "Instant key tap", "tap"), 
            ("Randomized (Stealth)", "Random patterns for maximum stealth", "random")
        ]
        
        for text, description, value in methods:
            method_item = tk.Frame(methods_frame, bg=styles.COLORS["bg_secondary"])
            method_item.pack(fill='x', pady=8)
            
            rb = tk.Radiobutton(method_item, text=text, variable=self.method_var, 
                               value=value,
                               font=("Segoe UI", 11),
                               fg=styles.COLORS["text_primary"],
                               bg=styles.COLORS["bg_secondary"],
                               selectcolor=styles.COLORS["accent"],
                               activebackground=styles.COLORS["bg_secondary"],
                               command=self.on_method_change)
            rb.pack(anchor='w')
            
            tk.Label(method_item, text=description,
                   font=("Segoe UI", 9),
                   fg=styles.COLORS["text_secondary"],
                   bg=styles.COLORS["bg_secondary"]).pack(anchor='w', padx=(25, 0))
        
        # Дополнительные настройки
        advanced_frame = tk.Frame(parent, bg=styles.COLORS["bg_secondary"])
        advanced_frame.pack(fill='x', pady=20, padx=20)
        
        tk.Label(advanced_frame, text="ADVANCED OPTIONS", 
                font=("Segoe UI", 13, "bold"),
                fg=styles.COLORS["text_primary"],
                bg=styles.COLORS["bg_secondary"]).pack(anchor='w')
        
        options_frame = tk.Frame(advanced_frame, bg=styles.COLORS["bg_secondary"])
        options_frame.pack(fill='x', pady=15)
        
        self.random_var = tk.BooleanVar(value=self.settings["random_variation"])
        random_cb = tk.Checkbutton(options_frame, text="Random interval variation (±20%)", 
                                 variable=self.random_var,
                                 font=("Segoe UI", 11),
                                 fg=styles.COLORS["text_primary"],
                                 bg=styles.COLORS["bg_secondary"],
                                 selectcolor=styles.COLORS["accent"],
                                 command=self.on_random_change)
        random_cb.pack(anchor='w', pady=5)
        
        self.auto_start_var = tk.BooleanVar(value=self.settings["auto_start"])
        auto_cb = tk.Checkbutton(options_frame, text="Auto-start when VALORANT detected", 
                                variable=self.auto_start_var,
                                font=("Segoe UI", 11),
                                fg=styles.COLORS["text_primary"],
                                bg=styles.COLORS["bg_secondary"],
                                selectcolor=styles.COLORS["accent"],
                                command=self.on_auto_start_change)
        auto_cb.pack(anchor='w', pady=5)
        
        self.notifications_var = tk.BooleanVar(value=self.settings["notifications"])
        notif_cb = tk.Checkbutton(options_frame, text="Show desktop notifications", 
                                 variable=self.notifications_var,
                                 font=("Segoe UI", 11),
                                 fg=styles.COLORS["text_primary"],
                                 bg=styles.COLORS["bg_secondary"],
                                 selectcolor=styles.COLORS["accent"],
                                 command=self.on_notifications_change)
        notif_cb.pack(anchor='w', pady=5)
        
    def create_valorant_tab(self, parent):
        # Основной контейнер
        main_container = tk.Frame(parent, bg=styles.COLORS["bg_secondary"])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Заголовок
        header_frame = tk.Frame(main_container, bg=styles.COLORS["bg_secondary"])
        header_frame.pack(fill='x', pady=(0, 25))
        
        tk.Label(header_frame, text="🎯 VALORANT OPTIMIZATION", 
                font=("Segoe UI", 18, "bold"),
                fg=styles.COLORS["accent"],
                bg=styles.COLORS["bg_secondary"]).pack()
        
        tk.Label(header_frame, text="Special settings optimized for VALORANT's Vanguard anti-cheat", 
                font=("Segoe UI", 11),
                fg=styles.COLORS["text_secondary"],
                bg=styles.COLORS["bg_secondary"]).pack(pady=(5, 0))
        
        # Контент в две колонки
        content_frame = tk.Frame(main_container, bg=styles.COLORS["bg_secondary"])
        content_frame.pack(fill='both', expand=True)
        
        # Левая колонка - настройки
        settings_col = tk.Frame(content_frame, bg=styles.COLORS["bg_secondary"])
        settings_col.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # VALORANT специфичные настройки
        settings_frame = tk.Frame(settings_col, bg=styles.COLORS["bg_tertiary"])
        settings_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(settings_frame, text="VALORANT SETTINGS", 
                font=("Segoe UI", 12, "bold"),
                fg=styles.COLORS["text_primary"],
                bg=styles.COLORS["bg_tertiary"]).pack(anchor='w', pady=(15, 10), padx=15)
        
        self.valorant_mode_var = tk.BooleanVar(value=self.settings["valorant_mode"])
        valorant_cb = tk.Checkbutton(settings_frame, text="Enable VALORANT optimization mode", 
                                   variable=self.valorant_mode_var,
                                   font=("Segoe UI", 11),
                                   fg=styles.COLORS["text_primary"],
                                   bg=styles.COLORS["bg_tertiary"],
                                   selectcolor=styles.COLORS["accent"],
                                   command=self.on_valorant_mode_change)
        valorant_cb.pack(anchor='w', pady=8, padx=15)
        
        # Правая колонка - советы
        tips_col = tk.Frame(content_frame, bg=styles.COLORS["bg_secondary"])
        tips_col.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # Рекомендации для VALORANT
        tips_frame = tk.Frame(tips_col, bg=styles.COLORS["bg_tertiary"])
        tips_frame.pack(fill='both', expand=True)
        
        tk.Label(tips_frame, text="💡 OPTIMIZATION TIPS", 
                font=("Segoe UI", 12, "bold"),
                fg=styles.COLORS["text_primary"],
                bg=styles.COLORS["bg_tertiary"]).pack(anchor='w', pady=(15, 10), padx=15)
        
        tips_text = """✅ Recommended Settings:

• Interval: 20-40 seconds
• Method: Hold & Release  
• Enable random variation
• Works in all game modes
• Vanguard compatible

⚠️ Important Notes:

• Stay in game client (not menus)
• Avoid very short intervals
• Test in custom games first
• Monitor game performance"""

        tips_content = tk.Frame(tips_frame, bg=styles.COLORS["bg_tertiary"])
        tips_content.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        tips_label = tk.Label(tips_content, text=tips_text,
                            font=("Segoe UI", 10),
                            fg=styles.COLORS["text_primary"],
                            bg=styles.COLORS["bg_tertiary"],
                            justify='left')
        tips_label.pack(anchor='w')
        
    def setup_footer(self):
        footer_frame = tk.Frame(self.root, bg=styles.COLORS["bg_primary"], height=50)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        # Градиентный фон футера
        footer_gradient = GradientFrame(footer_frame, 800, 50, 
                                      [(15, 30, 60), (8, 16, 32)],
                                      bg=styles.COLORS["bg_primary"])
        footer_gradient.pack(fill='both', expand=True)
        
        # Текст футера
        footer_gradient.create_text(400, 15, 
                                  text="© 2025 animerlock • Premium Anti-AFK System • Optimized for VALORANT", 
                                  font=("Segoe UI", 9),
                                  fill=styles.COLORS["text_muted"])
        
        # Кнопка сохранения настроек
        save_btn = ModernButton(footer_gradient, "💾 Save Settings", self.save_settings,
                               width=120, height=30,
                               bg_color=styles.COLORS["accent"],
                               hover_color=styles.COLORS["accent_hover"])
        save_btn.place(relx=0.85, rely=0.5, anchor='center')
        
    def on_interval_change(self, *args):
        self.settings["interval"] = self.interval_var.get()
        self.interval_label.config(text=f"Current: {self.interval_var.get():.1f}s")
        self.update_stats()
        
    def on_keys_change(self):
        self.settings["active_keys"] = [key for key, var in self.keys_vars.items() if var.get()]
        
    def on_method_change(self):
        self.settings["press_method"] = self.method_var.get()
        
    def on_random_change(self):
        self.settings["random_variation"] = self.random_var.get()
        
    def on_auto_start_change(self):
        self.settings["auto_start"] = self.auto_start_var.get()
        
    def on_notifications_change(self):
        self.settings["notifications"] = self.notifications_var.get()
        
    def on_valorant_mode_change(self):
        self.settings["valorant_mode"] = self.valorant_mode_var.get()
        
    def update_stats(self):
        if hasattr(self, 'stats_label'):
            status = "ACTIVE" if self.is_running else "READY"
            self.stats_label.config(
                text=f"Actions: {self.action_count} | Interval: {self.settings['interval']:.1f}s | Mode: {status}"
            )
        
    def toggle_anti_afk(self):
        if not self.is_running:
            self.start_anti_afk()
        else:
            self.stop_anti_afk()
            
    def start_anti_afk(self):
        if not self.game_detector.is_game_running():
            messagebox.showerror("Error", 
                               "No game detected! Please start VALORANT or your game first.")
            return
            
        if not any(var.get() for var in self.keys_vars.values()):
            messagebox.showerror("Error", 
                               "Please select at least one active key.")
            return
            
        self.is_running = True
        self.control_button.update_text("🛑 STOP ANTI-AFK")
        self.control_button.bg_color = styles.COLORS["stop"]
        self.control_button.hover_color = styles.COLORS["stop_hover"]
        self.control_button.draw_button()
        
        # Применяем настройки к Anti-AFK
        self.anti_afk.interval = self.settings["interval"]
        self.anti_afk.active_keys = self.settings["active_keys"]
        self.anti_afk.press_method = self.settings["press_method"]
        self.anti_afk.random_variation = self.settings["random_variation"]
        self.anti_afk.valorant_mode = self.settings["valorant_mode"]
        self.anti_afk.notifications = self.settings["notifications"]
        self.anti_afk.action_callback = self.on_action_performed
        
        # Запуск в отдельном потоке
        self.afk_thread = threading.Thread(target=self.anti_afk.start)
        self.afk_thread.daemon = True
        self.afk_thread.start()
        
        self.update_stats()
        if self.settings["notifications"]:
            show_system_notification("Anti-AFK Started", 
                       f"Active for {self.current_game}\n"
                       f"Interval: {self.settings['interval']:.1f}s",
                       3000)
        
    def stop_anti_afk(self):
        self.is_running = False
        self.anti_afk.stop()
        self.control_button.update_text("🚀 START ANTI-AFK")
        self.control_button.bg_color = styles.COLORS["success"]
        self.control_button.hover_color = "#00cc66"
        self.control_button.draw_button()
        
        self.update_stats()
        if self.settings["notifications"]:
            show_system_notification("Anti-AFK Stopped", "System has been deactivated")
        
    def on_action_performed(self, key_name, action_type):
        """Callback при выполнении действия"""
        self.action_count += 1
        self.update_stats()
        
    def save_settings(self):
        self.save_settings()
        if self.settings["notifications"]:
            show_system_notification("Settings Saved", "All settings have been saved successfully")
        
    def run(self):
        # Плавное появление
        self.root.attributes('-alpha', 0.0)
        self.root.after(100, self.fade_in_main_window)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def fade_in_main_window(self):
        for i in range(0, 101, 10):
            alpha = i / 100
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(0.02)

    def on_closing(self):
        if self.is_running:
            if messagebox.askokcancel("Quit", "Anti-AFK is still running. Are you sure you want to quit?"):
                self.stop_anti_afk()
                self.game_detector.stop_monitoring()
                self.save_settings()
                self.fade_out_and_quit()
        else:
            self.game_detector.stop_monitoring()
            self.save_settings()
            self.fade_out_and_quit()
            
    def fade_out_and_quit(self):
        for i in range(100, -1, -10):
            alpha = i / 100
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(0.02)
        self.root.destroy()

if __name__ == "__main__":
    app = OmnyAntiAFK()
    app.run()