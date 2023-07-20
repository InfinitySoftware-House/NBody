import pygame

class GameText:
    def addText(screen, text, position, color=(255,255,255), size=24):
        font = pygame.font.Font(None, size)
        label = font.render(text, True, color)
        screen.blit(label, position)
        pygame.display.update()