import pygame
import sys
from _base import Page, Widget, Button

class Multiplayer(Page):
    def __init__(self, image, base_w, base_h):
        super().__init__(image, base_w, base_h)