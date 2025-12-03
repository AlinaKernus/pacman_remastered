import pygame
import random
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
        self.difficulty = 1
        self.game_over = False
        self.difficulty = 1  # Уровень сложности (начинается с 1)
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

        # При полном новом запуске (default map) сбрасываем счет, жизни, сложность
        if map_type == "default":
            self.score = 0
            self.lives = 3
            self.difficulty = 1
            self.game_over = False

        # Инициализируем спрайты пакмана и призраков для отображения во время задержки
        # Вызываем update один раз без движения, чтобы загрузить спрайты
        if self.pacman:
            self.pacman.screen.fill(color_transparent)
            sprite_path = f"Static/Sprites/Pacman/Pacman-{self.pacman.get_sprite()}"
            try:
                sprite = pygame.image.load(sprite_path)
                self.pacman.screen.blit(sprite, (0, 0))
            except:
                pass
        
        for ghost in self.ghosts:
            ghost.screen.fill(color_transparent)
            sprite_path = None
            if ghost.mode == "Normal":
                sprite_path = f"Static/Sprites/{str(ghost.name)}/{str(ghost.name)}-{ghost.direction_movement}.png"
            elif ghost.mode == "Scared":
                sprite_path = f"Static/Sprites/Ghost-Scared.png"
            if sprite_path:
                try:
                    sprite = pygame.image.load(sprite_path)
                    ghost.screen.blit(sprite, (0, 0))
                except:
                    pass

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
        
        # Если игра окончена - не обновляем логику, только перерисовываем
        if self.game_over:
            self.screen_map.fill(color_black)
            self.screen.fill(color_black)
            self.render_map()
            self.render_food()
            self.render_ghosts()
            self.render_pacman()
            self.render_ui()
            self.screen.blit(self.screen_map, (0, 0))
            return
        
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
        elif is_in_start_delay:
            # Во время задержки обновляем только спрайты без анимации и движения
            # Показываем статичный спрайт пакмана (закрытый рот) без анимации
            if self.pacman:
                self.pacman.screen.fill(color_transparent)
                # Используем статичный спрайт "Closed" без анимации
                sprite_path = f"Static/Sprites/Pacman/Pacman-Closed.png"
                try:
                    sprite = pygame.image.load(sprite_path)
                    self.pacman.screen.blit(sprite, (0, 0))
                except:
                    pass
            # Обновляем спрайты призраков (статичные, без анимации)
            for ghost in self.ghosts:
                ghost.screen.fill(color_transparent)
                sprite_path = None
                if ghost.mode == "Normal":
                    sprite_path = f"Static/Sprites/{str(ghost.name)}/{str(ghost.name)}-{ghost.direction_movement}.png"
                elif ghost.mode == "Scared":
                    sprite_path = f"Static/Sprites/Ghost-Scared.png"
                if sprite_path:
                    try:
                        sprite = pygame.image.load(sprite_path)
                        ghost.screen.blit(sprite, (0, 0))
                    except:
                        pass
        
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
            # Сохраняем текущий счет и сложность перед перезапуском
            saved_score = self.score
            saved_difficulty = self.difficulty
            # Увеличиваем сложность
            self.difficulty += 1
            self.setup("generated")
            # Восстанавливаем счет и устанавливаем новую сложность после перезапуска
            self.score = saved_score
            self.difficulty = saved_difficulty + 1

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
        if user_input[pygame.K_h]:
            # Dev option: собрать все точки и перезапустить игру
            self.collect_all_points()
            self.ivent_timer = 0

    def collect_all_points(self):
        """Собирает все оставшиеся точки и перезапускает игру с сохранением счета"""
        # Симулируем процесс сбора всех точек
        # Подсчитываем очки за все оставшиеся точки
        points_collected = len(self.food) * 10
        # Добавляем очки к счету
        self.score += points_collected
        
        # Очищаем все точки (симулируем их сбор)
        self.food = []
        
        # Сохраняем текущий счет, жизни и сложность
        saved_score = self.score
        saved_lives = self.lives
        saved_difficulty = self.difficulty
        
        # Увеличиваем сложность
        self.difficulty += 1
        
        # Симулируем процесс победы - генерируем новую карту
        win_sound = pygame.mixer.Sound('Static/Sounds/win.ogg')
        if self.music_manager and not self.music_manager.is_sounds_muted():
            self.music_manager.play_sound(win_sound)
        elif not self.music_manager:
            win_sound.play()
        
        # Генерируем новую карту (как при обычной победе)
        make_a_record(self.username, self.score)
        self.setup("generated")
        
        # Восстанавливаем счет, жизни и устанавливаем новую сложность
        self.score = saved_score
        self.lives = saved_lives
        self.difficulty = saved_difficulty + 1

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

        if self.lives > 0:
            self.lives -= 1
            width = self.screen_map.get_height() // len(self.map)
            qw = width // 4 #quater width
            pacman_spawn = get_pacman_spawn(self.map)
            self.pacman = PacMan(width + 2 * qw, self.map, pacman_spawn, width)
            self.ghosts = self.init_ghosts()
            # Устанавливаем задержку при продолжении игры после смерти
            self.start_delay_start_time = pygame.time.get_ticks()
        else:
            make_a_record(self.username, self.score)
            self.game_over = True

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

        # Отображаем Game Over, если игра окончена
        if self.game_over:
            game_over_text = regular_font_large.render("GAME OVER", True, color_red)
            self.screen.blit(
                game_over_text,
                (middle - game_over_text.get_width() // 2, 550),
            )

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

        # Текущая сложность
        difficulty = getattr(self, "difficulty", 1)

        # Количество призраков:
        # начинается с 2, каждые 3 уровня сложности добавляется еще один
        # 1-3 -> 2 призрака, 4-6 -> 3, 7-9 -> 4, 10-12 -> 5, и т.д.
        num_ghosts = 2 + max(0, (difficulty - 1) // 3)

        # Порядок чередования типов призраков
        ghost_types_cycle = ["Blinky", "Pinky", "Inky", "Clyde"]
        # Базовые позиции относительно spawn для первых четырех призраков
        # Собираем все клетки внутри комнаты призраков вокруг точки spawn
        house_cells = []
        for i in range(sp_i - 2, sp_i + 3):
            # Сканируем комнату шире вправо (еще +3 клетки)
            for j in range(sp_j - 3, sp_j + 8):
                if 0 <= i < len(self.map) and 0 <= j < len(self.map[0]):
                    if self.map[i][j] in ["U", "g"]:
                        house_cells.append((i, j))

        ghosts = []
        for idx in range(num_ghosts):
            ghost_name = ghost_types_cycle[idx % len(ghost_types_cycle)]
            # Выбираем случайную свободную позицию внутри комнаты
            pos_i, pos_j = random.choice(house_cells)
            ghost = Ghost(
                ghost_name,
                width + 2 * qw,
                self.map,
                [pos_i, pos_j],
                width,
                difficulty,
            )
            ghosts.append(ghost)

        return ghosts

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
