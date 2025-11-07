import pygame
import sys
from src.pages._base import Page
from src.widgets._base import Widget
from src.widgets.button import Button
from src.utils.image import image_cache_manager
from src.utils.config import Config

class Menu(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)

        # create widgets (use already-loaded Surfaces)
        self.title_widget = Widget(39, 220, image_cache_manager.title_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.menu_widget = Widget(1020, 129, image_cache_manager.menu_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.authors_widget = Widget(65, 960, image_cache_manager.authors_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.spl_but = Button(1184, 267, image_cache_manager.spl_img, image_cache_manager.spl_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.mpl_but = Button(1184, 406, image_cache_manager.mpl_img, image_cache_manager.mpl_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.set_but = Button(1184, 548, image_cache_manager.set_img, image_cache_manager.set_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.quit_but = Button(1184, 687, image_cache_manager.quit_img, image_cache_manager.quit_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        # register widgets for resize
        self.widgets = [
            self.title_widget, self.menu_widget, self.authors_widget,
            self.spl_but, self.mpl_but, self.set_but, self.quit_but
        ]

    def run(self, surface):
        clock = pygame.time.Clock()
        # ensure initial resize
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
            # draw widgets
            self.title_widget.draw(surface)
            self.menu_widget.draw(surface)
            self.authors_widget.draw(surface)

            if self.spl_but.draw(surface):
                return "map_choice"
            if self.mpl_but.draw(surface):
                return "multi_player"
            if self.set_but.draw(surface):
                return "settings"
            if self.quit_but.draw(surface):
                pygame.quit()
                sys.exit()

            pygame.display.flip()
            clock.tick(60)