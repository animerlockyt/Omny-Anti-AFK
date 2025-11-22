import time
import random
import threading
from pynput import keyboard
from pynput.keyboard import Key, Listener
from notifications import show_action_notification, show_system_notification

class AntiAFK:
    def __init__(self):
        self.interval = 25.0
        self.active_keys = ['W', 'A', 'S', 'D', 'SPACE']
        self.press_method = "hold"
        self.random_variation = True
        self.key_hold_time = 0.1
        self.valorant_mode = True
        self.notifications = True
        self.is_running = False
        self.controller = keyboard.Controller()
        self.action_callback = None
        
        self.key_mapping = {
            'W': 'w',
            'A': 'a', 
            'S': 's',
            'D': 'd',
            'SPACE': Key.space
        }
        
        self.action_count = 0
        self.last_actions = []
        
    def start(self):
        self.is_running = True
        self.afk_loop()
        
    def stop(self):
        self.is_running = False
        
    def press_key(self, key, key_name):
        try:
            if self.press_method == "hold":
                # Для VALORANT используем более естественное нажатие
                if self.valorant_mode:
                    # Случайная небольшая задержка перед нажатием
                    time.sleep(random.uniform(0.02, 0.08))
                    
                self.controller.press(key)
                
                # Время удержания с небольшими вариациями
                hold_time = self.key_hold_time * random.uniform(0.8, 1.2)
                time.sleep(hold_time)
                
                self.controller.release(key)
                
                action_type = "hold"
                
            elif self.press_method == "tap":
                self.controller.tap(key)
                action_type = "tap"
                
            else:  # random
                if random.random() > 0.3:
                    self.controller.press(key)
                    time.sleep(0.05 + random.uniform(0, 0.1))
                    self.controller.release(key)
                    action_type = "hold"
                else:
                    self.controller.tap(key)
                    action_type = "tap"
            
            self.action_count += 1
            
            # Логируем действие
            action_info = f"Pressed {key_name} ({action_type})"
            self.last_actions.append(action_info)
            if len(self.last_actions) > 5:
                self.last_actions.pop(0)
                
            # Уведомление
            if self.notifications:
                show_action_notification(key_name, action_type)
                
            # Callback
            if self.action_callback:
                self.action_callback(key_name, action_type)
                
            print(f"Action #{self.action_count}: {action_info}")
            
        except Exception as e:
            print(f"Error pressing key {key_name}: {e}")
            
    def afk_loop(self):
        last_action_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            time_since_last_action = current_time - last_action_time
            
            # Вычисляем текущий интервал с учетом вариаций
            current_interval = self.interval
            if self.random_variation:
                current_interval *= random.uniform(0.8, 1.2)
            
            if time_since_last_action >= current_interval:
                if self.active_keys:
                    # Выбираем случайную клавишу
                    key_name = random.choice(self.active_keys)
                    key = self.key_mapping.get(key_name)
                    
                    if key:
                        self.press_key(key, key_name)
                        last_action_time = current_time
                
            # Небольшая пауза чтобы не нагружать CPU
            time.sleep(0.1)