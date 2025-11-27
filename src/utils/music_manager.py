"""
Менеджер для управления музыкой и звуками
"""
import pygame
import os
from .settings_manager import settings_manager

class MusicManager:
    """Класс для управления музыкой и звуками игры"""
    
    def __init__(self):
        # Загружаем настройки из файла
        settings = settings_manager.load_settings()
        self.music_volume = settings.get("music_volume", 0.5)  # Громкость музыки (0.0 - 1.0)
        self.sound_volume = settings.get("sound_volume", 1.0)  # Громкость звуковых эффектов (0.0 - 1.0)
        self.music_muted = settings.get("music_muted", False)  # Флаг мута музыки
        self.sounds_muted = settings.get("sounds_muted", False)  # Флаг мута звуков
        self._saved_volume = self.music_volume  # Сохраненная громкость перед мутом
        
        # Инициализируем mixer если еще не инициализирован
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Применяем загруженные настройки
        if self.music_muted:
            pygame.mixer.music.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def set_music_volume(self, volume):
        """Устанавливает громкость музыки (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if not self.music_muted:
            pygame.mixer.music.set_volume(self.music_volume)
        # Сохраняем настройки
        settings_manager.update_settings(music_volume=self.music_volume)
    
    def set_sound_volume(self, volume):
        """Устанавливает громкость звуковых эффектов (0.0 - 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        # Сохраняем настройки
        settings_manager.update_settings(sound_volume=self.sound_volume)
    
    def play_sound(self, sound):
        """Воспроизводит звук с учетом текущей громкости и мута"""
        if not self.sounds_muted and sound:
            sound.set_volume(self.sound_volume)
            sound.play()
    
    def toggle_music_mute(self):
        """Переключает мута музыки"""
        self.music_muted = not self.music_muted
        if self.music_muted:
            self._saved_volume = self.music_volume
            pygame.mixer.music.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(self._saved_volume)
        # Сохраняем настройки
        settings_manager.update_settings(music_muted=self.music_muted)
        return self.music_muted
    
    def toggle_sounds_mute(self):
        """Переключает мута звуковых эффектов"""
        self.sounds_muted = not self.sounds_muted
        # Сохраняем настройки
        settings_manager.update_settings(sounds_muted=self.sounds_muted)
        return self.sounds_muted
    
    def get_music_volume(self):
        """Возвращает текущую громкость музыки"""
        return self.music_volume
    
    def get_sound_volume(self):
        """Возвращает текущую громкость звуков"""
        return self.sound_volume
    
    def is_music_muted(self):
        """Проверяет, замьючена ли музыка"""
        return self.music_muted
    
    def is_sounds_muted(self):
        """Проверяет, замьючены ли звуки"""
        return self.sounds_muted
    
    def toggle_all_sounds(self):
        """Переключает мута музыки и звуков одновременно"""
        self.toggle_music_mute()
        self.toggle_sounds_mute()
        return self.music_muted or self.sounds_muted


# Глобальный экземпляр менеджера музыки
music_manager = MusicManager()

