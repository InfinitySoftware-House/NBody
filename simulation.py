import random
import time
import numpy as np
import pygame
import body
import simulation_video as sv
import menu as m
from game_text import GameText as gt
import psutil
from joblib import Parallel, delayed
import numpy as cp
from numba import jit
import multiprocessing 

class Simulation:
    pan_offset_x, pan_offset_y = 0, 0
    pan_velocity_x, pan_velocity_y = 0, 0
    zoom_factor = 1.0
    zoom_increment = 0.1
    start_sim = False
    particles = []
    show_legend = True
    add_black_hole_mode = False
    add_body_mode = False 
    show_ke = False
    show_velocity_color = False
    
    pos = []
    mass = []
    vel = []
    acc = []
    
    star_classification_mass = {
        'O': (16, 50),
        'B': (2.1, 16),
        'A': (1.4, 2.1),
        'F': (1.04, 1.4),
        'G': (0.8, 1.04),
        'K': (0.45, 0.8),
        'M': (0.08, 0.45)
    }

    star_classification_fraction = {
        'O': 0.000030,
        'B': 0.0012,
        'A': 0.0061,
        'F': 0.030,
        'G': 0.076,
        'K': 0.12,
        'M': 0.76
    }
  
    def __init__(self, window_size, screen, clock, ParticlesCount, t, tEnd, dt, softening, G, is_video_enabled, moltiplicatore_tempo, on_change_particles_count, on_softening_change, moltiplicatore_tempo_change, toggle_video, on_change_time, on_change_start_span, start_span, show_settings_menu, is_settings_menu_open, surface, start_shape, start_shape_change):
        self.window_size = window_size
        self.screen = screen
        self.clock = clock 
        self.ParticlesCount = ParticlesCount
        self.t = t
        self.tEnd = tEnd
        self.dt = dt
        self.softening = softening
        self.G = G
        self.is_video_enabled = is_video_enabled
        self.moltiplicatore_tempo = moltiplicatore_tempo
        self.on_change_particles_count = on_change_particles_count
        self.on_softening_change = on_softening_change
        self.moltiplicatore_tempo_change = moltiplicatore_tempo_change
        self.toggle_video = toggle_video
        self.on_change_time = on_change_time
        self.on_change_start_span = on_change_start_span
        self.start_span = start_span
        self.show_settings_menu = show_settings_menu
        self.is_settings_menu_open = is_settings_menu_open
        self.surface = surface
        self.start_shape = start_shape
        self.start_shape_change = start_shape_change
    
    @jit(fastmath=True)
    def get_kinetict_energy(self, mass, vel):
        vel = cp.sqrt(vel[0]**2 + vel[1]**2 + vel[2]**2)*5
        Ke = (1/2)*mass*cp.sqrt(vel)
        return Ke
        
    def handle_events(self, menuClass, video):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.add_black_hole_mode:
                        self.pos, self.mass, self.vel, self.acc = body.addBlackHoles(self.pos, self.mass, self.vel, self.acc, 1, event.pos)
                    elif self.add_body_mode:
                        self.pos, self.mass, self.vel, self.acc = body.addBody(self.pos, self.mass, self.vel, self.acc, 1, event.pos, self.mass.min(), self.mass.max())
                    self.ParticlesCount = len(self.pos)
            elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        menu = menuClass.get_menu()
                        menuClass.ParticlesCount = self.ParticlesCount
                        menuClass.softening = self.softening
                        menuClass.moltiplicatore_tempo = self.moltiplicatore_tempo
                        menuClass.time = self.tEnd
                        menuClass.start_span = self.start_span
                        # Reset self.mass
                        self.mass = np.zeros((self.ParticlesCount, 1))
                        
                        menu = menuClass.draw_menu(menu)
                        menuClass.run_menu(menu)
                        
                    if event.key == pygame.K_SPACE:
                        self.show_legend = not self.show_legend
                        
                    if event.key == pygame.K_b:
                        self.add_black_hole_mode = not self.add_black_hole_mode
                        self.add_body_mode = False

                    if event.key == pygame.K_a:
                        self.add_body_mode = not self.add_body_mode
                        self.add_black_hole_mode = False
                        
                    if event.key == pygame.K_r:
                        self.is_video_enabled = not self.is_video_enabled
                        if not self.is_video_enabled:
                            video.make_mp4()
                        
                    # Zoom
                    if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                        self.zoom_factor += self.zoom_increment
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                        self.zoom_factor -= self.zoom_increment
                    
                    if event.key == pygame.K_k:
                        self.show_ke = not self.show_ke
                        self.show_velocity_color = False
                        
                    if event.key == pygame.K_v:
                        self.show_velocity_color = not self.show_velocity_color
                        self.show_ke = False
                        
        keyboard_buttons = pygame.key.get_pressed()
    
        if keyboard_buttons[pygame.K_KP_ENTER]:
            self.start_sim = True
        if keyboard_buttons[pygame.K_LEFT]:
            self.pan_offset_x -= 5
        if keyboard_buttons[pygame.K_RIGHT]:
            self.pan_offset_x += 5
        if keyboard_buttons[pygame.K_UP]:
            self.pan_offset_y -= 5
        if keyboard_buttons[pygame.K_DOWN]:
            self.pan_offset_y += 5
        if keyboard_buttons[pygame.K_KP_0]:
            self.pan_offset_x = 0
            self.pan_offset_y = 0
            self.zoom_factor = 1
                    
                    
    def run(self):
        menuClass = m.Menu(screen=self.screen, window_size=self.window_size, simulation=self, 
                                           ParticlesCount=self.ParticlesCount, softening=self.softening, 
                                           moltiplicatore_tempo=self.moltiplicatore_tempo, on_softening_change=self.on_softening_change, 
                                           on_change_particles_count=self.on_change_particles_count, 
                                           moltiplicatore_tempo_change=self.moltiplicatore_tempo_change, clock=self.clock, time=self.tEnd, 
                                           on_change_time=self.on_change_time, on_change_start_span=self.on_change_start_span,
                                           show_settings_menu=self.show_settings_menu, is_settings_menu_open=self.is_settings_menu_open, surface=self.surface, start_shape_change=self.start_shape_change)
        # Generate Initial Conditions
        np.random.seed(random.randint(0, self.ParticlesCount))            # set the random number generator seed

        self.mass = body.generate_star_mass(self.ParticlesCount, self.star_classification_mass, self.star_classification_fraction)

        if self.start_shape == 0:
            self.pos = body.place_particles_in_circle(self.ParticlesCount, self.window_size, self.start_span)
        elif self.start_shape == 1:
            self.pos = body.place_particles_in_square(self.ParticlesCount, self.window_size, self.start_span)
        # Convert to Center-of-Mass frame
        self.vel = np.zeros((self.pos.shape))
        # Video recording settings
        video = sv.Video()
            
        # var = Tree(self.surface, self.pos)
        
        # Calculate initial gravitational accelerations
        self.acc = body.getAcc(self.pos, self.mass, self.G, self.softening)
        # Number of timesteps
        Nt = int(np.ceil(self.tEnd/self.dt))
        current_bodies = self.ParticlesCount

        total_time = 0
        iteration_count = 0
        
        # Main simulation loop
        i = 0
        game_text = gt(self.clock, surface=self.surface)
        
        while 1:
            iter_per_sec = 0
            if i >= Nt:
                break
            start_time = time.time()
            
            # (1/2) kick
            self.vel += self.acc * self.dt * self.moltiplicatore_tempo
            
            # Drift
            self.pos += self.vel * self.dt
            
            # Update accelerations
            self.acc = body.getAcc(self.pos, self.mass, self.G, self.softening)
            
            # (1/2) kick
            self.vel += self.acc * self.dt * self.moltiplicatore_tempo
            
            # Update time
            self.t += self.dt
            i += self.moltiplicatore_tempo/20*10**-8
            
            # Event handling (quit the simulation when window is closed)
            self.handle_events(menuClass, video)

            start_time = time.time()
            
            # Update time
            self.t += self.dt
            i += 1 * self.moltiplicatore_tempo/1*10**-8

            self.screen.fill('black')
            self.surface.fill("black")
            
            current_bodies = 0
            circle_radius = 0.8
            if self.ParticlesCount in range(0, 100):
                circle_radius = 2.5
                
            # Draw particles using the pre-calculated values
            for j in range(self.ParticlesCount):
                multiplier_size = (self.mass[j][0] - self.mass.min())/(self.mass.max()-self.mass.min()) * 2
                ellipse_size = ((circle_radius * 2) + multiplier_size, (circle_radius * 2) + multiplier_size)
                ellipse_rects = pygame.Rect(((self.pos[j][0] - circle_radius + self.pan_offset_x) * self.zoom_factor), 
                                    ((self.pos[j][1] - circle_radius + self.pan_offset_y) * self.zoom_factor), 
                                    *ellipse_size)
                
                if body.is_black_hole(self.mass[j][0]):
                    color = (255, 255, 255)
                    pygame.draw.circle(self.surface, color, (self.pos[j][0], self.pos[j][1]), circle_radius * 3)
                else:
                    ellipse_surface = pygame.Surface((ellipse_size[0], ellipse_size[1]), pygame.SRCALPHA)
                   
                    if self.show_ke:
                        Ke = self.get_kinetict_energy(self.mass[j][0], self.vel[j])
                        color = body.get_star_color_by_ke(Ke)
                    elif self.show_velocity_color:
                        color = body.get_star_color_by_vel(self.vel[j])
                    else:
                        color = body.get_star_color_by_mass(self.mass[j][0])
                    
                    ellipse_surface.fill(color) 
                    self.surface.blit(ellipse_surface, ellipse_rects)
                
                current_bodies += 1
           
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            total_time += elapsed_time
            iteration_count += 1
            
            iter_per_sec = iteration_count / total_time
            
            # Text
            game_text.addText(self.surface, f"Year: {int(i)}", (10, 10))
            game_text.addText(self.surface, f"Stars: {current_bodies}", (10, 30))
            
            if not self.is_video_enabled:
                game_text.addText(self.surface, f"Iters/second: {iter_per_sec:.2f}", (10, 50))
                game_text.addText(self.surface, f"RAM used: {psutil.virtual_memory()[3]/1000000000:.2f} GB", (10, self.window_size[1] - 60))
                
                if self.add_black_hole_mode:
                    game_text.addText(self.surface, "Click to add a black hole", (10, self.window_size[1] - 40))
                
                if self.add_body_mode:
                    game_text.addText(self.surface, "Click to add a body", (10, self.window_size[1] - 40))
                    
                if self.show_legend:
                    menuClass.show_legend_sim()
                    
            if self.show_ke:
                game_text.addText(self.surface, "Kinetict Energy", (self.window_size[0] - 140, 10))
            elif self.show_velocity_color:
                game_text.addText(self.surface, "Velocity", (self.window_size[0] - 100, 10))
             
            if self.is_video_enabled:
                pygame.display.set_caption("N-Body Simulation - Recording")
            else:
                pygame.display.set_caption("N-Body Simulation")
            
            self.clock.tick(60)

            self.screen.blit(self.surface, (0, 0))        
                
            pygame.display.update()
            
            if self.is_video_enabled:
                video.add_frame(self.screen)
            
        # Timeout
        if self.is_video_enabled:
            video.make_mp4()
        
        menu = menuClass.get_menu()
        menu = menuClass.draw_menu(menu)
        menuClass.run_menu(menu)
    
    def run_job(self):
        Parallel(n_jobs=12)(delayed(self.run()))