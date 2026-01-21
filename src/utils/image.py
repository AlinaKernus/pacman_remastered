import pygame
import os
from src.utils.path_helper import get_resource_path

_image_cache = {}

def load_image(path):
    """Load image once and cache it (convert_alpha applied)."""
    global _image_cache
    if path not in _image_cache:
        # Use resource path helper for exe compatibility
        full_path = get_resource_path(path)
        _image_cache[path] = pygame.image.load(full_path).convert_alpha()
    return _image_cache[path]


class ImageCache:
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
    game_img = load_image(f"Assets/Map1/Game_img_new.png")
    bonuses = load_image(f"Assets/Map1/Bonuses.png")


image_cache_manager = ImageCache()