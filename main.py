import pygame
import sys
import os
from pygame import mixer
from src.utils.config import Config
from src.utils.music_manager import music_manager

# initialize pygame
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Получаем размеры экрана для окна на весь экран
screen_info = pygame.display.Info()
screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h),
                                pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
pygame.display.set_caption('Pacman Remastered')


if __name__ == "__main__":
    from src.utils.config import Config
    
    # Загружаем настройки ПЕРЕД созданием страниц, чтобы тема применилась
    Config.load_from_settings()
    # music_manager уже загрузил настройки в __init__
    
    # Теперь импортируем router_manager после загрузки настроек
    from src.utils.router import router_manager
    
    # Применяем загруженную тему к страницам (если тема не 1)
    if Config.CURRENT_THEME != 1:
        router_manager.settings_page.change_theme(Config.CURRENT_THEME, refresh=False)

    # music - используем трек из pac-man-1
    mixer.init()
    # Get correct path for exe or dev
    from src.utils.path_helper import get_resource_path
    music_path = get_resource_path("pac-man-1/Static/Sounds/background.ogg")
    mixer.music.load(music_path)
    # Громкость уже установлена из настроек в music_manager
    mixer.music.play(loops=-1)

    clock = pygame.time.Clock()
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.VIDEORESIZE:
                # recreate screen with double buffering flags to ensure consistency
                screen = pygame.display.set_mode((event.w, event.h),
                                                pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
                # notify pages about resize so they precompute scaled assets
                router_manager.menu_page.on_resize(screen.get_size())
                router_manager.settings_page.on_resize(screen.get_size())
                router_manager.leaderboard_page.on_resize(screen.get_size())
                router_manager.map_choice_page.on_resize(screen.get_size())
                router_manager.singleplayer_page.on_resize(screen.get_size())

        # draw current page by delegating to its run loop (which also handles resize internally)
        if router_manager.current_page == "menu":
            router_manager.current_page = router_manager.menu_page.run(screen)
        elif router_manager.current_page == "map_choice":
            router_manager.current_page = router_manager.map_choice_page.run(screen)
        elif router_manager.current_page == "settings":
            router_manager.current_page = router_manager.settings_page.run(screen)
        elif router_manager.current_page == "leaderboard":
            router_manager.current_page = router_manager.leaderboard_page.run(screen)
        elif router_manager.current_page == "singleplayer":
            router_manager.current_page = router_manager.singleplayer_page.run(screen)

    pygame.quit()
    sys.exit()

