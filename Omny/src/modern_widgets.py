import tkinter as tk
from tkinter import ttk
import math

class ModernSlider(tk.Canvas):
    def __init__(self, parent, from_=0, to=100, initial_value=50, 
                 width=300, height=60, command=None, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg='#0a0a1a')
        
        self.from_ = from_
        self.to = to
        self.value = initial_value
        self.command = command
        self.width = width
        self.height = height
        self.is_dragging = False
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw_slider()
        
    def draw_slider(self):
        self.delete("all")
        
        # Фон слайдера
        track_height = 6
        track_y = self.height // 2 - track_height // 2
        
        # Трек
        self.create_rounded_rect(10, track_y, self.width-10, track_y+track_height, 3,
                               fill='#1a1a2e', outline='')
        
        # Заполненная часть
        fill_width = (self.value - self.from_) / (self.to - self.from_) * (self.width - 20)
        self.create_rounded_rect(10, track_y, 10 + fill_width, track_y+track_height, 3,
                               fill='#3399ff', outline='')
        
        # Бегунок
        thumb_x = 10 + fill_width
        thumb_radius = 12
        
        # Градиентный эффект для бегунка
        self.create_oval(thumb_x-thumb_radius, track_y-thumb_radius,
                        thumb_x+thumb_radius, track_y+thumb_radius,
                        fill='#3399ff', outline='#66b3ff', width=2)
        
        # Внутренний круг
        self.create_oval(thumb_x-thumb_radius+4, track_y-thumb_radius+4,
                        thumb_x+thumb_radius-4, track_y+thumb_radius-4,
                        fill='#0a0a1a', outline='')
        
        # Текст значения
        self.create_text(self.width//2, 20, text=f"{self.value:.1f}s", 
                        font=('Segoe UI', 10, 'bold'), fill='#b3e0ff')
        
        # Подписи
        self.create_text(10, self.height-10, text=f"{self.from_}s", 
                        font=('Segoe UI', 8), fill='#66aaff', anchor='w')
        self.create_text(self.width-10, self.height-10, text=f"{self.to}s", 
                        font=('Segoe UI', 8), fill='#66aaff', anchor='e')
        
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
        
    def on_click(self, event):
        self.is_dragging = True
        self.update_value(event.x)
        
    def on_drag(self, event):
        if self.is_dragging:
            self.update_value(event.x)
            
    def on_release(self, event):
        self.is_dragging = False
        
    def update_value(self, x):
        # Преобразование координаты X в значение
        track_width = self.width - 20
        relative_x = max(0, min(track_width, x - 10))
        self.value = self.from_ + (relative_x / track_width) * (self.to - self.from_)
        
        self.draw_slider()
        
        if self.command:
            self.command(self.value)
            
    def set_value(self, value):
        self.value = max(self.from_, min(self.to, value))
        self.draw_slider()

class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=60, height=30, initial_state=False, command=None):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg='#0a0a1a')
        
        self.state = initial_state
        self.command = command
        self.width = width
        self.height = height
        
        self.bind("<Button-1>", self.toggle)
        self.draw_switch()
        
    def draw_switch(self):
        self.delete("all")
        
        # Фон переключателя
        bg_color = '#3399ff' if self.state else '#1a1a2e'
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 15,
                               fill=bg_color, outline='#2a4a7a')
        
        # Бегунок
        thumb_pos = self.width - 18 if self.state else 18
        self.create_oval(thumb_pos-12, self.height//2-12,
                        thumb_pos+12, self.height//2+12,
                        fill='#ffffff', outline='#66b3ff')
        
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
        
    def toggle(self, event=None):
        self.state = not self.state
        self.draw_switch()
        
        if self.command:
            self.command(self.state)