import pygame
from src.widgets._base import Widget
from src.utils.music_manager import music_manager

class Slider(Widget):
    def __init__(self, x, y, img, base_w, base_h, length=300, min_val=0.0, max_val=1.0, scale=1):
        super().__init__(x, y, img, base_w, base_h, scale)
        self.length = length
        self.min_val = min_val
        self.max_val = max_val
        self.value = 0.5 * (min_val + max_val)
        self.dragging = False
        self.update_knob_position()

    def update_knob_position(self):
        win_w, win_h = pygame.display.get_surface().get_size()
        sfw = win_w / self.base_w
        sfh = win_h / self.base_h
        sf = min(sfw, sfh)

        #resize the length
        scaled_length = self.length * sf
        track_x = int(self.base_x * sfw)
        track_y = int(self.base_y * sfh)

        knob_radius = self._rect.width // 2 if self._rect else 0
        x_min = track_x - knob_radius
        x_max = track_x + int(scaled_length) - knob_radius

        #position of the ball
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        new_x = int(x_min + t * (x_max - x_min))

        if self._rect:
            self._rect.x = new_x
            self._rect.y = track_y

    def resize(self, window_size):
        super().resize(window_size)
        self.update_knob_position()

    def handle_event(self, event, surface):
        """Handles clicks with the mouse"""
        window_size = surface.get_size()
        self.resize(window_size)
        pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Проверяем клик на треке слайдера (не только на ползунке)
            win_w, win_h = window_size
            sfw = win_w / self.base_w
            scaled_length = self.length * sfw
            x_min = int(self.base_x * sfw)
            x_max = x_min + int(scaled_length)
            track_y = int(self.base_y * (win_h / self.base_h))
            track_height = 50  # Примерная высота области клика
            
            # Проверяем клик на треке
            if x_min <= pos[0] <= x_max and track_y - track_height//2 <= pos[1] <= track_y + track_height//2:
                self.dragging = True
                # Обновляем значение при клике на треке
                new_x = max(x_min, min(pos[0], x_max))
                t = (new_x - x_min) / (x_max - x_min)
                self.value = self.min_val + t * (self.max_val - self.min_val)
                # Обновляем громкость через music_manager
                music_manager.set_music_volume(self.value)
                self.update_knob_position()
            elif self.rect and self.rect.collidepoint(pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # пересчёт в зависимости от размера окна
            win_w, win_h = window_size
            sfw = win_w / self.base_w
            sf = sfw  # длина зависит только от ширины

            scaled_length = self.length * sf

            # ограничение движения по X
            x_min = int(self.base_x * sfw)
            x_max = x_min + int(scaled_length)
            new_x = max(x_min, min(pos[0], x_max))

            # нормализуем громкость в диапазон [min_val, max_val]
            t = (new_x - x_min) / (x_max - x_min)
            self.value = self.min_val + t * (self.max_val - self.min_val)
            # Обновляем громкость через music_manager
            music_manager.set_music_volume(self.value)

            # сдвигаем ползунок
            self._rect.x = new_x - self._rect.width // 2

    def draw(self, surface):
        """Draws the slider ball"""
        super().draw(surface)