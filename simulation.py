import datetime
import os
import numpy as np
import pygame
import scipy
import body
import simulation_video as sv
import shutil
import pygame_menu
import menu as m
from GameText import GameText as gt

class Simulation:
 
    def __init__(self, window_size, screen, clock, ParticlesCount, t, tEnd, dt, softening, G, is_video_enabled, moltiplicatore_tempo, on_change_particles_count, on_softening_change, moltiplicatore_tempo_change, toggle_video, on_change_time):
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

    def run(self):
        show_legend = True
        add_black_hole_mode = False
        add_body_mode = False    
        
        menuClass = m.Menu(screen=self.screen, window_size=self.window_size, simulation=self, 
                                           ParticlesCount=self.ParticlesCount, softening=self.softening, 
                                           moltiplicatore_tempo=self.moltiplicatore_tempo, is_video_enabled=self.is_video_enabled, 
                                           toggle_video=self.toggle_video, on_softening_change=self.on_softening_change, 
                                           on_change_particles_count=self.on_change_particles_count, 
                                           moltiplicatore_tempo_change=self.moltiplicatore_tempo_change, clock=self.clock, time=self.tEnd, on_change_time=self.on_change_time)
        
        # Generate Initial Conditions
        np.random.seed(17)            # set the random number generator seed

        # Generate random masses
        mass_min = 1.0*10**2
        small_mass_max = 1.0*10**3
        mass_max = 1*10**4
        small_mass = np.random.uniform(mass_min, small_mass_max, size=(int(self.ParticlesCount*0.9), 1))
        mass = np.concatenate((small_mass, np.random.uniform(small_mass_max, mass_max, size=(int(self.ParticlesCount*0.1), 1))), axis=0)

        range_pos = 100
        pos_min = np.array([(self.window_size[0]/2)-range_pos, (self.window_size[1]/2)-range_pos, 0])  # Minimum (x, y, z) coordinates
        pos_max = np.array([(self.window_size[0]/2)+range_pos, (self.window_size[1]/2)+range_pos, 0])  # Maximum (x, y, z) coordinates

        pos = np.random.uniform(pos_min, pos_max, size=(self.ParticlesCount, 3))   # randomly selected positions (2D)
        # pos, mass = body.addBlackHoles(pos, mass, 1, window_size, range_pos)
        # Convert to Center-of-Mass frame
        vel = np.zeros((pos.shape))
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

        # Main simulation loop
        i = 0
        for i in range(Nt):
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
            i += 1
            
            # Event handling (quit the simulation when window is closed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if add_black_hole_mode:
                            pos, mass, vel, acc = body.addBlackHoles(pos, mass, vel, acc, 1, event.pos)
                        elif add_body_mode:
                            pos, mass, vel, acc = body.addBody(pos, mass, vel, acc, 1, event.pos, mass_min, mass_max)
                        self.ParticlesCount = len(pos)
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        menu = menuClass.get_menu()
                        menu = menuClass.draw_menu(menu)
                        menuClass.run_menu(menu)
                        
                    if event.key == pygame.K_SPACE:
                        show_legend = not show_legend
                        
                    if event.key == pygame.K_b:
                        add_black_hole_mode = not add_black_hole_mode
                        add_body_mode = False

                    if event.key == pygame.K_a:
                        add_body_mode = not add_body_mode
                        add_black_hole_mode = False

            self.screen.fill('black')
            
            current_bodies = 0
            for j in range(self.ParticlesCount):
                # Draw particles on the screen
                scaled_pos = (pos[j][0], pos[j][1])
                if not body.is_particle_outside_box(scaled_pos[0], scaled_pos[1], 0, 0, self.window_size[0], self.window_size[1]):
                    circle_radius = 0.8
                    ellipse_rect = pygame.Rect((scaled_pos[0] - circle_radius), 
                                            (scaled_pos[1] - circle_radius), 
                                            (circle_radius * 2), 
                                            (circle_radius * 2))
                    color = body.get_star_color_by_mass(mass[j][0])
                    pygame.draw.ellipse(self.screen, color, ellipse_rect)
                    current_bodies += 1
                    
            # Add a text annotation for the current time step
            font = pygame.font.Font(None, 24)
            time_step_text = font.render(f"Years: {i}/{Nt}", True, (255, 255, 255))
            total_bodies_text = font.render(f"Bodies in view: {current_bodies}", True, (255, 255, 255))
            self.screen.blit(time_step_text, (10, 10))
            self.screen.blit(total_bodies_text, (10, 30))
            
            self.clock.tick(60)
            if self.is_video_enabled:
                video.make_png(screen=self.screen)
                
            if show_legend:
                menuClass.show_legend_sim()
            
            if add_black_hole_mode:
                gt.addText(self.screen, "Click to add a black hole", (10, self.window_size[1] - 40))
            
            if add_body_mode:
                gt.addText(self.screen, "Click to add a body", (10, self.window_size[1] - 40))
            
            pygame.display.update()
            
        # Timeout
        if self.is_video_enabled:
            video.make_mp4()
            shutil.rmtree(videoFolderPath)
        
        menu = menuClass.get_menu()
        menu = menuClass.draw_menu(menu)
        menuClass.run_menu(menu)
        