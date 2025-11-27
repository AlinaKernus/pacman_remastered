import pygame
import sys
from src.pages._base import Page
from src.widgets._base import Widget
from src.widgets.button import Button
from src.widgets.slider import Slider
from src.utils.image import image_cache_manager
from src.utils.config import Config
from src.utils.music_manager import music_manager

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

        self.main_but = Button(434, 53, image_cache_manager.main_img, image_cache_manager.main_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.lead_but = Button(1010, 53, image_cache_manager.lead_img, image_cache_manager.lead_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.back_but = Button(1350, 913, image_cache_manager.back_img, image_cache_manager.back_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col1 = Button(440, 567, image_cache_manager.col1_img, image_cache_manager.col1_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col2 = Button(540, 567, image_cache_manager.col2_img, image_cache_manager.col2_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col3 = Button(640, 567, image_cache_manager.col3_img, image_cache_manager.col3_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col4 = Button(740, 567, image_cache_manager.col4_img, image_cache_manager.col4_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.col5 = Button(840, 567, image_cache_manager.col5_img, image_cache_manager.col5_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.widgets = [
            self.deco1, self.deco2, self.name, self.volume, self.theme,
            self.col1, self.col2, self.col3, self.col4, self.col5, self.slider,
            self.main_but, self.lead_but, self.back_but
        ]


    def run(self, surface):
        clock = pygame.time.Clock()
        self.on_resize(surface.get_size())
        
        # Обновляем слайдер с текущей громкостью при входе на страницу
        self.slider.value = music_manager.get_music_volume()

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

            if self.main_but.draw(surface):
                return "settings"
            if self.lead_but.draw(surface):
                return "leaderboard"
            if self.back_but.draw(surface):
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