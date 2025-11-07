import pygame
from src.widgets._base import Widget

class Button(Widget):
    def __init__(self, x, y, img, hover_img, base_w, base_h, scale=1):
        super().__init__(x, y, img, base_w, base_h, scale)
        self.base_hover = hover_img
        self.clicked = False

        # hover cache
        self._hover_cached_size = None
        self._hover_cached_surf = None

    def resize(self, window_size):
        """Resize both base and hover to exactly same size and recalc rect."""
        prev_last = self._last_window_size
        super().resize(window_size)  # prepares _scaled_image and _rect

        # Ensure hover uses exactly same scaled size as base
        scaled_size = self._cached_size
        if self._hover_cached_size != scaled_size:
            # scale hover image
            self._hover_cached_surf = pygame.transform.smoothscale(self.base_hover, scaled_size)
            self._hover_cached_size = scaled_size

        # Recompute rect based on Widget's computed position (already in super)
        # (super().resize computed self._rect already)
        self._last_window_size = window_size

    def draw(self, surface):
        """Draw button using cached base and hover surfaces."""
        window_size = surface.get_size()
        if self._last_window_size != window_size or self._scaled_image is None:
            self.resize(window_size)

        action = False
        pos = pygame.mouse.get_pos()
        if self._rect and self._rect.collidepoint(pos):
            # blit hover (cached)
            surface.blit(self._hover_cached_surf, self._rect)
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                action = True
        else:
            surface.blit(self._scaled_image, self._rect)

        # reset clicked when mouse released
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        return action
