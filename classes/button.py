import pygame as pg
from pygame import Surface, Rect, Color

class Button:

    def __init__(self, pos, size, text, font_size, action = lambda : None):

        self.pos = pos
        self.action = action
        self.up_surface = Surface(size)
        self.down_surface = Surface(size)
        self.size = size
        self.rect = Rect((0, 0), size)
        self.up_color = Color("grey90")
        self.down_color = Color("grey60")
        self.text = text
        self.font_size = font_size

        self.is_up = True

        pg.draw.rect(self.up_surface, self.up_color, self.rect)
        pg.draw.rect(self.down_surface, self.down_color, self.rect)

        font = pg.font.Font(None, font_size)
        self.text_surface = font.render(text, True, Color("black"))
        self.up_surface.blit(
            self.text_surface, 
            (
                self.up_surface.get_width() / 2 - self.text_surface.get_width() / 2, 
                self.up_surface.get_height() / 2 - self.text_surface.get_height() / 2
            )
        )
        self.down_surface.blit(
            self.text_surface, 
            (
                self.up_surface.get_width() / 2 - self.text_surface.get_width() / 2, 
                self.up_surface.get_height() / 2 - self.text_surface.get_height() / 2
            )
        )
