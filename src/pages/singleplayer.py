import pygame
import sys
import os
from src.pages._base import Page
from src.widgets._base import Widget
from src.widgets.button import Button
from src.utils.image import image_cache_manager
from src.utils.config import Config

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "Jersey_10", "Jersey10-Regular.ttf")

# Импортируем функции игры
sys.path.insert(0, BASE_DIR)
from pacman_game import run_game_loop, start_new_game, get_score, get_lives

class Singleplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.game_bg = Widget(108, 90, image_cache_manager.game_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.bonuses = Widget(1144, 525, image_cache_manager.bonuses, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.back_but = Button(1350, 913, image_cache_manager.back_img, image_cache_manager.back_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.widgets = [
            self.game_bg, self.bonuses, self.back_but
        ]
        
        # Инициализация игры
        self.game_initialized = False
        self.game_surface = None  # Surface для отрисовки игры
        self.game_rect = None  # Позиция и размер для отрисовки игры на экране
        self._last_window_size = None  # Для отслеживания изменений размера окна
        
        # Таймер игры
        self.game_start_time = None
        self.game_over_start_time = None  # Время начала game over экрана
        self.font_size_base = 64
        self.font = None  # Будет инициализирован при первом запуске
        self.font_path = FONT_PATH if os.path.isfile(FONT_PATH) else None
        self.label_positions = {
            "score": (1213, 125),
            "time": (1213, 225),
            "lives": (1213, 325),
            "difficulty": (1213, 425)
        }
        self.label_texts = {
            "score": "Score",
            "time": "Time",
            "lives": "Lives",
            "difficulty": "Difficulty"
        }

    def _update_game_position(self, window_size):
        """Обновляет позицию и размер игры в зависимости от размера окна"""
        if self._last_window_size == window_size and self.game_rect:
            return  # Размер не изменился
        
        self.game_bg.resize(window_size)
        game_bg_rect = self.game_bg.rect
        
        # Масштабируем surface игры под размер game_bg
        # Увеличиваем масштаб, чтобы игра заполняла рамку без лишних пространств
        if game_bg_rect:
            game_scale_w = game_bg_rect.width / 552
            game_scale_h = game_bg_rect.height / 552
            # Используем минимум, чтобы игра влезала, добавляем пространство между рамкой и игрой
            game_scale = min(game_scale_w, game_scale_h) * 0.94  # 90% для пространства между рамкой и игрой
            
            scaled_game_w = int(552 * game_scale)
            scaled_game_h = int(552 * game_scale)
            
            # Центрируем игру в game_bg
            game_x = game_bg_rect.x + (game_bg_rect.width - scaled_game_w) // 2
            game_y = game_bg_rect.y + (game_bg_rect.height - scaled_game_h) // 2
            self.game_rect = pygame.Rect(game_x, game_y, scaled_game_w, scaled_game_h)
            self._last_window_size = window_size

    def _draw_hud(self, surface):
        """Рисует надписи Score/Time/Difficulty и их значения"""
        if not self.font or not self.game_initialized:
            return

        window_size = surface.get_size()
        scale_w = window_size[0] / Config.BASE_WIDTH
        scale_h = window_size[1] / Config.BASE_HEIGHT
        text_scale = min(scale_w, scale_h)

        font_size = max(16, int(self.font_size_base * text_scale))
        try:
            if self.font_path:
                font = pygame.font.Font(self.font_path, font_size)
            else:
                font = pygame.font.Font(None, font_size)
        except Exception:
            font = pygame.font.SysFont('arial', font_size)

        # Значения из игры
        score_value = str(get_score())

        if self.game_start_time:
            elapsed_ms = pygame.time.get_ticks() - self.game_start_time
            elapsed_seconds = elapsed_ms // 1000
            minutes = elapsed_seconds // 60
            seconds = elapsed_seconds % 60
            time_value = f"{minutes:02d}:{seconds:02d}"
        else:
            time_value = "00:00"

        lives_value = str(get_lives())
        difficulty_value = "1"

        values = {
            "score": score_value,
            "time": time_value,
            "lives": lives_value,
            "difficulty": difficulty_value
        }

        color = (255, 255, 0)
        spacing = int(80 * scale_w)

        for key in ["score", "time", "lives", "difficulty"]:
            base_pos = self.label_positions.get(key)
            if not base_pos:
                continue

            draw_x = int(base_pos[0] * scale_w)
            draw_y = int(base_pos[1] * scale_h)

            label_text = f"{self.label_texts[key]}:"
            label_surface = font.render(label_text, True, color)
            surface.blit(label_surface, (draw_x, draw_y))

            value_surface = font.render(values[key], True, color)
            value_x = draw_x + 200
            value_y = draw_y + (label_surface.get_height() - value_surface.get_height()) // 2
            surface.blit(value_surface, (value_x, value_y))

    def run(self, surface):
        clock = pygame.time.Clock()
        self.on_resize(surface.get_size())
        
        # Инициализация игры при первом запуске
        if not self.game_initialized:
            start_new_game()
            # Размер игры: 552x552 (23*24 x 23*24) - квадратный
            self.game_surface = pygame.Surface((552, 552))
            self.game_start_time = pygame.time.get_ticks()
            # Инициализируем шрифт для отображения текста
            try:
                initial_size = self.font_size_base
                if self.font_path:
                    self.font = pygame.font.Font(self.font_path, initial_size)
                else:
                    self.font = pygame.font.Font(None, initial_size)
            except Exception:
                self.font = pygame.font.SysFont('arial', self.font_size_base)
            self.game_initialized = True
        
        # Обновляем размер и позицию игры
        window_size = surface.get_size()
        self._update_game_position(window_size)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    surface = pygame.display.set_mode((event.w, event.h),
                                                      pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
                    self.on_resize(surface.get_size())
                    # Обновляем размеры при изменении окна
                    window_size = surface.get_size()
                    self._update_game_position(window_size)

            # Обновляем размеры игры (на случай изменения размера окна)
            current_window_size = surface.get_size()
            self._update_game_position(current_window_size)
            
            # Обновляем игру
            game_state = None
            if self.game_surface and self.game_rect:
                game_state = run_game_loop(self.game_surface)
            
            # Проверяем состояние игры (game over)
            # Автоматическое перенаправление закомментировано
            # if game_state == 'game_over':
            #     if self.game_over_start_time is None:
            #         self.game_over_start_time = pygame.time.get_ticks()
            #     else:
            #         # Через 2 секунды после проигрыша возвращаемся на главную страницу
            #         elapsed_ms = pygame.time.get_ticks() - self.game_over_start_time
            #         if elapsed_ms >= 2000:  # 2 секунды
            #             # Сбрасываем игру при выходе из страницы
            #             self.game_initialized = False
            #             self.game_surface = None
            #             self.game_rect = None
            #             self.game_start_time = None
            #             self.game_over_start_time = None
            #             self._last_window_size = None
            #             start_new_game()
            #             return "menu"
            # else:
            #     # Если игра не в состоянии game_over, сбрасываем таймер
            #     self.game_over_start_time = None

            # Отрисовываем все элементы
            self.draw(surface)  # Фон страницы
            self.game_bg.draw(surface)  # Фон игрового поля
            
            # Отрисовываем игру поверх фона game_bg
            if self.game_surface and self.game_rect:
                scaled_game = pygame.transform.smoothscale(self.game_surface, self.game_rect.size)
                surface.blit(scaled_game, self.game_rect)
            
            self.bonuses.draw(surface)
            self._draw_hud(surface)

            if self.back_but.draw(surface):
                # Сбрасываем игру при выходе из страницы
                self.game_initialized = False
                self.game_surface = None
                self.game_rect = None
                self.game_start_time = None
                self.game_over_start_time = None
                self._last_window_size = None
                start_new_game()
                return "menu"

            pygame.display.flip()
            clock.tick(60)