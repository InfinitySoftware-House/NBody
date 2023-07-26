import numpy as np
import pygame
import body

class Tree():
    cols = 200
    rows = 200
    rects = []
    
    def __init__(self, surface, pos):
        self.surface = surface
        self.pos = pos
        
    def get_square(self, pan_x, pan_y):
        self.rects = []
        width = self.surface.get_width() / self.cols
        heigth = self.surface.get_height() / self.rows
        
        for i in range(self.rows):
            for j in range(self.cols):
                self.rects.append((width * i + pan_x, heigth * j + pan_y, width, heigth))
    
    def get_particles_per_square(self):
        result = {}
        for rect in self.rects:
            for particle in self.pos:
                if not body.is_particle_outside_box(particle[0], particle[1], rect[0], rect[1], rect[2], rect[3]):
                    if rect in result:
                        result[rect] += 1
                    else:
                        result[rect] = 1
        return result
          
    def draw_square(self):
        for i in range(len(self.rects)):
            pygame.draw.rect(self.surface, (255, 255, 255), self.rects[i], 1)