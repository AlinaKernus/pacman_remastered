import pygame
import sys
import os
from src.pages._base import Page
from src.widgets._base import Widget
from src.widgets.button import Button
from src.utils.image import image_cache_manager
from src.utils.config import Config
from src.utils.music_manager import music_manager

from src.utils.path_helper import get_base_dir, get_resource_path
BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "Jersey_10", "Jersey10-Regular.ttf")

class Menu(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.font_path = FONT_PATH if os.path.isfile(FONT_PATH) else None

        # create widgets (use already-loaded Surfaces)
        self.title_widget = Widget(39, 220, image_cache_manager.title_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.menu_widget = Widget(1020, 129, image_cache_manager.menu_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.authors_widget = Widget(65, 960, image_cache_manager.authors_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        self.spl_but = Button(1184, 267, image_cache_manager.spl_img, image_cache_manager.spl_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.lead_but = Button(1184, 406, image_cache_manager.lead_img, image_cache_manager.lead_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.set_but = Button(1184, 548, image_cache_manager.set_img, image_cache_manager.set_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        self.quit_but = Button(1184, 687, image_cache_manager.quit_img, image_cache_manager.quit_hov_img, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        # register widgets for resize
        self.widgets = [
            self.title_widget, self.menu_widget, self.authors_widget,
            self.spl_but, self.lead_but, self.set_but, self.quit_but
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
            self.menu_widget.draw(surface)  # Removed to hide "Game" text
            self.authors_widget.draw(surface)

            # Draw buttons
            play_clicked = self.spl_but.draw(surface)
            if self.lead_but.draw(surface):
                return "leaderboard"
            if self.set_but.draw(surface):
                return "settings"
            if self.quit_but.draw(surface):
                pygame.quit()
                sys.exit()
            
            if play_clicked:
                return "singleplayer"
            
            # Отрисовка и обработка иконки звука
            if self.sound_icon.draw(surface):
                music_manager.toggle_all_sounds()

            pygame.display.flip()
            clock.tick(60)