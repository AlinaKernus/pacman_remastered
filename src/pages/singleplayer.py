import pygame
import sys
from src.pages._base import Page
from src.widgets._base import Widget
from src.widgets.button import Button
from src.utils.image import image_cache_manager
from src.utils.config import Config

class Singleplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.game_bg = Widget(108, 90, image_cache_manager.game_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.bonuses = Widget(1144, 489, image_cache_manager.bonuses, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.back_but = Button(1350, 913, image_cache_manager.back_img, image_cache_manager.back_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.score_txt = Widget(1213, 107, image_cache_manager.score, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.time_txt = Widget(1213, 228, image_cache_manager.time, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.dif_lvl_txt = Widget(1213, 349, image_cache_manager.dif_lvl, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.widgets = [
            self.game_bg, self.bonuses, self.score_txt,
            self.time_txt, self.dif_lvl_txt, self.back_but
        ]

    def run(self, surface):
        clock = pygame.time.Clock()
        self.on_resize(surface.get_size())

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    surface = pygame.display.set_mode((event.w, event.h),
                                                      pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
                    self.on_resize(surface.get_size())

            self.draw(surface)
            self.game_bg.draw(surface)
            self.bonuses.draw(surface)
            self.score_txt.draw(surface)
            self.time_txt.draw(surface)
            self.dif_lvl_txt.draw(surface)

            if self.back_but.draw(surface):
                return "menu"

            pygame.display.flip()
            clock.tick(60)