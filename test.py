import random

class EllersMaze:
    def ellers_maze(self, width, height, seed=None):
        if seed is not None:
            random.seed(seed)

        # Каждая клетка в строке имеет id множества
        next_set_id = 1
        sets = [0] * width  # множества для текущей строки
        # стены: right_walls[row][col] = True, bottom_walls[row][col] = True
        right_walls = [[True]*width for _ in range(height)]
        bottom_walls = [[True]*width for _ in range(height)]

        for y in range(height):
            # 1) Присвоить новые множества если нужно
            for x in range(width):
                if sets[x] == 0:
                    sets[x] = next_set_id
                    next_set_id += 1

            # 2) Горизонтальные соединения (решаем удалять правую стену или нет)
            for x in range(width - 1):
                if sets[x] != sets[x+1]:
                    join = random.choice([True, False])
                    # Для последней строки всегда объединяем (чтобы объединить всё)
                    if y == height - 1:
                        join = True
                    if join:
                        # удаляем правую стену
                        right_walls[y][x] = False
                        old_set = sets[x+1]
                        new_set = sets[x]
                        # объединяем множества вправо
                        for i in range(width):
                            if sets[i] == old_set:
                                sets[i] = new_set
                    else:
                        # оставляем стену
                        right_walls[y][x] = True

            # 3) Вертикальные соединения (вниз)
            if y < height - 1:
                # Для каждой множества подготовим список индексов
                set_to_cells = {}
                for x in range(width):
                    set_to_cells.setdefault(sets[x], []).append(x)

                new_sets = [0] * width  # множества для следующей строки
                for s, cells in set_to_cells.items():
                    # Должен быть хотя бы один проход вниз в этом множестве
                    num_cells = len(cells)
                    # Для каждого cell решаем случайно дать проход вниз, но
                    # гарантируем хотя бы один (выбираем случайным образом один как minimal)
                    must = random.choice(cells)
                    made_any = False
                    for x in cells:
                        make_down = random.choice([True, False])
                        if x == must:
                            make_down = True
                        if make_down:
                            bottom_walls[y][x] = False
                            new_sets[x] = s
                            made_any = True
                        else:
                            bottom_walls[y][x] = True
                    # (по конструкции made_any всегда True из-за must)
                sets = new_sets

        return right_walls, bottom_walls

    def print_maze_ascii(self, width, height, right_walls, bottom_walls):
        # Верхняя граница
        print("+" + "---+" * width)
        for y in range(height):
            # Строка с вертикальными стенами
            line = "|"
            for x in range(width):
                line += "   "
                line += "|" if right_walls[y][x] else " "
            print(line)
            # Строка с горизонтальными (нижними) стенами
            line2 = "+"
            for x in range(width):
                line2 += "---+" if bottom_walls[y][x] else "   +"
            print(line2)


class WilsonMaze:
    def wilson_maze(self, width, height, seed=None):
        if seed is not None:
            random.seed(seed)

        maze = [[False]*width for _ in range(height)]  # False = unvisited
        # стены: right_walls[y][x], bottom_walls[y][x]
        right_walls = [[True]*width for _ in range(height)]
        bottom_walls = [[True]*width for _ in range(height)]

        # вспомогательная функция
        def neighbors(x, y):
            dirs = []
            if x > 0: dirs.append((-1, 0))
            if x < width - 1: dirs.append((1, 0))
            if y > 0: dirs.append((0, -1))
            if y < height - 1: dirs.append((0, 1))
            return dirs

        # 1. выбрать случайную клетку и добавить в лабиринт
        maze[random.randrange(height)][random.randrange(width)] = True

        # пока есть непосещённые
        while any(not cell for row in maze for cell in row):
            # выбрать случайную непосещённую клетку
            y, x = random.choice([(r, c) for r in range(height) for c in range(width) if not maze[r][c]])
            path = [(x, y)]

            while not maze[y][x]:
                dx, dy = random.choice(neighbors(x, y))
                nx, ny = x + dx, y + dy
                if (nx, ny) in path:
                    # обрезаем петлю
                    loop_start = path.index((nx, ny))
                    path = path[:loop_start + 1]
                else:
                    path.append((nx, ny))
                x, y = nx, ny

            # добавить путь в лабиринт (убираем стены)
            for (x1, y1), (x2, y2) in zip(path, path[1:]):
                maze[y1][x1] = True
                maze[y2][x2] = True
                if x1 == x2:
                    # движение вверх/вниз
                    if y2 > y1:
                        bottom_walls[y1][x1] = False
                    else:
                        bottom_walls[y2][x2] = False
                else:
                    # движение влево/вправо
                    if x2 > x1:
                        right_walls[y1][x1] = False
                    else:
                        right_walls[y2][x2] = False

        return right_walls, bottom_walls

    def print_maze_ascii(self, width, height, right_walls, bottom_walls):
        print("+" + "---+" * width)
        for y in range(height):
            line = "|"
            for x in range(width):
                line += "   "
                line += "|" if right_walls[y][x] else " "
            print(line)
            line2 = "+"
            for x in range(width):
                line2 += "---+" if bottom_walls[y][x] else "   +"
            print(line2)


class PrimMaze:
    def prim_maze(self, width, height, seed=None):
        if seed is not None:
            random.seed(seed)

        # False = не посещена, True = уже в лабиринте
        in_maze = [[False]*width for _ in range(height)]
        # Стены
        right_walls = [[True]*width for _ in range(height)]
        bottom_walls = [[True]*width for _ in range(height)]

        def neighbors(x, y):
            dirs = []
            if x > 0: dirs.append((x-1, y))
            if x < width-1: dirs.append((x+1, y))
            if y > 0: dirs.append((x, y-1))
            if y < height-1: dirs.append((x, y+1))
            return dirs

        # 1. старт
        start_x, start_y = random.randrange(width), random.randrange(height)
        in_maze[start_y][start_x] = True

        # 2. список границ
        frontier = [(nx, ny, start_x, start_y) for (nx, ny) in neighbors(start_x, start_y)]

        while frontier:
            # 3. случайное ребро из границы
            x, y, from_x, from_y = random.choice(frontier)
            frontier.remove((x, y, from_x, from_y))

            if not in_maze[y][x]:
                # добавить в лабиринт
                in_maze[y][x] = True

                # удалить стену между (x,y) и (from_x,from_y)
                if x == from_x:
                    # движение вверх/вниз
                    if y > from_y:
                        bottom_walls[from_y][from_x] = False
                    else:
                        bottom_walls[y][x] = False
                elif y == from_y:
                    # движение влево/вправо
                    if x > from_x:
                        right_walls[from_y][from_x] = False
                    else:
                        right_walls[y][x] = False

                # добавить соседей этой клетки в frontier
                for nx, ny in neighbors(x, y):
                    if not in_maze[ny][nx]:
                        frontier.append((nx, ny, x, y))

        return right_walls, bottom_walls


    def print_maze_ascii(self, width, height, right_walls, bottom_walls):
        print("+" + "---+" * width)
        for y in range(height):
            line = "|"
            for x in range(width):
                line += "   "
                line += "|" if right_walls[y][x] else " "
            print(line)
            line2 = "+"
            for x in range(width):
                line2 += "---+" if bottom_walls[y][x] else "   +"
            print(line2)


class DSU:
        """Disjoint Set Union (Union-Find)"""
        def __init__(self, n):
            self.parent = list(range(n))

        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]

        def union(self, a, b):
            pa, pb = self.find(a), self.find(b)
            if pa == pb:
                return False
            self.parent[pb] = pa
            return True


class KruskalMaze:
    def kruskal_maze(self, width, height, seed=None):
        if seed is not None:
            random.seed(seed)

        n = width * height
        dsu = DSU(n)

        # Инициализация стен
        right_walls = [[True] * width for _ in range(height)]
        bottom_walls = [[True] * width for _ in range(height)]

        # Список всех возможных рёбер
        edges = []
        for y in range(height):
            for x in range(width):
                if x + 1 < width:
                    edges.append(((x, y), (x + 1, y)))  # вправо
                if y + 1 < height:
                    edges.append(((x, y), (x, y + 1)))  # вниз

        random.shuffle(edges)

        # Проходим по рёбрам
        for (x1, y1), (x2, y2) in edges:
            cell1 = y1 * width + x1
            cell2 = y2 * width + x2

            if dsu.union(cell1, cell2):
                # Если клетки были в разных множествах, убираем стену
                if x1 == x2:
                    # вертикальное соединение (вниз)
                    bottom_walls[min(y1, y2)][x1] = False
                else:
                    # горизонтальное соединение (вправо)
                    right_walls[y1][min(x1, x2)] = False

        return right_walls, bottom_walls


    def print_maze_ascii(self, width, height, right_walls, bottom_walls):
        print("+" + "---+" * width)
        for y in range(height):
            # строка с вертикальными стенами
            line = "|"
            for x in range(width):
                line += "   "
                line += "|" if right_walls[y][x] else " "
            print(line)
            # строка с горизонтальными стенами
            line2 = "+"
            for x in range(width):
                line2 += "---+" if bottom_walls[y][x] else "   +"
            print(line2)


if __name__ == "__main__":
    W, H = 16, 16

    right_walls, bottom_walls = EllersMaze().ellers_maze(W, H, seed=42)
    EllersMaze().print_maze_ascii(W, H, right_walls, bottom_walls)

    # right_walls, bottom_walls = WilsonMaze().wilson_maze(W, H, seed=123)
    # WilsonMaze().print_maze_ascii(W, H, right_walls, bottom_walls)

    # right_walls, bottom_walls = PrimMaze().prim_maze(W, H, seed=42)
    # PrimMaze().print_maze_ascii(W, H, right_walls, bottom_walls)

    # right_walls, bottom_walls = KruskalMaze().kruskal_maze(W, H, seed=42)
    # KruskalMaze().print_maze_ascii(W, H, right_walls, bottom_walls)