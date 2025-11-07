import pygame

class Widget:
    def __init__(self, x, y, img, base_w, base_h, scale=1):
        self.base_x = x
        self.base_y = y
        # img already must be a Surface (loaded via load_image)
        self.base_img = img
        self.base_w = base_w
        self.base_h = base_h
        self.scale = scale

        # cached scaled image & related info
        self._cached_size = None          # (width, height) of scaled image
        self._scaled_image = None         # scaled Surface
        self._rect = None                 # current rect (topleft pos)
        self._last_window_size = None     # (win_w, win_h) used to compute scaling

    def resize(self, window_size):
        """Resize/calc scaled image and rect if window size changed."""
        if self._last_window_size == window_size and self._cached_size is not None:
            return  # no change

        win_w, win_h = window_size
        sfw = win_w / self.base_w
        sfh = win_h / self.base_h
        sf = min(sfw, sfh)

        width, height = self.base_img.get_size()
        new_w = max(1, int(width * self.scale * sf))
        new_h = max(1, int(height * self.scale * sf))
        new_size = (new_w, new_h)

        # scale only if size changed
        if self._cached_size != new_size:
            self._scaled_image = pygame.transform.smoothscale(self.base_img, new_size)
            self._cached_size = new_size

        scaled_x = int(self.base_x * sfw)
        scaled_y = int(self.base_y * sfh)
        self._rect = self._scaled_image.get_rect(topleft=(scaled_x, scaled_y))

        self._last_window_size = window_size

    def draw(self, surface):
        """Draw widget using cached scaled image (resizes if needed)."""
        window_size = surface.get_size()
        if self._last_window_size != window_size or self._scaled_image is None:
            self.resize(window_size)
        surface.blit(self._scaled_image, self._rect)

    @property
    def rect(self):
        return self._rect