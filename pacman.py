import pygame
import random

# ---------- Алгоритм Эллера ----------
class EllersMaze:
    def ellers_maze(self, width, height, seed=None):
        if seed is not None:
            random.seed(seed)

        next_set_id = 1
        sets = [0] * width
        right_walls = [[True] * width for _ in range(height)]
        bottom_walls = [[True] * width for _ in range(height)]

        for y in range(height):
            for x in range(width):
                if sets[x] == 0:
                    sets[x] = next_set_id
                    next_set_id += 1

            for x in range(width - 1):
                if sets[x] != sets[x + 1]:
                    join = random.choice([True, False])
                    if y == height - 1:
                        join = True
                    if join:
                        right_walls[y][x] = False
                        old = sets[x + 1]
                        new = sets[x]
                        for i in range(width):
                            if sets[i] == old:
                                sets[i] = new

            if y < height - 1:
                set_to_cells = {}
                for x in range(width):
                    set_to_cells.setdefault(sets[x], []).append(x)

                new_sets = [0] * width
                for s, cells in set_to_cells.items():
                    must = random.choice(cells)
                    for x in cells:
                        make_down = random.choice([True, False]) or x == must
                        if make_down:
                            bottom_walls[y][x] = False
                            new_sets[x] = s
                sets = new_sets

        return right_walls, bottom_walls


# ---------- Генерация симметричного лабиринта ----------
def generate_symmetric_maze(width, height, seed=None):
    em = EllersMaze()
    half_width = width // 2
    rw_half, bw_half = em.ellers_maze(half_width, height, seed)

    right_walls = []
    bottom_walls = []

    for y in range(height):
        rw_row = rw_half[y] + list(reversed(rw_half[y]))
        bw_row = bw_half[y] + list(reversed(bw_half[y]))
        right_walls.append(rw_row)
        bottom_walls.append(bw_row)

    return right_walls, bottom_walls



# ---------- Pygame ----------
CELL = 20
WIDTH, HEIGHT = 16, 8
SCREEN_W, SCREEN_H = WIDTH * CELL + 1, HEIGHT * CELL + 1

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Pac-Man Maze (Ellers)")

clock = pygame.time.Clock()

def draw_maze(right_walls, bottom_walls):
    screen.fill((0, 0, 0))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if right_walls[y][x]:
                pygame.draw.line(screen, (0, 0, 255),
                                 (x * CELL + CELL, y * CELL),
                                 (x * CELL + CELL, y * CELL + CELL), 2)
            if bottom_walls[y][x]:
                pygame.draw.line(screen, (0, 0, 255),
                                 (x * CELL, y * CELL + CELL),
                                 (x * CELL + CELL, y * CELL + CELL), 2)

def main():
    rw, bw = generate_symmetric_maze(WIDTH, HEIGHT, seed=42)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_maze(rw, bw)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
