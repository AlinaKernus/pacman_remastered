import pygame
import sys
from src.pages._base import Page
from src.widgets._base import Widget
from src.widgets.button import Button
from src.utils.image import image_cache_manager
from src.utils.config import Config

class Leaderboard(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.deco1 = Widget(110, 91, image_cache_manager.deco, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.deco2 = Widget(1610, 91, image_cache_manager.deco, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.main_but = Button(434, 53, image_cache_manager.main_img, image_cache_manager.main_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.lead_but = Button(1010, 53, image_cache_manager.lead_img, image_cache_manager.lead_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.back_but = Button(1350, 913, image_cache_manager.back_img, image_cache_manager.back_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.widgets = [
            self.deco1, self.deco2,
            self.main_but, self.lead_but, self.back_but
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
            self.deco1.draw(surface)
            self.deco2.draw(surface)

            if self.main_but.draw(surface):
                return "settings"
            if self.lead_but.draw(surface):
                return "leaderboard"
            if self.back_but.draw(surface):
                return "menu"

            pygame.display.flip()
            clock.tick(60)