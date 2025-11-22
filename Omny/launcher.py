import tkinter as tk
import time
import os
import math
import random
import sys

# Добавляем путь к src для импортов
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

class ParticleSystem:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles = []
        
    def create_particles(self, count):
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 4)
            speed = random.uniform(0.5, 2.0)
            life = random.uniform(50, 150)
            
            particle = self.canvas.create_oval(
                x, y, x+size, y+size,
                fill=self.get_random_blue(), outline=""
            )
            
            self.particles.append({
                'id': particle,
                'x': x, 'y': y,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'speed': speed,
                'life': life,
                'max_life': life,
                'size': size
            })
            
    def get_random_blue(self):
        blues = ['#3399ff', '#66b3ff', '#88ccff', '#00aaff', '#0088cc']
        return random.choice(blues)
            
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * particle['speed']
            particle['y'] += particle['vy'] * particle['speed']
            particle['life'] -= 1
            
            if particle['x'] <= 0 or particle['x'] >= self.width:
                particle['vx'] *= -1
            if particle['y'] <= 0 or particle['y'] >= self.height:
                particle['vy'] *= -1
                
            life_ratio = particle['life'] / particle['max_life']
            current_size = particle['size'] * life_ratio
            
            self.canvas.coords(particle['id'],
                             particle['x'], particle['y'],
                             particle['x'] + current_size, 
                             particle['y'] + current_size)
            
            if particle['life'] <= 0:
                self.canvas.delete(particle['id'])
                self.particles.remove(particle)
                
        if random.random() < 0.3:
            self.create_particles(1)

class AnimatedSplash:
    def __init__(self):
        self.splash = tk.Tk()
        self.splash.title("Omny Anti-AFK")
        self.splash.geometry("600x500")
        self.splash.overrideredirect(True)
        self.splash.attributes('-alpha', 0.0)
        self.splash.configure(bg='#0a0a1a')
        self.splash.attributes('-topmost', True)
        
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 500) // 2
        self.splash.geometry(f"600x500+{x}+{y}")
        
        self.canvas = tk.Canvas(self.splash, width=600, height=500, 
                               highlightthickness=0, bg='#0a0a1a')
        self.canvas.pack()
        
        self.particle_system = ParticleSystem(self.canvas, 600, 500)
        self.progress_value = 0
        self.animation_phase = 0
        self.animation_id = None
        
        self.setup_ui()
        self.fade_in()
        
    def fade_in(self):
        for i in range(0, 101, 5):
            alpha = i / 100
            self.splash.attributes('-alpha', alpha)
            self.splash.update()
            time.sleep(0.02)
        
        self.start_animations()
        
    def setup_ui(self):
        self.particle_system.create_particles(50)
        
        self.logo_text = self.canvas.create_text(300, 180, text="", 
                                                font=("Segoe UI", 36, "bold"),
                                                fill="#3399ff")
        
        self.subtitle_text = self.canvas.create_text(300, 230, text="", 
                                                    font=("Segoe UI", 16),
                                                    fill="#66b3ff")
        
        self.create_progress_bar()
        
        self.percent_text = self.canvas.create_text(300, 320, text="0%", 
                                                   font=("Segoe UI", 14, "bold"),
                                                   fill="#b3e0ff")
        
        self.status_text = self.canvas.create_text(300, 350, text="Initializing Core Systems...", 
                                                  font=("Segoe UI", 11),
                                                  fill="#88ccff")
        
        self.canvas.create_text(300, 480, text="Created by animerlock © 2025 • Premium Anti-AFK System", 
                               font=("Segoe UI", 9),
                               fill="#66aaff")
        
    def create_progress_bar(self):
        self.canvas.create_rectangle(100, 290, 500, 305, fill="#1a1a2e", outline="")
        self.progress_bar = self.canvas.create_rectangle(100, 290, 100, 305, 
                                                        fill="#3399ff", outline="")
        
    def typewriter_effect(self, text, text_id, delay=0.05, callback=None):
        displayed_text = ""
        for char in text:
            displayed_text += char
            self.canvas.itemconfig(text_id, text=displayed_text)
            self.splash.update()
            time.sleep(delay)
        if callback:
            callback()
            
    def start_animations(self):
        self.typewriter_effect("OMNY ANTI-AFK", self.logo_text, 0.08, 
                              lambda: self.typewriter_effect("PREMIUM EDITION", self.subtitle_text, 0.04, self.start_loading))
        
        self.animate_loop()
        
    def animate_loop(self):
        try:
            self.particle_system.update()
            self.animation_phase += 0.1
            
            glow_intensity = abs(math.sin(self.animation_phase * 2)) * 0.4 + 0.6
            self.pulse_logo(glow_intensity)
            
            if hasattr(self, 'progress_bar'):
                progress_width = 100 + (self.progress_value * 4)
                self.canvas.coords(self.progress_bar, 100, 290, progress_width, 305)
            
            # Сохраняем ID анимации для возможности отмены
            self.animation_id = self.splash.after(16, self.animate_loop)
        except tk.TclError:
            # Окно было закрыто, прекращаем анимацию
            return
        
    def pulse_logo(self, intensity):
        base_color = (51, 153, 255)
        r = min(255, int(base_color[0] * intensity))
        g = min(255, int(base_color[1] * intensity))
        b = min(255, int(base_color[2] * intensity))
        color = f'#{r:02x}{g:02x}{b:02x}'
        self.canvas.itemconfig(self.logo_text, fill=color)
        
    def start_loading(self):
        loading_sequence = [
            ("Loading AI Core...", 15),
            ("Initializing Neural Network...", 30),
            ("Configuring Game Detection...", 50),
            ("Optimizing Performance...", 70),
            ("Loading Security Protocols...", 85),
            ("Starting Omny Engine...", 95),
            ("Ready for Launch", 100)
        ]
        
        def update_loading():
            for text, target in loading_sequence:
                self.canvas.itemconfig(self.status_text, text=text)
                
                while self.progress_value < target:
                    self.progress_value += 1
                    self.canvas.itemconfig(self.percent_text, text=f"{self.progress_value}%")
                    self.splash.update()
                    time.sleep(0.02)
                    
            self.canvas.itemconfig(self.status_text, text="Launching Omny Anti-AFK...")
            time.sleep(0.8)
            self.launch_main_app()
            
        self.splash.after(100, update_loading)
        
    def launch_main_app(self):
        """Плавный переход к главному приложению"""
        try:
            # Отменяем анимацию чтобы избежать ошибок
            if self.animation_id:
                self.splash.after_cancel(self.animation_id)
            
            # Плавное затухание
            for i in range(100, -1, -5):
                alpha = i / 100
                self.splash.attributes('-alpha', alpha)
                self.splash.update()
                time.sleep(0.02)
            
            self.splash.destroy()
            
            # Импортируем и запускаем главное приложение
            from src.main_app import OmnyAntiAFK
            app = OmnyAntiAFK()
            app.run()
            
        except Exception as e:
            print(f"Error launching main app: {e}")
            # Fallback
            try:
                import subprocess
                subprocess.Popen([sys.executable, "src/main_app.py"], cwd=os.path.dirname(__file__))
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                input("Press Enter to exit...")

if __name__ == "__main__":
    splash = AnimatedSplash()
    splash.splash.mainloop()