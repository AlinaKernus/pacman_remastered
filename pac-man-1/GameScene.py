import pygame
from Variables import *
from MapGenarator import *
from PacMan import *
from Ghost import *
from FoodPiece import *
from DB_communicator import *
from TileRenderer import render_map_with_tiles


class GameScene:
    def __init__(self):
        self.screen = pygame.Surface((1280, 720))
        # Увеличиваем карту: +50 вверх и +50 вниз = +100 к высоте
        # Старая высота: 713, новая: 813
        # Пропорционально ширина: 644 * (813/713) ≈ 735
        self.screen_map = pygame.Surface((735, 813))
        self.stay_here = True
        self.username = ""
        self.paused = False
        self.music = True
        self.ivent_timer = 0
        self.pacman = None
        self.ghosts = []
        self.map = None
        self.food = []
        self.score = 0
        self.score_high = 0
        self.lives = 3
        self.start_sound = pygame.mixer.Sound('Static/Sounds/game_start.ogg')
        self.theme_index = None  # Будет установлена извне или получена из Config
        self.music_manager = None  # Будет установлен извне для проверки мута звуков
        self.start_delay_start_time = None  # Время начала задержки перед стартом игры
        self.start_delay_duration = 3000  # Задержка 3 секунды (в миллисекундах)

    def setup(self, map_type):
        if map_type == "default":
            self.map = default_map
        elif map_type == "generated":
            self.map = map_generator.generate_map()

        width = self.screen_map.get_height() // len(self.map)
        qw = width // 4 #quater width
        pacman_spawn = get_pacman_spawn(self.map)
        self.pacman = PacMan(width + 2 * qw, self.map, pacman_spawn, width)
        self.ghosts = self.init_ghosts()
        self.food = self.init_food()

        self.score = 0
        self.lives = 3

        # Устанавливаем время начала задержки
        self.start_delay_start_time = pygame.time.get_ticks()

        self.start_sound.stop()
        # Используем music_manager если доступен, иначе проигрываем напрямую
        if self.music_manager and not self.music_manager.is_sounds_muted():
            self.music_manager.play_sound(self.start_sound)
        elif not self.music_manager:
            self.start_sound.play()

    def update(self, user_input):
        self.ivent_timer += 1
        self.manage_user_input(user_input)
        
        # Проверяем задержку перед стартом игры
        is_in_start_delay = False
        if self.start_delay_start_time is not None:
            elapsed_ms = pygame.time.get_ticks() - self.start_delay_start_time
            if elapsed_ms < self.start_delay_duration:
                is_in_start_delay = True
            else:
                # Задержка прошла, сбрасываем флаг
                self.start_delay_start_time = None
        
        # Обновляем логику игры только если не на паузе и не в задержке
        if not self.paused and not is_in_start_delay:
            self.pacman.update(user_input)
            self.update_gosts()
            self.game_logic()
        
        # Отрисовываем все элементы (даже во время задержки)
        self.screen_map.fill(color_black)
        self.screen.fill(color_black)
        self.render_map()
        self.render_food()
        self.render_ghosts()
        self.render_pacman()
        self.render_ui()
        self.screen.blit(self.screen_map, (0, 0))

    def game_logic(self):
        if self.pacman_bumped_into_ghost():
            if self.ghosts[0].mode == "Normal":
                self.death()
            else:
                eat_ghost_sound = pygame.mixer.Sound('Static/Sounds/eat_ghost.ogg')
                if self.music_manager and not self.music_manager.is_sounds_muted():
                    self.music_manager.play_sound(eat_ghost_sound)
                elif not self.music_manager:
                    eat_ghost_sound.play()
                self.send_ghost_to_prison()

        if len(self.food) == 0:
            win_sound = pygame.mixer.Sound('Static/Sounds/win.ogg')
            if self.music_manager and not self.music_manager.is_sounds_muted():
                self.music_manager.play_sound(win_sound)
            elif not self.music_manager:
                win_sound.play()
            make_a_record(self.username, self.score)
            self.setup("generated")

        self.update_food()
        self.check_gates()
        self.score_high = get_high(self.username)
        self.score_high = max(self.score_high, self.score)

    def send_ghost_to_prison(self):
        for ghost in self.ghosts:
            if self.pacman.pos_x == ghost.pos_x and self.pacman.pos_y == ghost.pos_y:
                spawn = get_ghost_spawn(self.map)
                sp_i = spawn[0]
                sp_j = spawn[1]
                ghost.pos_x = sp_j + 2
                ghost.pos_y = sp_i
                width = self.screen_map.get_height() // len(self.map)
                ghost.screen_pos_x = width * ghost.pos_x - width // 4
                ghost.screen_pos_y = width * ghost.pos_y - width // 4
        num_of_ghost = self.how_many_prisoned_ghosts()
        self.score += (200 * num_of_ghost)

    def manage_user_input(self, user_input):
        if self.ivent_timer < 10:
            return
        if user_input[pygame.K_p]:
            self.paused = not self.paused
            self.ivent_timer = 0
        if user_input[pygame.K_r] and user_input[pygame.K_c]:
            self.replay_on_current_map()
            self.ivent_timer = 0
        if user_input[pygame.K_r] and user_input[pygame.K_g]:
            self.setup("generated")
            self.ivent_timer = 0
        if user_input[pygame.K_r] and user_input[pygame.K_d]:
            self.setup("default")
            self.ivent_timer = 0
        if user_input[pygame.K_v]:
            self.stay_here = False
        if user_input[pygame.K_m]:
            self.music = not self.music
            if self.music:
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.pause()
            self.ivent_timer = 0

    def replay_on_current_map(self):
        width = self.screen_map.get_height() // len(self.map)
        qw = width // 4 #quater width
        pacman_spawn = get_pacman_spawn(self.map)
        self.pacman = PacMan(width + 2 * qw, self.map, pacman_spawn, width)
        self.ghosts = self.init_ghosts()
        self.food = self.init_food()
        self.score = 0
        self.lives = 3
        # Устанавливаем задержку при перезапуске
        self.start_delay_start_time = pygame.time.get_ticks()

    def death(self):
        death_sound = pygame.mixer.Sound('Static/Sounds/death.ogg')
        if self.music_manager and not self.music_manager.is_sounds_muted():
            self.music_manager.play_sound(death_sound)
        elif not self.music_manager:
            death_sound.play()

        self.lives -= 1

        if self.lives > 0:
            width = self.screen_map.get_height() // len(self.map)
            qw = width // 4 #quater width
            pacman_spawn = get_pacman_spawn(self.map)
            self.pacman = PacMan(width + 2 * qw, self.map, pacman_spawn, width)
            self.ghosts = self.init_ghosts()
            # Устанавливаем задержку при продолжении игры после смерти
            self.start_delay_start_time = pygame.time.get_ticks()
        else:
            make_a_record(self.username, self.score)
            self.setup("generated")

    def render_ui(self):
        small_font = pygame.font.Font('Static/Fonts/mini_pixel-7.ttf', 23)
        regular_font = pygame.font.Font('Static/Fonts/mini_pixel-7.ttf', 30)
        regular_font_large = pygame.font.Font('Static/Fonts/mini_pixel-7.ttf', 40)
        header_font = pygame.font.Font('Static/Fonts/PAC-FONT.ttf', 98)
        header = header_font.render("Pac---Man", True, color_white)
        score_text = regular_font_large.render(
            f"Score: {str(self.score)}", True, color_white
        )

        lives_text = regular_font_large.render(
            f"Lives: {str(self.lives)}", True, color_white
        )

        replay_default_text = regular_font.render("R + D -> replay on default map", True, color_white)
        replay_generated_text = regular_font.render("R + G -> replay on generated map", True, color_white)
        replay_text = regular_font.render("R + C -> replay on current map", True, color_white)
        see_records_text = regular_font.render("V     -> see records", True, color_white)
        pause_text = regular_font.render("P     -> play/pause", True, color_white)
        escape_text = regular_font.render("Esc   -> quit game", True, color_white)
        paused_text = regular_font_large.render("PAUSED", True, color_white)
        username_text = regular_font_large.render(
            f"Player: {self.username}", True, color_white
        )

        high_score_text = regular_font_large.render(
            f"High: {str(self.score_high)}", True, color_white
        )

        mute_music_text = None
        if self.music:
            mute_music_text = regular_font.render("M     -> mute music", True, color_white)
        else:
            mute_music_text = regular_font.render("M     -> unmute music", True, color_white)
        credit_text = small_font.render("G.Koganovskiy 2020", True, color_white)
        self.screen.blit(header, (self.screen_map.get_width() + 20, 10))
        self.screen.blit(score_text, (self.screen_map.get_width() + 20, 120))
        self.screen.blit(high_score_text,  (self.screen_map.get_width() + 20, 150))
        self.screen.blit(lives_text, (self.screen_map.get_width() + 20, 180))
        self.screen.blit(username_text, (self.screen_map.get_width() + 20, 220))
        self.screen.blit(pause_text, (self.screen_map.get_width() + 20, 310))
        self.screen.blit(replay_text, (self.screen_map.get_width() + 20, 340))
        self.screen.blit(replay_generated_text, (self.screen_map.get_width() + 20, 370))
        self.screen.blit(replay_default_text, (self.screen_map.get_width() + 20, 400))
        self.screen.blit(see_records_text, (self.screen_map.get_width() + 20, 430))
        self.screen.blit(mute_music_text, (self.screen_map.get_width() + 20, 460))
        self.screen.blit(escape_text, (self.screen_map.get_width() + 20, 490))
        self.screen.blit(credit_text, (self.screen.get_width() - credit_text.get_width() - 10, self.screen.get_height() - 20))
        middle = (self.screen.get_width() - self.screen_map.get_width()) // 2 + self.screen_map.get_width()
        if self.paused:
            self.screen.blit(paused_text, (middle - paused_text.get_width() // 2, 550))

    def check_gates(self):
        gates_pos = get_gates_pos(self.map)
        i = gates_pos[0]
        j = gates_pos[1]
        if self.prisoned_ghosts():
            self.map[i][j] = 'U'
            self.map[i][j + 1] = 'U'
        else:
            self.map[i][j] = '#'
            self.map[i][j + 1] = '#'

    def prisoned_ghosts(self):
        for ghost in self.ghosts:
            i = ghost.pos_y
            j = ghost.pos_x
            if self.map[i][j] == 'U' and ghost.mode == "Normal":
                return True
        return False

    def how_many_prisoned_ghosts(self):
        result = 0
        for ghost in self.ghosts:
            i = ghost.pos_y
            j = ghost.pos_x
            if self.map[i][j] in ['U', 'g']:
                result += 1
        return result

    def scare_ghosts(self):
        for ghost in self.ghosts:
            ghost.go_to_scare_mode()

    def update_food(self):
        ind = 0
        while ind < len(self.food):
            food_piece = self.food[ind]
            i = food_piece.i
            j = food_piece.j
            if self.pacman.pos_y == i and self.pacman.pos_x == j:
                if food_piece.type == "Energizer":
                    energizer_sound = pygame.mixer.Sound('Static/Sounds/energizer.ogg')
                    if self.music_manager and not self.music_manager.is_sounds_muted():
                        self.music_manager.play_sound(energizer_sound)
                    elif not self.music_manager:
                        energizer_sound.play()
                    self.scare_ghosts()
                if len(self.food) % 4 == 0:
                    eat_sound = pygame.mixer.Sound('Static/Sounds/eating.ogg')
                    if self.music_manager and not self.music_manager.is_sounds_muted():
                        self.music_manager.play_sound(eat_sound)
                    elif not self.music_manager:
                        eat_sound.play()
                self.food.pop(ind)
                self.score += 10
            ind += 1

    def render_food(self):
        width = self.screen_map.get_height() // len(self.map)
        for food_piece in self.food:
            i = food_piece.i
            j = food_piece.j
            if food_piece.type == "Energizer":
                if self.ivent_timer % 30 > 15:
                    pygame.draw.circle(self.screen_map, color_food, (j * width + width // 2, i * width + width // 2), 12)
            else:
                pygame.draw.circle(self.screen_map, color_food, (j * width + width // 2, i * width + width // 2), 3)

    def init_food(self):
        food_array = []
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if self.map[i][j] == 'O':
                    new_food_piece = None
                    if (i == 1 and j == 1) or (i == 29 and j == 1) or (i == 1 and j == 26) or (i == 29 and j == 26):
                        new_food_piece = FoodPiece(i, j, "Energizer")
                    else:
                        new_food_piece = FoodPiece(i, j)
                    food_array.append(new_food_piece)
        return food_array

    def pacman_bumped_into_ghost(self):
        return any(
            self.pacman.pos_x == ghost.pos_x and self.pacman.pos_y == ghost.pos_y
            for ghost in self.ghosts
        )

    def update_gosts(self):
        blinky = self.ghosts[0]
        for ghost in self.ghosts:
            ghost.update(self.pacman, blinky)

    def render_map(self):
        width = self.screen_map.get_height() // len(self.map)
        # Получаем текущую тему
        if self.theme_index is not None:
            theme_index = self.theme_index
        else:
            # Пытаемся получить из Config
            try:
                import sys
                import os
                # Добавляем путь к src для импорта Config
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                src_path = os.path.abspath(os.path.join(project_root, "src"))
                if src_path not in sys.path:
                    sys.path.insert(0, src_path)
                from utils.config import Config
                theme_index = Config.CURRENT_THEME
            except:
                # Fallback если импорт не удался
                theme_index = 1
        
        # Отрисовываем карту используя тайлы из старой версии с цветами темы
        # render_map_with_tiles теперь сам заливает фон цветом темы
        render_map_with_tiles(self.screen_map, self.map, width, theme_index)

    def render_pacman(self):
        self.screen_map.blit(self.pacman.screen, (self.pacman.screen_pos_x, self.pacman.screen_pos_y))

    def render_ghosts(self):
        for ghost in self.ghosts:
            self.screen_map.blit(ghost.screen, (ghost.screen_pos_x, ghost.screen_pos_y))

    def init_ghosts(self):
        width = self.screen_map.get_height() // len(self.map)
        qw = width // 4 #quater width
        spawn = get_ghost_spawn(self.map)
        sp_i = spawn[0]
        sp_j = spawn[1]
        blinky = Ghost("Blinky", width + 2 * qw, self.map, [sp_i, sp_j + 2], width)
        pinky = Ghost("Pinky", width + 2 * qw, self.map, [sp_i, sp_j + 3], width)
        inky = Ghost("Inky", width + 2 * qw, self.map, [sp_i + 1, sp_j + 2], width)
        clyde = Ghost("Clyde", width + 2 * qw, self.map, [sp_i + 1, sp_j + 3], width)
        return [blinky, pinky, inky, clyde]

def get_render_lines(map, i, j):
    result = [False, False, False, False] #up - right - down - left
    if map[i][j] == '#':
        if i == 0 or map[i - 1][j] != '#':
            result[0] = True
        if j == len(map[0]) - 1 or map[i][j + 1] != '#':
            result[1] = True
        if i == len(map) - 1 or map[i + 1][j] != '#':
            result[2] = True
        if j == 0 or map[i][j - 1] != '#':
            result[3] = True
    return result


def get_pacman_spawn(map):
    result = [None, None]
    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] == 'p':
                result[0] = i
                result[1] = j
                return result


def get_ghost_spawn(map):
    result = [None, None]
    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] == 'g':
                result[0] = i
                result[1] = j
                return result


def get_gates_pos(map):
    result = [None, None]
    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] == 'g':
                result[0] = i - 2
                result[1] = j + 2
                return result
