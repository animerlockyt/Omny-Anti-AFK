import tkinter as tk
from tkinter import ttk
import time
import threading
from PIL import Image, ImageTk
import styles

class NotificationManager:
    def __init__(self):
        self.notification_window = None
        self.is_showing = False
        self.current_duration = 3000  # значение по умолчанию
        
    def show_notification(self, title, message, duration=3000):
        """Показать уведомление"""
        if self.is_showing:
            self.hide_notification()
            
        self.current_duration = duration
        threading.Thread(target=self.create_notification_window, 
                        args=(title, message, duration), daemon=True).start()
    
    def create_notification_window(self, title, message, duration):
        """Создать окно уведомления"""
        self.is_showing = True
        
        # Создаем окно уведомления
        self.notification_window = tk.Toplevel()
        self.notification_window.overrideredirect(True)
        self.notification_window.attributes('-topmost', True)
        self.notification_window.attributes('-alpha', 0.0)
        
        # Позиционируем в правом верхнем углу
        screen_width = self.notification_window.winfo_screenwidth()
        screen_height = self.notification_window.winfo_screenheight()
        
        window_width = 350
        window_height = 120
        
        x = screen_width - window_width - 20
        y = 50
        
        self.notification_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        self.notification_window.configure(bg=styles.COLORS["bg_secondary"])
        
        # Настраиваем UI
        self.setup_notification_ui(title, message, duration)  # передаем duration
        
        # Плавное появление
        self.fade_in()
        
        # Автоматическое закрытие через duration миллисекунд
        self.notification_window.after(duration, self.fade_out)
    
    def setup_notification_ui(self, title, message, duration):  # добавил параметр duration
        """Настройка интерфейса уведомления"""
        if not self.notification_window:
            return
            
        # Основной фрейм
        main_frame = tk.Frame(self.notification_window, 
                             bg=styles.COLORS["bg_secondary"],
                             relief='raised', 
                             borderwidth=1)
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Header с градиентом
        header_frame = tk.Frame(main_frame, 
                               bg=styles.COLORS["accent"], 
                               height=30)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Заголовок
        title_label = tk.Label(header_frame, 
                              text=title,
                              font=("Segoe UI", 11, "bold"),
                              fg="white",
                              bg=styles.COLORS["accent"])
        title_label.pack(side='left', padx=15, pady=5)
        
        # Кнопка закрытия
        close_btn = tk.Label(header_frame, 
                           text="×", 
                           font=("Segoe UI", 16, "bold"),
                           fg="white",
                           bg=styles.COLORS["accent"],
                           cursor="hand2")
        close_btn.pack(side='right', padx=10)
        close_btn.bind("<Button-1>", lambda e: self.fade_out())
        
        # Сообщение
        message_label = tk.Label(main_frame,
                                text=message,
                                font=("Segoe UI", 10),
                                fg=styles.COLORS["text_primary"],
                                bg=styles.COLORS["bg_secondary"],
                                wraplength=300,
                                justify='left')
        message_label.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Прогрессбар для индикации времени
        progress_frame = tk.Frame(main_frame, 
                                 bg=styles.COLORS["bg_secondary"],
                                 height=4)
        progress_frame.pack(fill='x', side='bottom')
        progress_frame.pack_propagate(False)
        
        self.progress_bar = tk.Frame(progress_frame, 
                                   bg=styles.COLORS["success"],
                                   height=4)
        self.progress_bar.pack(fill='x')
        
        # Анимация прогрессбара
        self.animate_progress_bar(duration)  # теперь duration определен
    
    def animate_progress_bar(self, duration):
        """Анимация прогрессбара"""
        if not self.notification_window:
            return
            
        steps = 100
        interval = duration // steps
        
        def update_progress(step):
            if not self.notification_window or not self.is_showing:
                return
                
            # Обновляем ширину прогрессбара
            progress_width = int(350 * (steps - step) / steps)
            self.progress_bar.config(width=progress_width)
            
            if step < steps:
                self.notification_window.after(interval, update_progress, step + 1)
        
        update_progress(0)
    
    def fade_in(self):
        """Плавное появление"""
        if not self.notification_window:
            return
            
        for i in range(0, 101, 20):
            if not self.notification_window:
                break
            alpha = i / 100
            self.notification_window.attributes('-alpha', alpha)
            self.notification_window.update()
            time.sleep(0.02)
    
    def fade_out(self):
        """Плавное исчезновение"""
        if not self.notification_window:
            return
            
        for i in range(100, -1, -20):
            if not self.notification_window:
                break
            alpha = i / 100
            self.notification_window.attributes('-alpha', alpha)
            self.notification_window.update()
            time.sleep(0.02)
        
        self.hide_notification()
    
    def hide_notification(self):
        """Скрыть уведомление"""
        self.is_showing = False
        if self.notification_window:
            self.notification_window.destroy()
            self.notification_window = None

# Глобальный менеджер уведомлений
notification_manager = NotificationManager()

def show_system_notification(title, message, duration=3000):
    """Показать системное уведомление"""
    notification_manager.show_notification(title, message, duration)

def show_action_notification(action_type, key_name, interval):
    """Показать уведомление о действии"""
    message = f"Pressed: {key_name}\nNext action in: {interval:.1f}s"
    show_system_notification(f"Anti-AFK: {action_type}", message, 2000)