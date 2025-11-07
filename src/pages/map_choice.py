import pygame
import sys
from src.pages._base import Page
from src.widgets._base import Widget
from src.widgets.button import Button
from src.utils.image import image_cache_manager
from src.utils.config import Config

class MapChoice(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.choice_sel = Widget(470, 153, image_cache_manager.choice, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.rand_text = Widget(605, 855, image_cache_manager.random, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.draw_text = Widget(1157, 855, image_cache_manager.draw, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.rand_but = Button(536, 428, image_cache_manager.rand_img, image_cache_manager.rand_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.draw_but = Button(1044, 428, image_cache_manager.draw_img, image_cache_manager.draw_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

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

            # отрисовка надписей и кнопок
            self.choice_sel.draw(surface)
            self.rand_text.draw(surface)
            self.draw_text.draw(surface)

            if self.rand_but.draw(surface):
                return "singleplayer"
            if self.draw_but.draw(surface):
                pass

            pygame.display.flip()
            clock.tick(60)