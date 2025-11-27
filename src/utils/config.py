class Config:
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080
    CURRENT_THEME = 1  # Текущая выбранная тема (1-5)
    
    @staticmethod
    def load_from_settings():
        """Загружает настройки из файла"""
        from .settings_manager import settings_manager
        settings = settings_manager.load_settings()
        Config.CURRENT_THEME = settings.get("theme", 1)