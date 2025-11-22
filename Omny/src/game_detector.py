import psutil
import time
import threading

class GameDetector:
    def __init__(self):
        self.supported_games = {
            'VALORANT': ['valorant.exe', 'valorant-win64-shipping.exe'],
            'CS2': ['cs2.exe', 'counterstrike2.exe'],
            'Overwatch': ['overwatch.exe', 'overwatch_dx12.exe'],
            'Apex Legends': ['r5apex.exe'],
            'Fortnite': ['fortnite.exe', 'fortnitelauncher.exe'],
            'Call of Duty': ['modernwarfare.exe', 'cod.exe'],
            'Rainbow Six': ['rainbowsix.exe', 'rainbowsix_vulkan.exe']
        }
        
        self.detected_game = None
        self.is_monitoring = False
        self.callback = None
        
    def start_monitoring(self, callback=None):
        """Запуск мониторинга игр"""
        self.callback = callback
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.is_monitoring = False
        
    def _monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.is_monitoring:
            current_game = self.detect_running_game()
            
            # Если состояние игры изменилось
            if current_game != self.detected_game:
                self.detected_game = current_game
                if self.callback:
                    self.callback(current_game)
            
            time.sleep(2)  # Проверка каждые 2 секунды
            
    def detect_running_game(self):
        """Обнаружение запущенных игр"""
        for process in psutil.process_iter(['pid', 'name']):
            try:
                process_name = process.info['name'].lower()
                
                for game_name, process_list in self.supported_games.items():
                    for game_process in process_list:
                        if game_process.lower() in process_name:
                            return game_name
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return None
    
    def is_game_running(self, game_name=None):
        """Проверка запущена ли конкретная игра"""
        if game_name:
            return self.detected_game == game_name
        return self.detected_game is not None
    
    def get_detected_game(self):
        """Получить название обнаруженной игры"""
        return self.detected_game