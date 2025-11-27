import pygame
from src.utils.image import load_image
from src.utils.config import Config
from src.utils.image import image_cache_manager
from src.widgets.sound_icon import SoundIcon
from src.utils.music_manager import music_manager

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
        
        # Иконка звука для всех страниц
        self.sound_icon = SoundIcon(base_w, base_h)

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
        
        # Иконка звука
        if hasattr(self, 'sound_icon'):
            self.sound_icon.resize(window_size)

    def draw(self, surface):
        """Draw background (cached). Widgets draw themselves."""
        window_size = surface.get_size()
        if self._last_window_size != window_size or self._bg_scaled is None:
            self.on_resize(window_size)
        surface.blit(self._bg_scaled, (0, 0))

    def change_theme(self, theme_index, refresh=True):
        """Загружает новый набор ассетов и обновляет страницы."""
        # Сохраняем текущую тему в Config
        Config.CURRENT_THEME = theme_index
        # Сохраняем тему в настройках
        from src.utils.settings_manager import settings_manager
        settings_manager.set_setting("theme", theme_index)

        menu_path = f"Assets/Menu{theme_index}"
        set_path = f"Assets/Settings{theme_index}"
        map_path = f"Assets/Map{theme_index}"

        image_cache_manager.menu_img = load_image(f"{menu_path}/Menu.png")
        image_cache_manager.spl_img = load_image(f"{menu_path}/Buttons/Spl_img.png")
        image_cache_manager.spl_hov_img = load_image(f"{menu_path}/Buttons/Spl_hov_img.png")
        image_cache_manager.mpl_img = load_image(f"{menu_path}/Buttons/Mpl_img.png")
        image_cache_manager.mpl_hov_img = load_image(f"{menu_path}/Buttons/Mpl_hov_img.png")
        image_cache_manager.set_img = load_image(f"{menu_path}/Buttons/Set_img.png")
        image_cache_manager.set_hov_img = load_image(f"{menu_path}/Buttons/Set_hov_img.png")
        image_cache_manager.quit_img = load_image(f"{menu_path}/Buttons/Quit_img.png")
        image_cache_manager.quit_hov_img = load_image(f"{menu_path}/Buttons/Quit_hov_img.png")

        image_cache_manager.bg = load_image(f"Assets/Bg{theme_index}.png")

        image_cache_manager.main_img = load_image(f"{set_path}/Buttons/Main_img.png")
        image_cache_manager.main_hov_img = load_image(f"{set_path}/Buttons/Main_hov_img.png")
        image_cache_manager.lead_img = load_image(f"{set_path}/Buttons/Lead_img.png")
        image_cache_manager.lead_hov_img = load_image(f"{set_path}/Buttons/Lead_hov_img.png")
        image_cache_manager.back_img = load_image(f"{set_path}/Buttons/Back_img.png")
        image_cache_manager.back_hov_img = load_image(f"{set_path}/Buttons/Back_hov_img.png")

        #Выбор карты
        image_cache_manager.choice = load_image(f"{map_path}/Choice.png")

        #Синглплеер
        image_cache_manager.game_img = load_image(f"{map_path}/Game_img_new.png")
        image_cache_manager.bonuses = load_image(f"{map_path}/Bonuses.png")

        # Обновление страниц
        from src.pages.menu import Menu
        from src.pages.settings import Settings
        from src.pages.leaderboard import Leaderboard
        from src.pages.map_choice import MapChoice
        from src.pages.singleplayer import Singleplayer
        from src.utils.router import router_manager

        router_manager.menu_page = Menu(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        router_manager.leaderboard_page = Leaderboard(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        router_manager.map_choice_page = MapChoice(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)
        router_manager.singleplayer_page = Singleplayer(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        new_settings_page = Settings(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)

        if isinstance(self, Settings):
            self.__dict__.update(new_settings_page.__dict__)
            settings_page = self
        else:
            settings_page = new_settings_page

        if refresh:
            self.base_img = image_cache_manager.bg
            self._bg_scaled = None
            self.on_resize(pygame.display.get_surface().get_size())
            self.draw(pygame.display.get_surface())
            pygame.display.flip()