import pygame
import sys
import os
from src.pages._base import Page
from src.widgets._base import Widget
from src.widgets.button import Button
from src.widgets.slider import Slider
from src.utils.image import image_cache_manager
from src.utils.config import Config
from src.utils.music_manager import music_manager
from src.utils.settings_manager import settings_manager

from src.utils.path_helper import get_base_dir
BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "Jersey_10", "Jersey10-Regular.ttf")

class Settings(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)

        self.deco1 = Widget(110, 91, image_cache_manager.deco, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.deco2 = Widget(1610, 91, image_cache_manager.deco, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.name = Widget(211, 275, image_cache_manager.name_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.volume = Widget(211, 424, image_cache_manager.volume_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.theme = Widget(211, 573, image_cache_manager.theme_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        # Слайдер для громкости музыки (0.0 - 1.0)
        self.slider = Slider(430, 432, image_cache_manager.slider_img, Config.BASE_WIDTH, Config.BASE_HEIGHT, length=290, min_val=0.0, max_val=1.0)
        # Инициализируем слайдер с текущей громкостью
        self.slider.value = music_manager.get_music_volume()

        self.back_but = Button(1350, 913, image_cache_manager.back_img, image_cache_manager.back_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col1 = Button(440, 567, image_cache_manager.col1_img, image_cache_manager.col1_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col2 = Button(540, 567, image_cache_manager.col2_img, image_cache_manager.col2_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col3 = Button(640, 567, image_cache_manager.col3_img, image_cache_manager.col3_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col4 = Button(740, 567, image_cache_manager.col4_img, image_cache_manager.col4_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col5 = Button(840, 567, image_cache_manager.col5_img, image_cache_manager.col5_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.widgets = [
            self.deco1, self.deco2, self.name, self.volume, self.theme,
            self.col1, self.col2, self.col3, self.col4, self.col5, self.slider,
            self.back_but
        ]
        
        # Поле ввода username
        self.username = settings_manager.get_setting("username", "")  # Автоматически сгенерируется если пусто
        self.username_input_active = False
        self.username_input_rect = None
        self.font_path = FONT_PATH if os.path.isfile(FONT_PATH) else None


    def _init_font(self, size=36):
        """Инициализация шрифта"""
        try:
            if self.font_path:
                return pygame.font.Font(self.font_path, size)
            else:
                return pygame.font.Font(None, size)
        except Exception:
            return pygame.font.SysFont('arial', size)
    
    def _draw_username_input(self, surface):
        """Отрисовка поля ввода username"""
        window_size = surface.get_size()
        scale_w = window_size[0] / Config.BASE_WIDTH
        scale_h = window_size[1] / Config.BASE_HEIGHT
        
        # Позиция рядом с "Username" (name widget)
        if self.name.rect:
            input_x = int(self.name.rect.right + 85 * scale_w)  # Отступ слева 100 пикселей
            input_y = int(self.name.rect.y - 5)
        else:
            input_x = int(500 * scale_w)
            input_y = int(275 * scale_h)
        
        input_width = int(300 * scale_w + 200)  # Увеличено на 200 пикселей
        input_height = int(60 * scale_h + 10)  # Увеличено еще на 20 пикселей
        
        # Прямоугольник для поля ввода
        input_rect = pygame.Rect(input_x, input_y, input_width, input_height)
        self.username_input_rect = input_rect
        
        # Получаем цвет фона страницы из base_img (с учетом темы)
        try:
            # Получаем цвет из фонового изображения в точке, где находится инпут
            # Конвертируем координаты в координаты базового изображения
            base_x = int((input_x / scale_w) * (self.base_img.get_width() / Config.BASE_WIDTH))
            base_y = int((input_y / scale_h) * (self.base_img.get_height() / Config.BASE_HEIGHT))
            # Ограничиваем координаты размерами изображения
            base_x = max(0, min(base_x, self.base_img.get_width() - 1))
            base_y = max(0, min(base_y, self.base_img.get_height() - 1))
            bg_color = self.base_img.get_at((base_x, base_y))[:3]  # Берем только RGB, без alpha
        except:
            # Fallback если не удалось получить цвет
            bg_color = (40, 40, 40)
        
        # Обводка красная
        border_color = (255, 0, 0)
        border_width = 2
        text_color = (255, 255, 255) if self.username_input_active else (255, 255, 0)
        
        # Рисуем фон и рамку
        pygame.draw.rect(surface, bg_color, input_rect)
        pygame.draw.rect(surface, border_color, input_rect, border_width)
        
        # Текст в поле ввода (шрифт увеличен в 1.5 раза)
        display_text = self.username + ("|" if self.username_input_active else "")
        font_size = int(54 * min(scale_w, scale_h))  # 36 * 1.5 = 54
        font = self._init_font(font_size)
        text_surface = font.render(display_text, True, text_color)
        
        # Центрируем текст в поле ввода
        text_x = input_x + int(20 * scale_w)  # Отступ слева 20 пикселей для текста
        text_y = input_y + (input_height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
    
    def run(self, surface):
        clock = pygame.time.Clock()
        self.on_resize(surface.get_size())
        
        # Обновляем слайдер с текущей громкостью при входе на страницу
        self.slider.value = music_manager.get_music_volume()
        
        # Загружаем username из настроек (автоматически сгенерируется если пусто)
        self.username = settings_manager.get_setting("username", "")

        while True:
            for event in pygame.event.get():
                self.slider.handle_event(event, surface)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    surface = pygame.display.set_mode((event.w, event.h),
                                                     pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
                    self.on_resize(surface.get_size())
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Обработка кликов по полю ввода username
                    if event.button == 1:  # Левая кнопка мыши
                        mouse_pos = event.pos
                        if self.username_input_rect and self.username_input_rect.collidepoint(mouse_pos):
                            self.username_input_active = True
                        else:
                            # Клик вне поля ввода - сохраняем и убираем фокус
                            if self.username_input_active:
                                settings_manager.set_setting("username", self.username)
                            self.username_input_active = False
                elif event.type == pygame.KEYDOWN:
                    if self.username_input_active:
                        if event.key == pygame.K_RETURN:
                            # Сохраняем и убираем фокус
                            settings_manager.set_setting("username", self.username)
                            self.username_input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.username = self.username[:-1]
                        elif event.unicode and event.unicode.isprintable():
                            if len(self.username) < 20:  # Максимальная длина имени
                                self.username += event.unicode

            # Обновляем громкость музыки из слайдера
            music_manager.set_music_volume(self.slider.value)

            self.draw(surface)
            # draw widgets
            for w in [
                self.deco1, self.deco2, self.name, self.volume, self.theme,
                self.slider
            ]:
                w.draw(surface)

            self.slider.draw(surface)
            
            # Отрисовка поля ввода username
            self._draw_username_input(surface)

            if self.back_but.draw(surface):
                # Сохраняем username перед выходом
                if self.username:
                    settings_manager.set_setting("username", self.username)
                return "menu"
            if self.col1.draw(surface):
                self.change_theme(1)
            if self.col2.draw(surface):
                self.change_theme(2)
            if self.col3.draw(surface):
                self.change_theme(3)
            if self.col4.draw(surface):
                self.change_theme(4)
            if self.col5.draw(surface):
                self.change_theme(5)
            
            # Отрисовка и обработка иконки звука
            if self.sound_icon.draw(surface):
                music_manager.toggle_all_sounds()
                # Обновляем слайдер если музыка была размучена
                if not music_manager.is_music_muted():
                    self.slider.value = music_manager.get_music_volume()

            pygame.display.flip()
            clock.tick(60)