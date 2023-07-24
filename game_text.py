import pygame

class GameText:
    def __init__(self, clock, surface) -> None:
        self.clock = clock
        self.surface = surface
        
    def addText(self, screen, text, position, color=(255,255,255), size=24):
        font = pygame.font.Font(None, size)
        label = font.render(text, True, color)
        self.surface.blit(label, position)