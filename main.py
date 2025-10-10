import pygame
import sys
import os

# ----------------------------
# Image cache helper
# ----------------------------
_image_cache = {}

def load_image(path):
    """Load image once and cache it (convert_alpha applied)."""
    global _image_cache
    if path not in _image_cache:
        _image_cache[path] = pygame.image.load(path).convert_alpha()
    return _image_cache[path]


# ----------------------------
# Base Class: Widget
# ----------------------------
class Widget:
    def __init__(self, x, y, img, base_w, base_h, scale=1):
        self.base_x = x
        self.base_y = y
        # img already must be a Surface (loaded via load_image)
        self.base_img = img
        self.base_w = base_w
        self.base_h = base_h
        self.scale = scale

        # cached scaled image & related info
        self._cached_size = None          # (width, height) of scaled image
        self._scaled_image = None         # scaled Surface
        self._rect = None                 # current rect (topleft pos)
        self._last_window_size = None     # (win_w, win_h) used to compute scaling

    def resize(self, window_size):
        """Resize/calc scaled image and rect if window size changed."""
        if self._last_window_size == window_size and self._cached_size is not None:
            return  # no change

        win_w, win_h = window_size
        sfw = win_w / self.base_w
        sfh = win_h / self.base_h
        sf = min(sfw, sfh)

        width, height = self.base_img.get_size()
        new_w = max(1, int(width * self.scale * sf))
        new_h = max(1, int(height * self.scale * sf))
        new_size = (new_w, new_h)

        # scale only if size changed
        if self._cached_size != new_size:
            self._scaled_image = pygame.transform.smoothscale(self.base_img, new_size)
            self._cached_size = new_size

        scaled_x = int(self.base_x * sfw)
        scaled_y = int(self.base_y * sfh)
        self._rect = self._scaled_image.get_rect(topleft=(scaled_x, scaled_y))

        self._last_window_size = window_size

    def draw(self, surface):
        """Draw widget using cached scaled image (resizes if needed)."""
        window_size = surface.get_size()
        if self._last_window_size != window_size or self._scaled_image is None:
            self.resize(window_size)
        surface.blit(self._scaled_image, self._rect)

    @property
    def rect(self):
        return self._rect


# ----------------------------
# Derived Class: Button
# ----------------------------
class Button(Widget):
    def __init__(self, x, y, img, hover_img, base_w, base_h, scale=1):
        super().__init__(x, y, img, base_w, base_h, scale)
        self.base_hover = hover_img
        self.clicked = False

        # hover cache
        self._hover_cached_size = None
        self._hover_cached_surf = None

    def resize(self, window_size):
        """Resize both base and hover to exactly same size and recalc rect."""
        prev_last = self._last_window_size
        super().resize(window_size)  # prepares _scaled_image and _rect

        # Ensure hover uses exactly same scaled size as base
        scaled_size = self._cached_size
        if self._hover_cached_size != scaled_size:
            # scale hover image
            self._hover_cached_surf = pygame.transform.smoothscale(self.base_hover, scaled_size)
            self._hover_cached_size = scaled_size

        # Recompute rect based on Widget's computed position (already in super)
        # (super().resize computed self._rect already)
        self._last_window_size = window_size

    def draw(self, surface):
        """Draw button using cached base and hover surfaces."""
        window_size = surface.get_size()
        if self._last_window_size != window_size or self._scaled_image is None:
            self.resize(window_size)

        action = False
        pos = pygame.mouse.get_pos()
        if self._rect and self._rect.collidepoint(pos):
            # blit hover (cached)
            surface.blit(self._hover_cached_surf, self._rect)
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True
        else:
            surface.blit(self._scaled_image, self._rect)

        # reset clicked when mouse released
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        return action


# ----------------------------
# Base Page
# ----------------------------
class Page:
    def __init__(self, image, base_w, base_h, scale=1):
        self.base_img = image         # background surface (loaded via load_image)
        self.base_w = base_w
        self.base_h = base_h
        self.scale = scale

        # background cache
        self._bg_cached_size = None
        self._bg_scaled = None
        self._last_window_size = None

        # store widgets in a list in derived pages
        self.widgets = []

    def on_resize(self, window_size):
        """Call resize on background and all widgets."""
        # background
        if self._last_window_size != window_size or self._bg_scaled is None:
            win_w, win_h = window_size
            self._bg_scaled = pygame.transform.smoothscale(self.base_img, (win_w, win_h))
            self._bg_cached_size = (win_w, win_h)
            self._last_window_size = window_size

        # widgets
        for w in self.widgets:
            w.resize(window_size)

    def draw(self, surface):
        """Draw background (cached). Widgets draw themselves."""
        window_size = surface.get_size()
        if self._last_window_size != window_size or self._bg_scaled is None:
            self.on_resize(window_size)
        surface.blit(self._bg_scaled, (0, 0))


# ----------------------------
# Menu Page
# ----------------------------
class Menu(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)

        # create widgets (use already-loaded Surfaces)
        self.title_widget = Widget(39, 220, title_img, BASE_WIDTH, BASE_HEIGHT)
        self.menu_widget = Widget(1020, 129, menu_img, BASE_WIDTH, BASE_HEIGHT)
        self.authors_widget = Widget(65, 960, authors_img, BASE_WIDTH, BASE_HEIGHT)

        self.spl_but = Button(1184, 267, spl_img, spl_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.mpl_but = Button(1184, 406, mpl_img, mpl_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.set_but = Button(1184, 548, set_img, set_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.quit_but = Button(1184, 687, quit_img, quit_hov_img, BASE_WIDTH, BASE_HEIGHT)

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
                return "single_player"
            if self.mpl_but.draw(surface):
                return "multi_player"
            if self.set_but.draw(surface):
                return "settings"
            if self.quit_but.draw(surface):
                pygame.quit()
                sys.exit()

            pygame.display.flip()
            clock.tick(60)


# ----------------------------
# Settings Page
# ----------------------------
class Settings(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)

        self.deco1 = Widget(110, 91, deco, BASE_WIDTH, BASE_HEIGHT)
        self.deco2 = Widget(1610, 91, deco, BASE_WIDTH, BASE_HEIGHT)
        self.name = Widget(211, 275, name_img, BASE_WIDTH, BASE_HEIGHT)
        self.volume = Widget(211, 424, volume_img, BASE_WIDTH, BASE_HEIGHT)
        self.theme = Widget(211, 573, theme_img, BASE_WIDTH, BASE_HEIGHT)
        self.col1 = Widget(440, 567, col1_img, BASE_WIDTH, BASE_HEIGHT)
        self.col2 = Widget(540, 567, col2_img, BASE_WIDTH, BASE_HEIGHT)
        self.col3 = Widget(640, 567, col3_img, BASE_WIDTH, BASE_HEIGHT)
        self.col4 = Widget(740, 567, col4_img, BASE_WIDTH, BASE_HEIGHT)
        self.col5 = Widget(840, 567, col5_img, BASE_WIDTH, BASE_HEIGHT)
        self.slider = Widget(409, 432, slider_img, BASE_WIDTH, BASE_HEIGHT)

        self.main_but = Button(434, 53, main_img, main_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.lead_but = Button(1010, 53, lead_img, lead_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.back_but = Button(1350, 913, back_img, back_hov_img, BASE_WIDTH, BASE_HEIGHT)

        self.widgets = [
            self.deco1, self.deco2, self.name, self.volume, self.theme,
            self.col1, self.col2, self.col3, self.col4, self.col5, self.slider,
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
            # draw widgets
            for w in [
                self.deco1, self.deco2, self.name, self.volume, self.theme,
                self.col1, self.col2, self.col3, self.col4, self.col5, self.slider
            ]:
                w.draw(surface)

            if self.main_but.draw(surface):
                return "settings"
            if self.lead_but.draw(surface):
                return "leaderboard"
            if self.back_but.draw(surface):
                return "menu"

            pygame.display.flip()
            clock.tick(60)


# ----------------------------
# Leaderboard Page
# ----------------------------
class Leaderboard(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.deco1 = Widget(110, 91, deco, BASE_WIDTH, BASE_HEIGHT)
        self.deco2 = Widget(1610, 91, deco, BASE_WIDTH, BASE_HEIGHT)

        self.main_but = Button(434, 53, main_img, main_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.lead_but = Button(1010, 53, lead_img, lead_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.back_but = Button(1350, 913, back_img, back_hov_img, BASE_WIDTH, BASE_HEIGHT)

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


# ----------------------------
# Simple Page placeholders
# ----------------------------
class Singleplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)


class Multiplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)


# ----------------------------
# Game Setup
# ----------------------------
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

BASE_WIDTH, BASE_HEIGHT = 1920, 1080
# use double buffering + hardware surface if available
screen = pygame.display.set_mode((BASE_WIDTH // 2, BASE_HEIGHT // 2),
                                 pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
pygame.display.set_caption('Pacman Remastered')

# Load background and assets using cache
bg = load_image('Assets/Bg.png')

title_img = load_image('Assets/Menu/Title.png')
authors_img = load_image('Assets/Menu/Authors.png')
menu_img = load_image('Assets/Menu/Menu.png')
spl_img = load_image('Assets/Menu/Buttons/Spl_img.png')
spl_hov_img = load_image('Assets/Menu/Buttons/Spl_hov_img.png')
mpl_img = load_image('Assets/Menu/Buttons/Mpl_img.png')
mpl_hov_img = load_image('Assets/Menu/Buttons/Mpl_hov_img.png')
set_img = load_image('Assets/Menu/Buttons/Set_img.png')
set_hov_img = load_image('Assets/Menu/Buttons/Set_hov_img.png')
quit_img = load_image('Assets/Menu/Buttons/Quit_img.png')
quit_hov_img = load_image('Assets/Menu/Buttons/Quit_hov_img.png')

deco = load_image('Assets/Settings/Deco.png')
name_img = load_image('Assets/Settings/Name.png')
volume_img = load_image('Assets/Settings/Volume.png')
theme_img = load_image('Assets/Settings/Theme.png')
col1_img = load_image('Assets/Settings/Buttons/Col1_img.png')
col2_img = load_image('Assets/Settings/Buttons/Col2_img.png')
col3_img = load_image('Assets/Settings/Buttons/Col3_img.png')
col4_img = load_image('Assets/Settings/Buttons/Col4_img.png')
col5_img = load_image('Assets/Settings/Buttons/Col5_img.png')
slider_img = load_image('Assets/Settings/Buttons/Slider_img.png')
main_img = load_image('Assets/Settings/Buttons/Main_img.png')
main_hov_img = load_image('Assets/Settings/Buttons/Main_hov_img.png')
lead_img = load_image('Assets/Settings/Buttons/Lead_img.png')
lead_hov_img = load_image('Assets/Settings/Buttons/Lead_hov_img.png')
back_img = load_image('Assets/Settings/Buttons/Back_img.png')
back_hov_img = load_image('Assets/Settings/Buttons/Back_hov_img.png')

# Create pages
menu_page = Menu(bg, BASE_WIDTH, BASE_HEIGHT)
settings_page = Settings(bg, BASE_WIDTH, BASE_HEIGHT)
leaderboard_page = Leaderboard(bg, BASE_WIDTH, BASE_HEIGHT)

current_page = "menu"
clock = pygame.time.Clock()
done = False

# ----------------------------
# Main Loop
# ----------------------------
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.VIDEORESIZE:
            # recreate screen with double buffering flags to ensure consistency
            screen = pygame.display.set_mode((event.w, event.h),
                                             pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
            # notify pages about resize so they precompute scaled assets
            menu_page.on_resize(screen.get_size())
            settings_page.on_resize(screen.get_size())
            leaderboard_page.on_resize(screen.get_size())

    # draw current page by delegating to its run loop (which also handles resize internally)
    if current_page == "menu":
        current_page = menu_page.run(screen)
    elif current_page == "single_player":
        # placeholder: just go back to menu for now
        current_page = "menu"
    elif current_page == "multi_player":
        current_page = "menu"
    elif current_page == "settings":
        current_page = settings_page.run(screen)
    elif current_page == "leaderboard":
        current_page = leaderboard_page.run(screen)

    # small sleep is handled by page loops; main loop mainly dispatches to page.run

pygame.quit()
sys.exit()


# import pygame
# import sys
# import os
#
# # ----------------------------
# # Base Class: Widget
# # ----------------------------
# class Widget:
#     def __init__(self, x, y, img, base_w, base_h, scale=1):
#         self.base_x = x
#         self.base_y = y
#         self.base_img = img.convert_alpha()
#         self.base_w = base_w
#         self.base_h = base_h
#         self.scale = scale
#
#         # Initialize scaled image and rect
#         self.image = self.base_img
#         self.rect = self.image.get_rect(topleft=(x, y))
#
#     def _auto_resize(self, surface):
#         """Automatically rescale and reposition the widget based on current window size."""
#         current_w, current_h = surface.get_size()
#         scale_factor_w = current_w / self.base_w
#         scale_factor_h = current_h / self.base_h
#         scale_factor = min(scale_factor_w, scale_factor_h)  # keep proportions
#
#         # Scale image
#         width, height = self.base_img.get_size()
#         new_size = (int(width * self.scale * scale_factor), int(height * self.scale * scale_factor))
#         self.image = pygame.transform.smoothscale(self.base_img, new_size)
#
#         # Recalculate position
#         scaled_x = int(self.base_x * scale_factor_w)
#         scaled_y = int(self.base_y * scale_factor_h)
#         self.rect = self.image.get_rect(topleft=(scaled_x, scaled_y))
#
#
#     def draw(self, surface):
#         """Draw widget and auto-resize before rendering."""
#         self._auto_resize(surface)
#         surface.blit(self.image, self.rect)
#
#
# # ----------------------------
# # Derived Class: Buttons
# # ----------------------------
# class Button(Widget):
#     def __init__(self, x, y, img, hover_img, base_w, base_h, scale=1):
#         super().__init__(x, y, img, base_w, base_h, scale)
#         self.base_hover = hover_img.convert_alpha()
#         self.hover = self.base_hover
#         self.clicked = False
#
#     def draw(self, surface):
#         """Draw resizable button with hover and click behavior."""
#         # Auto-resize both images
#         current_w, current_h = surface.get_size()
#         scale_factor_w = current_w / self.base_w
#         scale_factor_h = current_h / self.base_h
#         scale_factor = min(scale_factor_w, scale_factor_h)
#
#         width, height = self.base_img.get_size()
#         new_size = (int(width * self.scale * scale_factor), int(height * self.scale * scale_factor))
#         self.image = pygame.transform.smoothscale(self.base_img, new_size)
#         self.hover = pygame.transform.smoothscale(self.base_hover, new_size)
#
#         # Position
#         scaled_x = int(self.base_x * scale_factor_w)
#         scaled_y = int(self.base_y * scale_factor_h)
#         self.rect = self.image.get_rect(topleft=(scaled_x, scaled_y))
#
#         # Interaction
#         action = False
#         pos = pygame.mouse.get_pos()
#         if self.rect.collidepoint(pos):
#             surface.blit(self.hover, self.rect)
#             if pygame.mouse.get_pressed()[0] and not self.clicked:
#                 self.clicked = True
#                 action = True
#         else:
#             surface.blit(self.image, self.rect)
#
#         if pygame.mouse.get_pressed()[0] == 0:
#             self.clicked = False
#
#         return action
#
# class Page:
#     def __init__(self, image, base_w, base_h, scale=1):
#         self.base_img = image.convert_alpha()
#         self.base_w = base_w
#         self.base_h = base_h
#         self.scale = scale
#
#     def draw(self, surface):
#         current_w, current_h = surface.get_size()
#         image = pygame.transform.smoothscale(self.base_img, (current_w, current_h))
#         surface.blit(image, (0, 0))
#
# class Menu(Page):
#     def __init__(self, image, base_w, base_h):
#         super().__init__(image, base_w, base_h)
#         self.title_widget = Widget(39, 220, title_img, BASE_WIDTH, BASE_HEIGHT)
#         self.menu_widget = Widget(1020, 129, menu_img, BASE_WIDTH, BASE_HEIGHT)
#         self.authors_widget = Widget(65, 960, authors_img, BASE_WIDTH, BASE_HEIGHT)
#         self.spl_but = Button(1184, 267, spl_img, spl_hov_img, BASE_WIDTH, BASE_HEIGHT)
#         self.mpl_but = Button(1184, 406, mpl_img, mpl_hov_img, BASE_WIDTH, BASE_HEIGHT)
#         self.set_but = Button(1184, 548, set_img, set_hov_img, BASE_WIDTH, BASE_HEIGHT)
#         self.quit_but = Button(1184, 687, quit_img, quit_hov_img, BASE_WIDTH, BASE_HEIGHT)
#
#     def run(self, surface):
#         clock = pygame.time.Clock()
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()
#                 elif event.type == pygame.VIDEORESIZE:
#                     surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
#
#             self.draw(surface)
#             self.title_widget.draw(surface)
#             self.menu_widget.draw(surface)
#             self.authors_widget.draw(surface)
#
#             if self.spl_but.draw(surface):
#                 return "single_player"
#             if self.mpl_but.draw(surface):
#                 return "multi_player"
#             if self.set_but.draw(surface):
#                 return "settings"
#             if self.quit_but.draw(surface):
#                 pygame.quit()
#                 sys.exit()
#
#             pygame.display.flip()
#             clock.tick(60)
#
# class Settings(Page):
#     def __init__(self, image, base_w, base_h):
#         super().__init__(image, base_w, base_h)
#         self.deco1 = Widget(110, 91, deco, BASE_WIDTH, BASE_HEIGHT)
#         self.deco2 = Widget(1610, 91, deco, BASE_WIDTH, BASE_HEIGHT)
#         self.name = Widget(211, 275, name_img, BASE_WIDTH, BASE_HEIGHT)
#         self.volume = Widget(211, 424, volume_img, BASE_WIDTH, BASE_HEIGHT)
#         self.theme = Widget(211, 573, theme_img, BASE_WIDTH, BASE_HEIGHT)
#         self.col1 = Widget(440, 567, col1_img, BASE_WIDTH, BASE_HEIGHT)
#         self.col2 = Widget(540, 567, col2_img, BASE_WIDTH, BASE_HEIGHT)
#         self.col3 = Widget(640, 567, col3_img, BASE_WIDTH, BASE_HEIGHT)
#         self.col4 = Widget(740, 567, col4_img, BASE_WIDTH, BASE_HEIGHT)
#         self.col5 = Widget(840, 567, col5_img, BASE_WIDTH, BASE_HEIGHT)
#         self.slider = Widget(409, 432, slider_img, BASE_WIDTH, BASE_HEIGHT)
#         self.main_but = Button(434, 53, main_img, main_hov_img, BASE_WIDTH, BASE_HEIGHT)
#         self.lead_but = Button(1010, 53, lead_img, lead_hov_img, BASE_WIDTH, BASE_HEIGHT)
#         self.back_but = Button(1350, 913, back_img, back_hov_img, BASE_WIDTH, BASE_HEIGHT)
#     def run(self, surface):
#         clock = pygame.time.Clock()
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()
#                 elif event.type == pygame.VIDEORESIZE:
#                     surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
#
#             self.draw(surface)
#             self.deco1.draw(surface)
#             self.deco2.draw(surface)
#             self.name.draw(surface)
#             self.volume.draw(surface)
#             self.theme.draw(surface)
#             self.col1.draw(surface)
#             self.col2.draw(surface)
#             self.col3.draw(surface)
#             self.col4.draw(surface)
#             self.col5.draw(surface)
#             self.slider.draw(surface)
#
#             if self.main_but.draw(surface):
#                 return "settings"
#             if self.lead_but.draw(surface):
#                 return "leaderboard"
#             if self.back_but.draw(surface):
#                 return "menu"
#
#             pygame.display.flip()
#             clock.tick(60)
#
# class Leaderboard(Page):
#     def __init__(self, image, base_w, base_h):
#         super().__init__(image, base_w, base_h)
#         self.deco1 = Widget(110, 91, deco, BASE_WIDTH, BASE_HEIGHT)
#         self.deco2 = Widget(1610, 91, deco, BASE_WIDTH, BASE_HEIGHT)
#         self.main_but = Button(434, 53, main_img, main_hov_img, BASE_WIDTH, BASE_HEIGHT)
#         self.lead_but = Button(1010, 53, lead_img, lead_hov_img, BASE_WIDTH, BASE_HEIGHT)
#         self.back_but = Button(1350, 913, back_img, back_hov_img, BASE_WIDTH, BASE_HEIGHT)
#
#
#     def run(self, surface):
#         clock = pygame.time.Clock()
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()
#                 elif event.type == pygame.VIDEORESIZE:
#                     surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
#
#             self.draw(surface)
#             self.deco1.draw(surface)
#             self.deco2.draw(surface)
#
#             if self.main_but.draw(surface):
#                 return "settings"
#             if self.lead_but.draw(surface):
#                 return "leaderboard"
#             if self.back_but.draw(surface):
#                 return "menu"
#
#             pygame.display.flip()
#             clock.tick(60)
#
# class Singleplayer(Page):
#     def __init__(self, image, base_w, base_h):
#         super().__init__(image, base_w, base_h)
#
# class Multiplayer(Page):
#     def __init__(self, image, base_w, base_h):
#         super().__init__(image, base_w, base_h)
#
# # ----------------------------
# # Game Setup
# # ----------------------------
# pygame.init()
# os.environ['SDL_VIDEO_CENTERED'] = '1'
#
# BASE_WIDTH, BASE_HEIGHT = 1920, 1080
# screen = pygame.display.set_mode((BASE_WIDTH // 2, BASE_HEIGHT // 2), pygame.RESIZABLE)
# pygame.display.set_caption('Pacman Remastered')
#
# # Load background
# bg = pygame.image.load('Assets/Bg.png')
#
# #Load images
#
# title_img = pygame.image.load('Assets/Menu/Title.png')
# authors_img = pygame.image.load('Assets/Menu/Authors.png')
# menu_img = pygame.image.load('Assets/Menu/Menu.png')
# spl_img = pygame.image.load('Assets/Menu/Buttons/Spl_img.png')
# spl_hov_img = pygame.image.load('Assets/Menu/Buttons/Spl_hov_img.png')
# mpl_img = pygame.image.load('Assets/Menu/Buttons/Mpl_img.png')
# mpl_hov_img = pygame.image.load('Assets/Menu/Buttons/Mpl_hov_img.png')
# set_img = pygame.image.load('Assets/Menu/Buttons/Set_img.png')
# set_hov_img = pygame.image.load('Assets/Menu/Buttons/Set_hov_img.png')
# quit_img = pygame.image.load('Assets/Menu/Buttons/Quit_img.png')
# quit_hov_img = pygame.image.load('Assets/Menu/Buttons/Quit_hov_img.png')
#
# deco = pygame.image.load('Assets/Settings/Deco.png')
# name_img = pygame.image.load('Assets/Settings/Name.png')
# volume_img = pygame.image.load('Assets/Settings/Volume.png')
# theme_img = pygame.image.load('Assets/Settings/Theme.png')
# col1_img = pygame.image.load('Assets/Settings/Buttons/Col1_img.png')
# col2_img = pygame.image.load('Assets/Settings/Buttons/Col2_img.png')
# col3_img = pygame.image.load('Assets/Settings/Buttons/Col3_img.png')
# col4_img = pygame.image.load('Assets/Settings/Buttons/Col4_img.png')
# col5_img = pygame.image.load('Assets/Settings/Buttons/Col5_img.png')
# slider_img = pygame.image.load('Assets/Settings/Buttons/Slider_img.png')
# main_img = pygame.image.load('Assets/Settings/Buttons/Main_img.png')
# main_hov_img = pygame.image.load('Assets/Settings/Buttons/Main_hov_img.png')
# lead_img = pygame.image.load('Assets/Settings/Buttons/Lead_img.png')
# lead_hov_img = pygame.image.load('Assets/Settings/Buttons/Lead_hov_img.png')
# back_img = pygame.image.load('Assets/Settings/Buttons/Back_img.png')
# back_hov_img = pygame.image.load('Assets/Settings/Buttons/Back_hov_img.png')
#
# # Create pages
# menu_page = Menu(bg, BASE_WIDTH, BASE_HEIGHT)
# settings_page = Settings(bg, BASE_WIDTH, BASE_HEIGHT)
# leaderboard_page = Leaderboard(bg, BASE_WIDTH, BASE_HEIGHT)
#
# current_page = "menu"
# clock = pygame.time.Clock()
# done = False
#
# # ----------------------------
# # Main Loop
# # ----------------------------
# while not done:
#
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             done = True
#
#     screen.fill((0, 23, 175))
#
#     if current_page == "menu":
#         current_page = menu_page.run(screen)
#     elif current_page == "single_player":
#         current_page = menu_page.run(screen)
#     elif current_page == "multi_player":
#         current_page = menu_page.run(screen)
#     elif current_page == "settings":
#         current_page = settings_page.run(screen)
#     elif current_page == "leaderboard":
#         current_page = leaderboard_page.run(screen)
#
#
#     pygame.display.flip()
#     clock.tick(60)
#
# pygame.quit()
# sys.exit()




# ----------------------------
# Derived Class: Input Box
# ----------------------------
# class InputBox(Widget):
#     def __init__(self, x, y, w, h, base_w, base_h, font_size=40, text_color=(255, 255, 255),
#                  box_color=(100, 100, 100), active_color=(180, 180, 180), scale=1):
#         """
#         Наследник Widget — текстовое поле для ввода строки
#         :param x, y: базовые координаты
#         :param w, h: базовые размеры поля
#         :param base_w, base_h: базовые размеры экрана
#         :param font_size: базовый размер шрифта
#         """
#         # создаем пустое изображение (фон поля)
#         base_img = pygame.Surface((w, h), pygame.SRCALPHA)
#         base_img.fill((0, 0, 0, 0))  # прозрачный фон
#         super().__init__(x, y, base_img, base_w, base_h, scale)
#
#         self.base_box_w = w
#         self.base_box_h = h
#         self.text_color = text_color
#         self.box_color = box_color
#         self.active_color = active_color
#         self.font_size = font_size
#         self.active = False
#         self.text = ""
#         self.cursor_visible = True
#         self.cursor_timer = 0
#         self.cursor_interval = 500  # мс
#
#     def handle_event(self, event):
#         """Обработка событий ввода"""
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             # Проверяем клик по полю
#             if self.rect.collidepoint(event.pos):
#                 self.active = True
#             else:
#                 self.active = False
#
#         if self.active and event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_RETURN:
#                 print(f"Введено: {self.text}")
#                 self.active = False
#             elif event.key == pygame.K_BACKSPACE:
#                 self.text = self.text[:-1]
#             else:
#                 if len(self.text) < 30:  # ограничение длины
#                     self.text += event.unicode
#
#     def draw(self, surface):
#         """Масштабирует, рисует рамку и текст"""
#         self._auto_resize(surface)
#
#         # Вычисляем текущие масштабы
#         current_w, current_h = surface.get_size()
#         scale_factor_w = current_w / self.base_w
#         scale_factor_h = current_h / self.base_h
#         scale_factor = min(scale_factor_w, scale_factor_h)
#
#         box_w = int(self.base_box_w * scale_factor)
#         box_h = int(self.base_box_h * scale_factor)
#         font_size_scaled = int(self.font_size * scale_factor)
#
#         # Рисуем прямоугольник
#         color = self.active_color if self.active else self.box_color
#         pygame.draw.rect(surface, color, self.rect, border_radius=10)
#
#         # Шрифт и текст
#         font = pygame.font.SysFont(None, font_size_scaled)
#         text_surface = font.render(self.text, True, self.text_color)
#
#         text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
#         surface.blit(text_surface, text_rect)
#
#         # мигающий курсор
#         if self.active:
#             self.cursor_timer += pygame.time.get_ticks() % 1000
#             if (pygame.time.get_ticks() // self.cursor_interval) % 2 == 0:
#                 cursor_x = text_rect.right + 5
#                 cursor_y = self.rect.y + box_h // 4
#                 cursor_h = box_h // 2
#                 pygame.draw.line(surface, self.text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)