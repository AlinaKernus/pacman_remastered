"""
Модуль для отрисовки карты используя тайлы из старой версии игры
"""
import pygame
import os
import sys

# Добавляем путь к src для импорта Config
# pac-man-1/TileRenderer.py -> корень проекта -> src
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.abspath(os.path.join(project_root, "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from utils.config import Config
except ImportError:
    # Fallback если импорт не удался
    class Config:
        CURRENT_THEME = 1

# Путь к тайлам
TILES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "res", "tiles")

# Кэш загруженных тайлов
_tile_cache = {}
# Кэш раскрашенных тайлов для каждой темы (ключ: (tile_name, theme_index))
_colored_tile_cache = {}

def get_theme_colors(theme_index):
    """
    Возвращает цвета для темы: (фон, края_светлые, заполнение, тени)
    """
    # Цвета фона для каждой темы (в RGB)
    theme_backgrounds = {
        1: (4, 0, 22),      # 040016 - темно-синий
        2: (0, 28, 1),      # 001C01 - темно-зеленый
        3: (53, 3, 0),      # 350300 - темно-коричневый/красный
        4: (42, 43, 0),     # 2A2B00 - темно-желтый/оливковый
        5: (54, 0, 28),     # 36001C - темно-пурпурный/фиолетовый
    }
    
    bg_color = theme_backgrounds.get(theme_index, (0, 0, 0))
    
    # Создаем яркие цвета для стен, как были синие раньше
    # Формат: (edge_light - яркие края, fill - заполнение, edge_shadow - тени)
    theme_wall_colors = {
        1: ((0, 191, 255), (0, 0, 139), (0, 0, 255)),         # Синяя тема - яркие синие оттенки (как было)
        2: ((0, 255, 127), (0, 100, 0), (0, 200, 0)),         # Зеленая тема - яркие зеленые оттенки
        3: ((255, 69, 0), (139, 0, 0), (255, 0, 0)),          # Красная тема - яркие красно-оранжевые оттенки
        4: ((255, 255, 0), (200, 200, 0), (255, 215, 0)),     # Желтая тема - яркие желтые оттенки
        5: ((255, 20, 147), (139, 0, 139), (255, 105, 180)),  # Розовая/фиолетовая тема - яркие розовые оттенки
    }
    
    if theme_index in theme_wall_colors:
        edge_light, fill, edge_shadow = theme_wall_colors[theme_index]
    else:
        # Fallback: создаем цвета автоматически
        edge_light = tuple(min(255, c + 100) for c in bg_color)
        fill = tuple(min(255, c + 60) for c in bg_color)
        edge_shadow = tuple(max(0, c - 20) for c in bg_color)
    
    return bg_color, edge_light, fill, edge_shadow

def load_tile(tile_name):
    """Загружает тайл из файла"""
    if tile_name in _tile_cache:
        return _tile_cache[tile_name]
    
    tile_path = os.path.join(TILES_DIR, f"{tile_name}.gif")
    if os.path.exists(tile_path):
        tile = pygame.image.load(tile_path).convert_alpha()
        _tile_cache[tile_name] = tile
        return tile
    return None

def get_wall_tile_type(map, i, j):
    """
    Определяет тип тайла стены на основе соседних клеток
    Возвращает имя тайла или None если это внутренняя стена (окружена со всех сторон)
    """
    if map[i][j] != '#':
        return None
    
    # Проверяем соседние клетки (верх, право, низ, лево)
    up = i > 0 and map[i - 1][j] == '#'
    right = j < len(map[0]) - 1 and map[i][j + 1] == '#'
    down = i < len(map) - 1 and map[i + 1][j] == '#'
    left = j > 0 and map[i][j - 1] == '#'
    
    # Определяем тип стены
    neighbors = [up, right, down, left]
    neighbor_count = sum(neighbors)
    
    # Если стена окружена со всех 4 сторон - это внутренняя стена, делаем пустое пространство
    if neighbor_count == 4:
        return None  # Не отрисовываем внутренние стены
    
    if neighbor_count == 0:
        # Изолированная стена
        return "wall-nub"
    elif neighbor_count == 1:
        # Конец стены (зеркалим)
        if up:
            return "wall-end-b"  # Если стена сверху, используем конец снизу
        elif right:
            return "wall-end-l"  # Если стена справа, используем конец слева
        elif down:
            return "wall-end-t"  # Если стена снизу, используем конец сверху
        elif left:
            return "wall-end-r"  # Если стена слева, используем конец справа
    elif neighbor_count == 2:
        # Прямая линия или угол
        if up and down:
            return "wall-straight-vert"
        elif left and right:
            return "wall-straight-horiz"
        elif up and right:
            # Угол верх-право - используем противоположный (низ-лево)
            return "wall-corner-ll"
        elif right and down:
            # Угол право-низ - используем противоположный (верх-лево)
            return "wall-corner-ul"
        elif down and left:
            # Угол низ-лево - используем противоположный (верх-право)
            return "wall-corner-ur"
        elif left and up:
            # Угол лево-верх - используем противоположный (низ-право)
            return "wall-corner-lr"
    elif neighbor_count == 3:
        # T-образное соединение
        if not up:
            return "wall-t-top"
        elif not right:
            return "wall-t-right"
        elif not down:
            return "wall-t-bottom"
        elif not left:
            return "wall-t-left"
    
    # По умолчанию
    return "wall-straight-horiz"

def apply_theme_colors(tile_surface, theme_index, tile_name=None):
    """
    Применяет цвета темы к тайлу
    Заменяет цвета тайла на цвета выбранной темы
    """
    # Проверяем кэш
    if tile_name and (tile_name, theme_index) in _colored_tile_cache:
        return _colored_tile_cache[(tile_name, theme_index)]
    
    # Оригинальные цвета в тайлах (из pacman_game.py):
    IMG_EDGE_LIGHT_COLOR = (255, 206, 255, 255)
    IMG_FILL_COLOR = (132, 0, 132, 255)
    IMG_EDGE_SHADOW_COLOR = (255, 0, 255, 255)
    IMG_PELLET_COLOR = (128, 0, 128, 255)
    
    # Получаем цвета темы
    _, edge_light, fill, edge_shadow = get_theme_colors(theme_index)
    
    # Создаем копию тайла
    colored_tile = tile_surface.copy()
    
    # Заменяем цвета точно как в старой версии
    for y in range(colored_tile.get_height()):
        for x in range(colored_tile.get_width()):
            pixel = colored_tile.get_at((x, y))
            r, g, b, a = pixel
            
            # Точное сравнение с оригинальными цветами
            if (r, g, b, a) == IMG_EDGE_LIGHT_COLOR:
                colored_tile.set_at((x, y), (*edge_light, a))
            elif (r, g, b, a) == IMG_FILL_COLOR:
                colored_tile.set_at((x, y), (*fill, a))
            elif (r, g, b, a) == IMG_EDGE_SHADOW_COLOR:
                colored_tile.set_at((x, y), (*edge_shadow, a))
            elif (r, g, b, a) == IMG_PELLET_COLOR:
                # Для пеллет используем средний цвет
                colored_tile.set_at((x, y), (*fill, a))
    
    # Сохраняем в кэш
    if tile_name:
        _colored_tile_cache[(tile_name, theme_index)] = colored_tile
    
    return colored_tile

def render_map_with_tiles(screen_map, map_data, tile_size, theme_index=None):
    """
    Отрисовывает карту используя тайлы из старой версии с цветами выбранной темы
    """
    # Получаем текущую тему из Config, если не указана
    if theme_index is None:
        try:
            theme_index = Config.CURRENT_THEME
        except:
            theme_index = 1
    
    # Получаем цвет фона для темы
    bg_color, _, _, _ = get_theme_colors(theme_index)
    
    # Заливаем экран цветом фона темы
    screen_map.fill(bg_color)
    
    # Загружаем тайлы
    wall_tiles = {}
    for tile_name in ["wall-corner-ul", "wall-corner-ur", "wall-corner-ll", "wall-corner-lr",
                      "wall-straight-horiz", "wall-straight-vert",
                      "wall-t-top", "wall-t-bottom", "wall-t-left", "wall-t-right",
                      "wall-x", "wall-end-t", "wall-end-b", "wall-end-l", "wall-end-r",
                      "wall-nub", "blank"]:
        tile = load_tile(tile_name)
        if tile:
            # Применяем цвета темы (с кэшированием)
            colored_tile = apply_theme_colors(tile, theme_index, tile_name)
            # Масштабируем тайл до нужного размера
            wall_tiles[tile_name] = pygame.transform.scale(colored_tile, (tile_size, tile_size))
    
    # Отрисовываем карту
    for i in range(len(map_data)):
        for j in range(len(map_data[0])):
            x = j * tile_size
            y = i * tile_size
            
            if map_data[i][j] == '#':
                # Определяем тип тайла для стены
                tile_type = get_wall_tile_type(map_data, i, j)
                # Если tile_type == None, значит это внутренняя стена - не отрисовываем
                if tile_type and tile_type in wall_tiles:
                    screen_map.blit(wall_tiles[tile_type], (x, y))
                else:
                    # Внутренняя стена или неизвестный тип - рисуем фон темы
                    pygame.draw.rect(screen_map, bg_color, (x, y, tile_size, tile_size))
            elif map_data[i][j] in ['O', 'U', 'p', 'g', 'p1', 'p2']:
                # Свободное пространство - используем фон темы
                pygame.draw.rect(screen_map, bg_color, (x, y, tile_size, tile_size))

