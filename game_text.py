import pygame

class GameText:
    def __init__(self, clock) -> None:
        self.clock = clock
        
    def addText(self, screen, text, position, color=(255,255,255), size=24):
        font = pygame.font.Font(None, size)
        label = font.render(text, True, color)
        screen.blit(label, position)
        pygame.display.flip()
        self.clock.tick(60)