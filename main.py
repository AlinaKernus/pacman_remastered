import pygame
import sys
import os
from pygame import mixer
from src.utils.config import Config

# initialize pygame
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

screen = pygame.display.set_mode((Config.BASE_WIDTH // 2, Config.BASE_HEIGHT // 2),
                                pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
pygame.display.set_caption('Pacman Remastered')


if __name__ == "__main__":
    from src.utils.router import router_manager

    # music
    mixer.init()
    mixer.music.load("Assets/main_music.mp3")
    mixer.music.set_volume(0.05)
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
        elif router_manager.current_page == "multi_player":
            router_manager.current_page = "menu"
        elif router_manager.current_page == "settings":
            router_manager.current_page = router_manager.settings_page.run(screen)
        elif router_manager.current_page == "leaderboard":
            router_manager.current_page = router_manager.leaderboard_page.run(screen)
        elif router_manager.current_page == "singleplayer":
            router_manager.current_page = router_manager.singleplayer_page.run(screen)

    pygame.quit()
    sys.exit()

