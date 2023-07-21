import datetime
import os
import random
import time
import numpy as np
import pygame
import body
import simulation_video as sv
import shutil
import menu as m
from game_text import GameText as gt
import psutil

class Simulation:
    pan_offset_x, pan_offset_y = 0, 0
    pan_velocity_x, pan_velocity_y = 0, 0
    zoom_factor = 1.0
    zoom_increment = 0.1
        
    def __init__(self, window_size, screen, clock, ParticlesCount, t, tEnd, dt, softening, G, is_video_enabled, moltiplicatore_tempo, on_change_particles_count, on_softening_change, moltiplicatore_tempo_change, toggle_video, on_change_time, on_change_start_span, start_span):
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

    def run(self):
        show_legend = True
        add_black_hole_mode = False
        add_body_mode = False 
        scroll_mode = False 
        
        menuClass = m.Menu(screen=self.screen, window_size=self.window_size, simulation=self, 
                                           ParticlesCount=self.ParticlesCount, softening=self.softening, 
                                           moltiplicatore_tempo=self.moltiplicatore_tempo, is_video_enabled=self.is_video_enabled, 
                                           toggle_video=self.toggle_video, on_softening_change=self.on_softening_change, 
                                           on_change_particles_count=self.on_change_particles_count, 
                                           moltiplicatore_tempo_change=self.moltiplicatore_tempo_change, clock=self.clock, time=self.tEnd, 
                                           on_change_time=self.on_change_time, on_change_start_span=self.on_change_start_span)
        
        # Generate Initial Conditions
        np.random.seed(random.randint(0, self.ParticlesCount))            # set the random number generator seed

        # Generate random masses
        mass_min = 1.0*10**2
        small_mass_max = 1.0*10**3
        mass_max = 1*10**4
        small_mass = np.random.uniform(mass_min, small_mass_max, size=(int(self.ParticlesCount*0.8), 1))
        mass = np.concatenate((small_mass, np.random.uniform(small_mass_max, mass_max, size=(int(self.ParticlesCount*0.2), 1))), axis=0)

        pos = body.place_particles_in_circle(self.ParticlesCount, self.window_size, self.start_span)

        # Convert to Center-of-Mass frame
        vel = np.zeros((pos.shape))
        # Video recording settings
        if self.is_video_enabled:
            videoFolderName = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            videoFolderPath = os.path.join("/Users/francesco/Desktop/Progetti/NBody/Videos", videoFolderName)
            os.mkdir(videoFolderPath)

            video = sv.Video(path=videoFolderPath)
            
        # Calculate initial gravitational accelerations
        acc = body.getAcc(pos, mass, self.G, self.softening)
        # Number of timesteps
        Nt = int(np.ceil(self.tEnd/self.dt))

        current_bodies = self.ParticlesCount

        total_time = 0
        iteration_count = 0
        
        # Main simulation loop
        i = 0
        game_text = gt(self.clock)
        font = pygame.font.Font(None, 24)
        pan_speed = 0.1
        while 1:
            if i >= Nt:
                break
            start_time = time.time()
            # (1/2) kick
            vel += acc * self.dt * self.moltiplicatore_tempo
            
            # Drift
            pos += vel * self.dt
            
            # Update accelerations
            acc = body.getAcc(pos, mass, self.G, self.softening)
            
            # (1/2) kick
            vel += acc * self.dt * self.moltiplicatore_tempo
            
            # Update time
            self.t += self.dt
            i += 1 * self.moltiplicatore_tempo/1*10**-8
            
            # Event handling (quit the simulation when window is closed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shutil.rmtree(videoFolderPath)
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if add_black_hole_mode:
                            pos, mass, vel, acc = body.addBlackHoles(pos, mass, vel, acc, 1, event.pos)
                        elif add_body_mode:
                            pos, mass, vel, acc = body.addBody(pos, mass, vel, acc, 1, event.pos, mass_min, mass_max)
                        self.ParticlesCount = len(pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        menu = menuClass.get_menu()
                        menu = menuClass.draw_menu(menu)
                        menuClass.run_menu(menu)
                        shutil.rmtree(videoFolderPath)
                        
                    if event.key == pygame.K_SPACE:
                        show_legend = not show_legend
                        
                    if event.key == pygame.K_b:
                        add_black_hole_mode = not add_black_hole_mode
                        add_body_mode = False

                    if event.key == pygame.K_a:
                        add_body_mode = not add_body_mode
                        add_black_hole_mode = False
                        
                    if event.key == pygame.K_t and self.is_video_enabled:
                        self.is_video_enabled = False
                        video.make_mp4()
                        shutil.rmtree(videoFolderPath)
                        
                    # Zoom
                    if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                        self.zoom_factor += self.zoom_increment
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                        self.zoom_factor -= self.zoom_increment
                        
                    if event.key == pygame.K_s:
                        scroll_mode = not scroll_mode
                        if not scroll_mode:
                            self.pan_offset_x = 0
                            self.pan_offset_y = 0

            mouse_buttons = pygame.mouse.get_pressed()
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Handle panning based on mouse input
            if mouse_buttons[0] and scroll_mode:  # Left mouse button is pressed
                # Calculate pan velocity based on mouse movement
                self.pan_velocity_x = (mouse_x - self.window_size[0] // 2) * pan_speed
                self.pan_velocity_y = (mouse_y - self.window_size[1] // 2) * pan_speed

                # Update the pan offset based on the pan velocity
                self.pan_offset_x += self.pan_velocity_x
                self.pan_offset_y += self.pan_velocity_y
            elif mouse_buttons[1]:
                self.pan_offset_x = 0
                self.pan_offset_y = 0
                              
            self.screen.fill('black')
            
            current_bodies = 0
            circle_radius = 0.5
            ellipse_size = (circle_radius * 2 * self.zoom_factor, circle_radius * 2 * self.zoom_factor)
            
            # Draw particles using the pre-calculated values
            for j in range(self.ParticlesCount):
                if not body.is_particle_outside_box(pos[j][0], pos[j][1], 0, 0, self.window_size[0], self.window_size[1]):
                    
                    ellipse_rects = pygame.Rect(((pos[j][0] - circle_radius + self.pan_offset_x) * self.zoom_factor), 
                                        ((pos[j][1] - circle_radius + self.pan_offset_y) * self.zoom_factor), 
                                        *ellipse_size)
                    
                    color = body.get_star_color_by_mass(mass[j][0])
                    pygame.draw.ellipse(self.screen, color, ellipse_rects)
                    current_bodies += 1
           
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            total_time += elapsed_time
            iteration_count += 1
            
            iter_per_sec = iteration_count / total_time
            
            # Text
            game_text.addText(self.screen, f"Iters/second: {iter_per_sec:.2f}", (10, 50))
            game_text.addText(self.screen, f"Years: {int(i)}/{Nt}", (10, 10))
            game_text.addText(self.screen, f"Bodies in view: {current_bodies}", (10, 30))
            game_text.addText(self.screen, f"RAM used: {psutil.virtual_memory()[3]/1000000000:.2f} GB", (10, self.window_size[1] - 60))
            if scroll_mode:
                game_text.addText(self.screen, "Scroll mode ON", (10, self.window_size[1] - 20))
            
            if add_black_hole_mode:
                game_text.addText(self.screen, "Click to add a black hole", (10, self.window_size[1] - 40))
            
            if add_body_mode:
                game_text.addText(self.screen, "Click to add a body", (10, self.window_size[1] - 40))
           
            if self.is_video_enabled:
                video.make_png(screen=self.screen)
                
            if show_legend:
                menuClass.show_legend_sim(record_enabled=self.is_video_enabled)
            
            self.clock.tick(60)
            pygame.display.flip()
            
        # Timeout
        if self.is_video_enabled:
            video.make_mp4()
            shutil.rmtree(videoFolderPath)
        
        menu = menuClass.get_menu()
        menu = menuClass.draw_menu(menu)
        menuClass.run_menu(menu)
        