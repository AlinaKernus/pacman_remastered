import pygame
import sys
import os

# ----------------------------
# Base Class: Widget
# ----------------------------
class Widget:
    def __init__(self, x, y, img, base_w, base_h, scale=1):
        self.base_x = x
        self.base_y = y
        self.base_img = img.convert_alpha()
        self.base_w = base_w
        self.base_h = base_h
        self.scale = scale

        # Initialize scaled image and rect
        self.image = self.base_img
        self.rect = self.image.get_rect(topleft=(x, y))

    def _auto_resize(self, surface):
        """Automatically rescale and reposition the widget based on current window size."""
        current_w, current_h = surface.get_size()
        scale_factor_w = current_w / self.base_w
        scale_factor_h = current_h / self.base_h
        scale_factor = min(scale_factor_w, scale_factor_h)  # keep proportions

        # Scale image
        width, height = self.base_img.get_size()
        new_size = (int(width * self.scale * scale_factor), int(height * self.scale * scale_factor))
        self.image = pygame.transform.smoothscale(self.base_img, new_size)

        # Recalculate position
        scaled_x = int(self.base_x * scale_factor_w)
        scaled_y = int(self.base_y * scale_factor_h)
        self.rect = self.image.get_rect(topleft=(scaled_x, scaled_y))

    def draw(self, surface):
        """Draw widget and auto-resize before rendering."""
        self._auto_resize(surface)
        surface.blit(self.image, self.rect)


# ----------------------------
# Derived Class: Buttons
# ----------------------------
class Button(Widget):
    def __init__(self, x, y, img, hover_img, base_w, base_h, scale=1):
        super().__init__(x, y, img, base_w, base_h, scale)
        self.base_hover = hover_img.convert_alpha()
        self.hover = self.base_hover
        self.clicked = False

    def draw(self, surface):
        """Draw resizable button with hover and click behavior."""
        # Auto-resize both images
        current_w, current_h = surface.get_size()
        scale_factor_w = current_w / self.base_w
        scale_factor_h = current_h / self.base_h
        scale_factor = min(scale_factor_w, scale_factor_h)

        width, height = self.base_img.get_size()
        new_size = (int(width * self.scale * scale_factor), int(height * self.scale * scale_factor))
        self.image = pygame.transform.smoothscale(self.base_img, new_size)
        self.hover = pygame.transform.smoothscale(self.base_hover, new_size)

        # Position
        scaled_x = int(self.base_x * scale_factor_w)
        scaled_y = int(self.base_y * scale_factor_h)
        self.rect = self.image.get_rect(topleft=(scaled_x, scaled_y))

        # Interaction
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            surface.blit(self.hover, self.rect)
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True
        else:
            surface.blit(self.image, self.rect)

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action

# ----------------------------
# Derived Class: Input Box
# ----------------------------
# class InputBox(Widget):
#     def __init__(self, x, y, w, h, base_w, base_h, font_size=40, text_color=(255, 255, 255),
#                  box_color=(100, 100, 100), active_color=(180, 180, 180), scale=1):
#         """
#         Наследник Widget — текстовое поле для ввода строки
#         :param x, y: базовые координаты
#         :param w, h: базовые размеры поля
#         :param base_w, base_h: базовые размеры экрана
#         :param font_size: базовый размер шрифта
#         """
#         # создаем пустое изображение (фон поля)
#         base_img = pygame.Surface((w, h), pygame.SRCALPHA)
#         base_img.fill((0, 0, 0, 0))  # прозрачный фон
#         super().__init__(x, y, base_img, base_w, base_h, scale)
#
#         self.base_box_w = w
#         self.base_box_h = h
#         self.text_color = text_color
#         self.box_color = box_color
#         self.active_color = active_color
#         self.font_size = font_size
#         self.active = False
#         self.text = ""
#         self.cursor_visible = True
#         self.cursor_timer = 0
#         self.cursor_interval = 500  # мс
#
#     def handle_event(self, event):
#         """Обработка событий ввода"""
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             # Проверяем клик по полю
#             if self.rect.collidepoint(event.pos):
#                 self.active = True
#             else:
#                 self.active = False
#
#         if self.active and event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_RETURN:
#                 print(f"Введено: {self.text}")
#                 self.active = False
#             elif event.key == pygame.K_BACKSPACE:
#                 self.text = self.text[:-1]
#             else:
#                 if len(self.text) < 30:  # ограничение длины
#                     self.text += event.unicode
#
#     def draw(self, surface):
#         """Масштабирует, рисует рамку и текст"""
#         self._auto_resize(surface)
#
#         # Вычисляем текущие масштабы
#         current_w, current_h = surface.get_size()
#         scale_factor_w = current_w / self.base_w
#         scale_factor_h = current_h / self.base_h
#         scale_factor = min(scale_factor_w, scale_factor_h)
#
#         box_w = int(self.base_box_w * scale_factor)
#         box_h = int(self.base_box_h * scale_factor)
#         font_size_scaled = int(self.font_size * scale_factor)
#
#         # Рисуем прямоугольник
#         color = self.active_color if self.active else self.box_color
#         pygame.draw.rect(surface, color, self.rect, border_radius=10)
#
#         # Шрифт и текст
#         font = pygame.font.SysFont(None, font_size_scaled)
#         text_surface = font.render(self.text, True, self.text_color)
#
#         text_rect = text_surface.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
#         surface.blit(text_surface, text_rect)
#
#         # мигающий курсор
#         if self.active:
#             self.cursor_timer += pygame.time.get_ticks() % 1000
#             if (pygame.time.get_ticks() // self.cursor_interval) % 2 == 0:
#                 cursor_x = text_rect.right + 5
#                 cursor_y = self.rect.y + box_h // 4
#                 cursor_h = box_h // 2
#                 pygame.draw.line(surface, self.text_color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)

class Page:
    def __init__(self, image, base_w, base_h, scale=1):
        self.base_img = image.convert_alpha()
        self.base_w = base_w
        self.base_h = base_h
        self.scale = scale

    def draw(self, surface):
        current_w, current_h = surface.get_size()
        image = pygame.transform.smoothscale(self.base_img, (current_w, current_h))
        surface.blit(image, (0, 0))

class Menu(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.title_widget = Widget(39, 220, title_img, BASE_WIDTH, BASE_HEIGHT)
        self.menu_widget = Widget(1020, 129, menu_img, BASE_WIDTH, BASE_HEIGHT)
        self.authors_widget = Widget(65, 960, authors_img, BASE_WIDTH, BASE_HEIGHT)
        self.spl_but = Button(1184, 267, spl_img, spl_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.mpl_but = Button(1184, 406, mpl_img, mpl_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.set_but = Button(1184, 548, set_img, set_hov_img, BASE_WIDTH, BASE_HEIGHT)
        self.quit_but = Button(1184, 687, quit_img, quit_hov_img, BASE_WIDTH, BASE_HEIGHT)

    def run(self, surface):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            self.draw(surface)
            self.title_widget.draw(surface)
            self.menu_widget.draw(surface)
            self.authors_widget.draw(surface)

            if self.spl_but.draw(surface):
                return "single_player"
            if self.mpl_but.draw(surface):
                return "multi_player"
            if self.set_but.draw(surface):
                return "settings"
            if self.quit_but.draw(surface):
                pygame.quit()
                sys.exit()

            pygame.display.flip()
            clock.tick(60)

class Settings(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)
        self.deco1, self.deco2 = Widget(39, 220, deco, BASE_WIDTH, BASE_HEIGHT)
        self.name = Widget(39, 220, name_img, BASE_WIDTH, BASE_HEIGHT)
        self.volume = Widget(39, 220, volume_img, BASE_WIDTH, BASE_HEIGHT)
        self.theme = Widget(39, 220, theme_img, BASE_WIDTH, BASE_HEIGHT)
        # self.col1 = Widget(39, 220, col1_img, BASE_WIDTH, BASE_HEIGHT)
        # self.col2 = Widget(39, 220, col2_img, BASE_WIDTH, BASE_HEIGHT)
        # self.col3 = Widget(39, 220, col3_img, BASE_WIDTH, BASE_HEIGHT)
        # self.col4 = Widget(39, 220, col4_img, BASE_WIDTH, BASE_HEIGHT)
        # self.col5 = Widget(39, 220, col5_img, BASE_WIDTH, BASE_HEIGHT)
        # self.slider = Widget(39, 220, col5_img, BASE_WIDTH, BASE_HEIGHT)

class Singleplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)

class Multiplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)

# ----------------------------
# Game Setup
# ----------------------------
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'

BASE_WIDTH, BASE_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((BASE_WIDTH // 2, BASE_HEIGHT // 2), pygame.RESIZABLE)
pygame.display.set_caption('Pacman Remastered')

# Load background
bg = pygame.image.load('Assets/Bg.png')

#Load images

title_img = pygame.image.load('Assets/Menu/Title.png')
authors_img = pygame.image.load('Assets/Menu/Authors.png')
menu_img = pygame.image.load('Assets/Menu/Menu.png')
spl_img = pygame.image.load('Assets/Menu/Buttons/Spl_img.png')
spl_hov_img = pygame.image.load('Assets/Menu/Buttons/Spl_hov_img.png')
mpl_img = pygame.image.load('Assets/Menu/Buttons/Mpl_img.png')
mpl_hov_img = pygame.image.load('Assets/Menu/Buttons/Mpl_hov_img.png')
set_img = pygame.image.load('Assets/Menu/Buttons/Set_img.png')
set_hov_img = pygame.image.load('Assets/Menu/Buttons/Set_hov_img.png')
quit_img = pygame.image.load('Assets/Menu/Buttons/Quit_img.png')
quit_hov_img = pygame.image.load('Assets/Menu/Buttons/Quit_hov_img.png')

deco = pygame.image.load('Assets/Settings/Deco.png')
name_img = pygame.image.load('Assets/Settings/Name.png')
volume_img = pygame.image.load('Assets/Settings/Volume.png')
theme_img = pygame.image.load('Assets/Settings/Theme.png')


# Create pages
menu_page = Menu(bg, BASE_WIDTH, BASE_HEIGHT)

current_page = "menu"
clock = pygame.time.Clock()
done = False

# ----------------------------
# Main Loop
# ----------------------------
while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill((0, 23, 175))

    if current_page == "menu":
        current_page = menu_page.run(screen)
    elif current_page == "single_player":
        current_page = menu_page.run(screen)
    elif current_page == "multi_player":
        current_page = menu_page.run(screen)
    elif current_page == "settings":
        current_page = menu_page.run(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
