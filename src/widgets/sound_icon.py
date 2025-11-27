"""
Виджет иконки звука для переключения мута музыки
"""
import pygame
import os
from src.widgets._base import Widget
from src.utils.music_manager import music_manager
from src.utils.config import Config


class SoundIcon(Widget):
    """Иконка звука в правом верхнем углу экрана"""
    
    def __init__(self, base_w, base_h):
        # Загружаем изображения иконок
        sound_path = "Assets/sound.png"
        mute_path = "Assets/mute.png"
        
        try:
            # Загружаем изображения с прозрачностью
            self.icon_sound_on = pygame.image.load(sound_path).convert_alpha()
            self.icon_sound_off = pygame.image.load(mute_path).convert_alpha()
        except (pygame.error, FileNotFoundError) as e:
            # Fallback: создаем простые квадраты если изображения не найдены
            print(f"Не удалось загрузить иконки звука: {e}")
            icon_size = (50, 50)
            self.icon_sound_on = pygame.Surface(icon_size)
            self.icon_sound_on.fill((255, 255, 255))
            self.icon_sound_off = pygame.Surface(icon_size)
            self.icon_sound_off.fill((150, 150, 150))
        
        # Получаем размер иконки из загруженного изображения
        icon_width = self.icon_sound_on.get_width()
        icon_height = self.icon_sound_on.get_height()
        
        # Позиция: правый верхний угол с отступом
        # На базовом разрешении 1920x1080: x = 1920 - ширина - 20, y = 20
        x = base_w - icon_width - 50
        y = 50
        
        # Используем icon_sound_on как базовое изображение
        super().__init__(x, y, self.icon_sound_on, base_w, base_h)
        self.clicked = False
        
        # Кэш для масштабированных версий
        self._scaled_sound_on = None
        self._scaled_sound_off = None
        self._icon_cached_size = None
    
    def resize(self, window_size):
        """Обновляет размер иконки при изменении размера окна"""
        super().resize(window_size)
        
        # Масштабируем обе иконки используя размер из базового класса
        # _cached_size устанавливается в super().resize()
        if self._cached_size:
            scaled_size = self._cached_size
        else:
            # Если размер еще не вычислен, используем размер из rect
            if self._rect:
                scaled_size = (self._rect.width, self._rect.height)
            else:
                scaled_size = (50, 50)
        
        # Обновляем кэш только если размер изменился
        if not hasattr(self, '_icon_cached_size') or self._icon_cached_size != scaled_size or self._scaled_sound_on is None:
            self._scaled_sound_on = pygame.transform.smoothscale(self.icon_sound_on, scaled_size)
            self._scaled_sound_off = pygame.transform.smoothscale(self.icon_sound_off, scaled_size)
            self._icon_cached_size = scaled_size
    
    def draw(self, surface):
        """Рисует иконку звука и обрабатывает клики"""
        window_size = surface.get_size()
        if self._last_window_size != window_size:
            self.resize(window_size)
        
        # Выбираем иконку в зависимости от состояния мута (музыка И звуки)
        if music_manager.is_music_muted() or music_manager.is_sounds_muted():
            icon_surface = self._scaled_sound_off if self._scaled_sound_off else self.icon_sound_off
        else:
            icon_surface = self._scaled_sound_on if self._scaled_sound_on else self.icon_sound_on
        
        # Рисуем иконку
        if self._rect:
            surface.blit(icon_surface, self._rect)
        
        # Обрабатываем клики
        action = False
        pos = pygame.mouse.get_pos()
        if self._rect and self._rect.collidepoint(pos):
            # Можно добавить эффект hover (например, затемнение)
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True
        
        # Сбрасываем clicked когда кнопка мыши отпущена
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False
        
        return action
    
    def set_icon_images(self, sound_on_image, sound_off_image):
        """Позволяет заменить простые квадраты на кастомные изображения"""
        if sound_on_image:
            self.icon_sound_on = sound_on_image
        if sound_off_image:
            self.icon_sound_off = sound_off_image
        # Сбрасываем кэш
        self._scaled_sound_on = None
        self._scaled_sound_off = None
        self._icon_cached_size = None

