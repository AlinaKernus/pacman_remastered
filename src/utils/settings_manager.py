"""
Менеджер для сохранения и загрузки настроек игры
"""
import json
import os
import sys

# For exe: save settings in user directory, not in temp folder
if getattr(sys, 'frozen', False):
    # Running in exe - save to user's AppData or home directory
    if sys.platform == 'win32':
        settings_dir = os.path.join(os.environ.get('APPDATA', ''), 'PacmanRemastered')
    else:
        settings_dir = os.path.join(os.path.expanduser('~'), '.pacman_remastered')
    os.makedirs(settings_dir, exist_ok=True)
    SETTINGS_FILE = os.path.join(settings_dir, "settings.json")
else:
    # Running in dev - save in project root
    SETTINGS_FILE = "settings.json"

class SettingsManager:
    """Класс для управления сохранением и загрузкой настроек"""
    
    def __init__(self, settings_file=SETTINGS_FILE):
        self.settings_file = settings_file
        self.default_settings = {
            "music_volume": 0.5,
            "sound_volume": 1.0,
            "music_muted": False,
            "sounds_muted": False,
            "theme": 1
        }
    
    def load_settings(self):
        """Загружает настройки из файла"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Объединяем с дефолтными настройками на случай если какие-то отсутствуют
                    merged_settings = self.default_settings.copy()
                    merged_settings.update(settings)
                    return merged_settings
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка при загрузке настроек: {e}")
                return self.default_settings.copy()
        return self.default_settings.copy()
    
    def save_settings(self, settings):
        """Сохраняет настройки в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Ошибка при сохранении настроек: {e}")
            return False
    
    def get_setting(self, key, default=None):
        """Получает значение настройки"""
        settings = self.load_settings()
        return settings.get(key, default if default is not None else self.default_settings.get(key))
    
    def set_setting(self, key, value):
        """Устанавливает значение настройки и сохраняет"""
        settings = self.load_settings()
        settings[key] = value
        self.save_settings(settings)
        return True
    
    def update_settings(self, **kwargs):
        """Обновляет несколько настроек одновременно"""
        settings = self.load_settings()
        settings.update(kwargs)
        self.save_settings(settings)
        return True


# Глобальный экземпляр менеджера настроек
settings_manager = SettingsManager()

