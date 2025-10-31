import pygame
import sys
import os
from pygame import mixer

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
# Derived Class: Slider
# ----------------------------
class Slider(Widget):
    def __init__(self, x, y, img, base_w, base_h, length=300, min_val=0.0, max_val=1.0, scale=1):
        super().__init__(x, y, img, base_w, base_h, scale)
        self.length = length
        self.min_val = min_val
        self.max_val = max_val
        self.value = 0.5 * (min_val + max_val)
        self.dragging = False
        self.update_knob_position()

    def update_knob_position(self):
        win_w, win_h = pygame.display.get_surface().get_size()
        sfw = win_w / self.base_w
        sfh = win_h / self.base_h
        sf = min(sfw, sfh)

        #resize the length
        scaled_length = self.length * sf
        track_x = int(self.base_x * sfw)
        track_y = int(self.base_y * sfh)

        knob_radius = self._rect.width // 2 if self._rect else 0
        x_min = track_x - knob_radius
        x_max = track_x + int(scaled_length) - knob_radius

        #position of the ball
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        new_x = int(x_min + t * (x_max - x_min))

        if self._rect:
            self._rect.x = new_x
            self._rect.y = track_y

    def resize(self, window_size):
        super().resize(window_size)
        self.update_knob_position()

    def handle_event(self, event, surface):
        """Handles clicks with the mouse"""
        window_size = surface.get_size()
        self.resize(window_size)
        pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect and self.rect.collidepoint(pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # пересчёт в зависимости от размера окна
            win_w, win_h = window_size
            sfw = win_w / self.base_w
            sf = sfw  # длина зависит только от ширины

            scaled_length = self.length * sf

            # ограничение движения по X
            x_min = int(self.base_x * sfw)
            x_max = x_min + int(scaled_length)
            new_x = max(x_min, min(pos[0], x_max))

            # нормализуем громкость в диапазон [min_val, max_val]
            t = (new_x - x_min) / (x_max - x_min)
            self.value = self.min_val + t * (self.max_val - self.min_val)
            pygame.mixer.music.set_volume(self.value ** 2)

            # сдвигаем ползунок
            self._rect.x = new_x - self._rect.width // 2

    def draw(self, surface):
        """Draws the slider ball"""
        super().draw(surface)

# ----------------------------
# Base Page
# ----------------------------
class Page:
    def __init__(self, image, base_w, base_h, scale=1):
        self.base_img = image
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

    def change_theme(self, theme_index, refresh=True):
        """Загружает новый набор ассетов и обновляет страницы."""
        global bg, title_img, authors_img, menu_img
        global spl_img, spl_hov_img, mpl_img, mpl_hov_img, set_img, set_hov_img, quit_img, quit_hov_img
        global deco, name_img, volume_img, theme_img
        global col1_img, col2_img, col3_img, col4_img, col5_img
        global slider_img, main_img, main_hov_img, lead_img, lead_hov_img, back_img, back_hov_img
        global menu_page, settings_page, leaderboard_page, map_choice_page, singleplayer_page
        global random, draw, choice, draw_img, draw_hov_img, rand_img, rand_hov_img
        global game_img, bonuses

        menu_path = f"Assets/Menu{theme_index}"
        set_path = f"Assets/Settings{theme_index}"
        map_path = f"Assets/Map{theme_index}"

        # Меню
        # title_img = load_image("Assets/Menu1/Title.png")
        # authors_img = load_image("Assets/Menu1/Authors.png")
        menu_img = load_image(f"{menu_path}/Menu.png")
        spl_img = load_image(f"{menu_path}/Buttons/Spl_img.png")
        spl_hov_img = load_image(f"{menu_path}/Buttons/Spl_hov_img.png")
        mpl_img = load_image(f"{menu_path}/Buttons/Mpl_img.png")
        mpl_hov_img = load_image(f"{menu_path}/Buttons/Mpl_hov_img.png")
        set_img = load_image(f"{menu_path}/Buttons/Set_img.png")
        set_hov_img = load_image(f"{menu_path}/Buttons/Set_hov_img.png")
        quit_img = load_image(f"{menu_path}/Buttons/Quit_img.png")
        quit_hov_img = load_image(f"{menu_path}/Buttons/Quit_hov_img.png")

        # Настройки
        # deco = load_image("Assets/Settings1/Deco.png")
        # name_img = load_image("Assets/Settings1/Name.png")
        # volume_img = load_image("Assets/Settings1/Volume.png")
        # theme_img = load_image("Assets/Settings1/Theme.png")

        # col1_img = load_image("Assets/Settings1/Buttons/Col1_img.png")
        # col2_img = load_image("Assets/Settings1/Buttons/Col2_img.png")
        # col3_img = load_image("Assets/Settings1/Buttons/Col3_img.png")
        # col4_img = load_image("Assets/Settings1/Buttons/Col4_img.png")
        # col5_img = load_image("Assets/Settings1/Buttons/Col5_img.png")
        # slider_img = load_image("Assets/Settings1/Buttons/Slider_img.png")

        bg = load_image(f"Assets/Bg{theme_index}.png")

        main_img = load_image(f"{set_path}/Buttons/Main_img.png")
        main_hov_img = load_image(f"{set_path}/Buttons/Main_hov_img.png")
        lead_img = load_image(f"{set_path}/Buttons/Lead_img.png")
        lead_hov_img = load_image(f"{set_path}/Buttons/Lead_hov_img.png")
        back_img = load_image(f"{set_path}/Buttons/Back_img.png")
        back_hov_img = load_image(f"{set_path}/Buttons/Back_hov_img.png")

        #Выбор карты
        # random = load_image(f"Assets/Map1/Random.png")
        # draw = load_image(f"Assets/Map1/Draw.png")
        choice = load_image(f"{map_path}/Choice.png")
        # draw_img = load_image(f"Assets/Map1/Buttons/Draw_img.png")
        # draw_hov_img = load_image(f"Assets/Map1/Buttons/Draw_hov_img.png")
        # rand_img = load_image(f"Assets/Map1/Buttons/Rand_img.png")
        # rand_hov_img = load_image(f"Assets/Map1/Buttons/Rand_hov_img.png")

        #Синглплеер
        game_img = load_image(f"{map_path}/Game_img.png")
        bonuses = load_image(f"{map_path}/Bonuses.png")

        # Обновление страниц
        menu_page = Menu(bg, BASE_WIDTH, BASE_HEIGHT)
        leaderboard_page = Leaderboard(bg, BASE_WIDTH, BASE_HEIGHT)
        map_choice_page = MapChoice(bg, BASE_WIDTH, BASE_HEIGHT)
        singleplayer_page = Singleplayer(bg, BASE_WIDTH, BASE_HEIGHT)

        new_settings_page = Settings(bg, BASE_WIDTH, BASE_HEIGHT)

        if isinstance(self, Settings):
            self.__dict__.update(new_settings_page.__dict__)
            settings_page = self
        else:
            settings_page = new_settings_page

        if refresh:
            self.base_img = bg
            self._bg_scaled = None
            self.on_resize(pygame.display.get_surface().get_size())
            self.draw(pygame.display.get_surface())
            pygame.display.flip()

# ----------------------------
# Menu1 Page
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


#----------------------------
#Settings1 Page
#----------------------------
class Settings(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)

        self.deco1 = Widget(110, 91, deco, BASE_WIDTH, BASE_HEIGHT)
        self.deco2 = Widget(1610, 91, deco, BASE_WIDTH, BASE_HEIGHT)
        self.name = Widget(211, 275, name_img, BASE_WIDTH, BASE_HEIGHT)
        self.volume = Widget(211, 424, volume_img, BASE_WIDTH, BASE_HEIGHT)
        self.theme = Widget(211, 573, theme_img, BASE_WIDTH, BASE_HEIGHT)
        self.slider = Slider(430, 432, slider_img, BASE_WIDTH, BASE_HEIGHT, length=290, max_val=0.5)

        self.main_but = Button(434, 53, main_img, main_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.lead_but = Button(1010, 53, lead_img, lead_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.back_but = Button(1350, 913, back_img, back_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.col1 = Button(440, 567, col1_img, col1_img, BASE_WIDTH, BASE_HEIGHT)
        self.col2 = Button(540, 567, col2_img, col2_img, BASE_WIDTH, BASE_HEIGHT)
        self.col3 = Button(640, 567, col3_img, col3_img, BASE_WIDTH, BASE_HEIGHT)
        self.col4 = Button(740, 567, col4_img, col4_img, BASE_WIDTH, BASE_HEIGHT)
        self.col5 = Button(840, 567, col5_img, col5_img, BASE_WIDTH, BASE_HEIGHT)

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
                self.slider.handle_event(event, surface)
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


class MapChoice(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.choice_sel = Widget(470, 153, choice, BASE_WIDTH, BASE_HEIGHT)
        self.rand_text = Widget(605, 855, random, BASE_WIDTH, BASE_HEIGHT)
        self.draw_text = Widget(1157, 855, draw, BASE_WIDTH, BASE_HEIGHT)
        self.rand_but = Button(536, 428, rand_img, rand_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.draw_but = Button(1044, 428, draw_img, draw_hov_img, BASE_WIDTH, BASE_HEIGHT)

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
# ----------------------------
# Simple Page placeholders
# ----------------------------
class Singleplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.game_bg = Widget(108, 90, game_img, BASE_WIDTH, BASE_HEIGHT)
        self.bonuses = Widget(1144, 489, bonuses, BASE_WIDTH, BASE_HEIGHT)
        self.back_but = Button(1350, 913, back_img, back_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.score_txt = Widget(1213, 107, score, BASE_WIDTH, BASE_HEIGHT)
        self.time_txt = Widget(1213, 228, time, BASE_WIDTH, BASE_HEIGHT)
        self.dif_lvl_txt = Widget(1213, 349, dif_lvl, BASE_WIDTH, BASE_HEIGHT)

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

class Multiplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)


# ----------------------------
# Game Setup
# ----------------------------
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

BASE_WIDTH, BASE_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((BASE_WIDTH // 2, BASE_HEIGHT // 2),
                                 pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
pygame.display.set_caption('Pacman Remastered')

mixer.init()
mixer.music.load("Assets/main_music.mp3")
mixer.music.set_volume(0.05)

# Load background and assets using cache
bg = load_image('Assets/Bg1.png')

title_img = load_image('Assets/Menu1/Title.png')
authors_img = load_image('Assets/Menu1/Authors.png')
menu_img = load_image('Assets/Menu1/Menu.png')
spl_img = load_image('Assets/Menu1/Buttons/Spl_img.png')
spl_hov_img = load_image('Assets/Menu1/Buttons/Spl_hov_img.png')
mpl_img = load_image('Assets/Menu1/Buttons/Mpl_img.png')
mpl_hov_img = load_image('Assets/Menu1/Buttons/Mpl_hov_img.png')
set_img = load_image('Assets/Menu1/Buttons/Set_img.png')
set_hov_img = load_image('Assets/Menu1/Buttons/Set_hov_img.png')
quit_img = load_image('Assets/Menu1/Buttons/Quit_img.png')
quit_hov_img = load_image('Assets/Menu1/Buttons/Quit_hov_img.png')

deco = load_image('Assets/Settings1/Deco.png')
name_img = load_image('Assets/Settings1/Name.png')
volume_img = load_image('Assets/Settings1/Volume.png')
theme_img = load_image('Assets/Settings1/Theme.png')
col1_img = load_image('Assets/Settings1/Buttons/Col1_img.png')
col2_img = load_image('Assets/Settings1/Buttons/Col2_img.png')
col3_img = load_image('Assets/Settings1/Buttons/Col3_img.png')
col4_img = load_image('Assets/Settings1/Buttons/Col4_img.png')
col5_img = load_image('Assets/Settings1/Buttons/Col5_img.png')
slider_img = load_image('Assets/Settings1/Buttons/Slider_img.png')
main_img = load_image('Assets/Settings1/Buttons/Main_img.png')
main_hov_img = load_image('Assets/Settings1/Buttons/Main_hov_img.png')
lead_img = load_image('Assets/Settings1/Buttons/Lead_img.png')
lead_hov_img = load_image('Assets/Settings1/Buttons/Lead_hov_img.png')
back_img = load_image('Assets/Settings1/Buttons/Back_img.png')
back_hov_img = load_image('Assets/Settings1/Buttons/Back_hov_img.png')

random = load_image(f"Assets/Map1/Random.png")
draw = load_image(f"Assets/Map1/Draw.png")
choice = load_image(f"Assets/Map1/Choice.png")
draw_img = load_image(f"Assets/Map1/Buttons/Draw_img.png")
draw_hov_img = load_image(f"Assets/Map1/Buttons/Draw_hov_img.png")
rand_img = load_image(f"Assets/Map1/Buttons/Rand_img.png")
rand_hov_img = load_image(f"Assets/Map1/Buttons/Rand_hov_img.png")

score = load_image(f"Assets/Map1/Score.png")
time = load_image(f"Assets/Map1/Time.png")
dif_lvl = load_image(f"Assets/Map1/Dif_lvl.png")
game_img = load_image(f"Assets/Map1/Game_img.png")
bonuses = load_image(f"Assets/Map1/Bonuses.png")

# Create pages
menu_page = Menu(bg, BASE_WIDTH, BASE_HEIGHT)
settings_page = Settings(bg, BASE_WIDTH, BASE_HEIGHT)
leaderboard_page = Leaderboard(bg, BASE_WIDTH, BASE_HEIGHT)
map_choice_page = MapChoice(bg, BASE_WIDTH, BASE_HEIGHT)
singleplayer_page = Singleplayer(bg, BASE_WIDTH, BASE_HEIGHT)

current_page = "menu"
mixer.music.play(loops=-1)
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
    elif current_page == "map_choice":
        current_page = map_choice_page.run(screen)
    elif current_page == "multi_player":
        current_page = "menu"
    elif current_page == "settings":
        current_page = settings_page.run(screen)
    elif current_page == "leaderboard":
        current_page = leaderboard_page.run(screen)
    elif current_page == "singleplayer":
        current_page = singleplayer_page.run(screen)

pygame.quit()
sys.exit()

