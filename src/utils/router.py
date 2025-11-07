from src.pages.menu import Menu
from src.pages.settings import Settings
from src.pages.leaderboard import Leaderboard
from src.pages.map_choice import MapChoice
from src.pages.singleplayer import Singleplayer
from src.utils.image import image_cache_manager
from src.utils.config import Config

class Router:
    menu_page = Menu(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)
    settings_page = Settings(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)
    leaderboard_page = Leaderboard(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)
    map_choice_page = MapChoice(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)
    singleplayer_page = Singleplayer(image_cache_manager.bg, Config.BASE_WIDTH, Config.BASE_HEIGHT)
    current_page = "menu"


router_manager = Router()