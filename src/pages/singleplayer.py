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
PACMAN1_DIR = os.path.join(BASE_DIR, "pac-man-1")

# Импортируем игру из pac-man-1
# Временно меняем рабочую директорию для правильных путей к ресурсам
old_cwd = os.getcwd()
sys.path.insert(0, PACMAN1_DIR)
os.chdir(PACMAN1_DIR)
from GameScene import GameScene
os.chdir(old_cwd)

# Импортируем music_manager для управления звуками
from src.utils.music_manager import music_manager

class Singleplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.game_bg = Widget(108, 90, image_cache_manager.game_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.back_but = Button(1350, 913, image_cache_manager.back_img, image_cache_manager.back_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.widgets = [
            self.game_bg, self.back_but
        ]
        
        # Инициализация игры из pac-man-1
        self.game_initialized = False
        self.game_scene = None  # GameScene из pac-man-1
        self.game_surface = None  # Surface для отрисовки игры
        self.game_rect = None  # Позиция и размер для отрисовки игры на экране
        self._last_window_size = None  # Для отслеживания изменений размера окна
        self._original_music_volume = None  # Сохраняем оригинальную громкость музыки
        
        # Таймер игры
        self.game_start_time = None
        self.game_over_start_time = None  # Время начала game over экрана
        self.font_size_base = 64
        self.font = None  # Будет инициализирован при первом запуске
        self.font_path = FONT_PATH if os.path.isfile(FONT_PATH) else None
        # Позиции центрированы по вертикали (высота экрана 1080, размещаем от 300 до 800)
        self.label_positions = {
            "score": (1213, 300),
            "time": (1213, 400),
            "lives": (1213, 500),
            "difficulty": (1213, 600),
            "controls": (1213, 700),
            # "dev_options": (1213, 800),
            # "collect_points": (1213, 850)
        }
        self.label_texts = {
            "score": "Score",
            "time": "Time",
            "lives": "Lives",
            "difficulty": "Difficulty",
            "controls": "Controls",
            # "dev_options": "Dev options",
            # "collect_points": "Collect all points: H"
        }

    def _update_game_position(self, window_size):
        """Обновляет позицию и размер игры в зависимости от размера окна"""
        if self._last_window_size == window_size and self.game_rect:
            return  # Размер не изменился
        
        self.game_bg.resize(window_size)
        game_bg_rect = self.game_bg.rect
        
        # Масштабируем surface игры под размер game_bg
        # GameScene использует screen_map размером 735x813 (увеличенный)
        if game_bg_rect:
            # Используем стандартные размеры GameScene если игра еще не инициализирована
            if self.game_scene and hasattr(self.game_scene, 'screen_map'):
                game_original_w = self.game_scene.screen_map.get_width()  # 735
                game_original_h = self.game_scene.screen_map.get_height()  # 813
            else:
                game_original_w = 735  # Стандартный размер screen_map (увеличенный)
                game_original_h = 813
            
            game_scale_w = game_bg_rect.width / game_original_w
            game_scale_h = game_bg_rect.height / game_original_h
            # Используем минимум, чтобы игра влезала, добавляем пространство между рамкой и игрой
            game_scale = min(game_scale_w, game_scale_h) * 1.05  # 94% для пространства между рамкой и игрой
            
            scaled_game_w = int(game_original_w * game_scale)
            scaled_game_h = int(game_original_h * game_scale)
            
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
        if self.game_scene:
            score_value = str(self.game_scene.score)
            lives_value = str(self.game_scene.lives)
        else:
            score_value = "0"
            lives_value = "0"

        if self.game_start_time:
            elapsed_ms = pygame.time.get_ticks() - self.game_start_time
            elapsed_seconds = elapsed_ms // 1000
            minutes = elapsed_seconds // 60
            seconds = elapsed_seconds % 60
            time_value = f"{minutes:02d}:{seconds:02d}"
        else:
            time_value = "00:00"
        # Получаем difficulty из игры
        if self.game_scene:
            difficulty_value = str(self.game_scene.difficulty)
        else:
            difficulty_value = "1"

        controls_value = "W,A,S,D"
        
        values = {
            "score": score_value,
            "time": time_value,
            "lives": lives_value,
            "difficulty": difficulty_value,
            "controls": controls_value
        }

        color = (255, 255, 0)
        spacing = int(80 * scale_w)

        for key in ["score", "time", "lives", "difficulty", "controls", "dev_options", "collect_points"]:
            base_pos = self.label_positions.get(key)
            if not base_pos:
                continue

            draw_x = int(base_pos[0] * scale_w)
            draw_y = int(base_pos[1] * scale_h)

            # Для dev_options и collect_points не добавляем двоеточие и значение
            if key in ["dev_options", "collect_points"]:
                label_text = self.label_texts[key]
                label_surface = font.render(label_text, True, color)
                surface.blit(label_surface, (draw_x, draw_y))
            else:
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
            # Сохраняем оригинальную громкость музыки и уменьшаем на 50%
            if self._original_music_volume is None:
                self._original_music_volume = music_manager.get_music_volume()
            # Уменьшаем громкость музыки на 50% для игры
            reduced_volume = self._original_music_volume * 0.5
            if not music_manager.is_music_muted():
                from pygame import mixer
                mixer.music.set_volume(reduced_volume)
            
            # Временно меняем рабочую директорию для инициализации GameScene
            old_cwd = os.getcwd()
            os.chdir(PACMAN1_DIR)
            self.game_scene = GameScene()
            self.game_scene.username = "Player"  # Можно сделать настраиваемым
            # Устанавливаем тему из Config
            self.game_scene.theme_index = Config.CURRENT_THEME
            # Устанавливаем music_manager для проверки мута звуков
            self.game_scene.music_manager = music_manager
            self.game_scene.setup("generated")  # Запускаем сгенерированную карту
            
            # Устанавливаем громкость звуков через music_manager
            # Обновляем громкость всех звуков в GameScene
            if hasattr(self.game_scene, 'start_sound'):
                self.game_scene.start_sound.set_volume(music_manager.get_sound_volume())
            os.chdir(old_cwd)
            
            # GameScene создает свой screen размером 1280x720, но нам нужен только игровой экран
            # Используем screen_map из GameScene (644x713) или весь screen
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
            
            # Обновляем игру из pac-man-1
            if self.game_scene:
                # Обновляем тему, если она изменилась
                if self.game_scene.theme_index != Config.CURRENT_THEME:
                    self.game_scene.theme_index = Config.CURRENT_THEME
                
                # Временно меняем рабочую директорию для обновления GameScene
                old_cwd = os.getcwd()
                os.chdir(PACMAN1_DIR)
                user_input = pygame.key.get_pressed()
                self.game_scene.update(user_input)
                os.chdir(old_cwd)
                # Используем screen_map из GameScene для отрисовки игрового поля
                self.game_surface = self.game_scene.screen_map
            
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
            
            self._draw_hud(surface)

            # Если игра окончена, рисуем надпись GAME OVER над окном игры
            if self.game_scene and getattr(self.game_scene, "game_over", False):
                # Используем основной шрифт (Jersey) красного цвета
                window_size = surface.get_size()
                scale_w = window_size[0] / Config.BASE_WIDTH
                scale_h = window_size[1] / Config.BASE_HEIGHT
                text_scale = min(scale_w, scale_h)

                font_size = max(32, int(self.font_size_base * text_scale))
                try:
                    if self.font_path:
                        go_font = pygame.font.Font(self.font_path, font_size)
                    else:
                        go_font = pygame.font.Font(None, font_size)
                except Exception:
                    go_font = pygame.font.SysFont('arial', font_size)

                game_over_text = go_font.render("GAME OVER", True, (255, 0, 0))

                if self.game_rect:
                    # По центру окна игры по горизонтали и вертикали
                    go_x = self.game_rect.centerx - game_over_text.get_width() // 2
                    go_y = self.game_rect.centery - game_over_text.get_height() // 2
                else:
                    # Фоллбек: центрируем по всему окну
                    go_x = (window_size[0] - game_over_text.get_width()) // 2
                    go_y = (window_size[1] - game_over_text.get_height()) // 2

                surface.blit(game_over_text, (go_x, go_y))

            if self.back_but.draw(surface):
                # Останавливаем все звуки игры перед выходом
                # Останавливаем все звуковые эффекты pygame.mixer (включая звуки из GameScene)
                pygame.mixer.stop()
                # Останавливаем музыку игры если она играет
                pygame.mixer.music.stop()
                # Восстанавливаем оригинальную громкость музыки главного меню
                from pygame import mixer
                mixer.music.load("pac-man-1/Static/Sounds/background.ogg")
                if not music_manager.is_music_muted():
                    # Восстанавливаем оригинальную громкость
                    if self._original_music_volume is not None:
                        mixer.music.set_volume(self._original_music_volume)
                    else:
                        mixer.music.set_volume(music_manager.get_music_volume())
                else:
                    mixer.music.set_volume(0.0)
                mixer.music.play(loops=-1)
                
                # Сбрасываем игру при выходе из страницы
                self.game_initialized = False
                self.game_scene = None
                self.game_surface = None
                self.game_rect = None
                self.game_start_time = None
                self.game_over_start_time = None
                self._last_window_size = None
                self._original_music_volume = None  # Сбрасываем сохраненную громкость
                return "menu"
            
            # Отрисовка и обработка иконки звука
            if self.sound_icon.draw(surface):
                music_manager.toggle_all_sounds()

            pygame.display.flip()
            clock.tick(60)