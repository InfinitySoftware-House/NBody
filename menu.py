import pygame
import pygame_menu

class Menu:
    def __init__(self, screen, window_size, ParticlesCount, softening, moltiplicatore_tempo, is_video_enabled, toggle_video, on_change_particles_count, on_softening_change, moltiplicatore_tempo_change, simulation, clock, time, on_change_time, on_change_start_span):
        self.screen = screen
        self.window_size = window_size
        self.ParticlesCount = ParticlesCount
        self.softening = softening
        self.moltiplicatore_tempo = moltiplicatore_tempo
        self.is_video_enabled = is_video_enabled
        self.toggle_video = toggle_video
        self.on_change_particles_count = on_change_particles_count
        self.on_softening_change = on_softening_change
        self.moltiplicatore_tempo_change = moltiplicatore_tempo_change
        self.simulation = simulation
        self.screen = screen
        self.window_size = window_size
        self.clock = clock
        self.time = time
        self.on_change_time = on_change_time
        self.on_change_start_span = on_change_start_span
        
    def get_menu(self):
        menu = pygame_menu.Menu(
                'N-Body Simulation',
                self.window_size[0],
                self.window_size[1],
                theme=pygame_menu.themes.THEME_DARK)
        return menu

    def draw_menu(self, menu: pygame_menu.Menu):
        menu.add.vertical_margin(10)
        menu.add.button("RUN SIMULATION", self.simulation.run)
        menu.add.vertical_fill()
        menu.add.text_input("Particles Count: ", default=self.ParticlesCount, input_type=pygame_menu.locals.INPUT_INT, onchange=self.on_change_particles_count, font_size=20)
        menu.add.vertical_margin(10)
        menu.add.text_input("Softening: ", default=self.softening, input_type=pygame_menu.locals.INPUT_FLOAT, onchange=self.on_softening_change, font_size=20)
        menu.add.vertical_margin(10)
        menu.add.text_input("Time multiplier: ", default=1, input_type=pygame_menu.locals.INPUT_FLOAT, onchange=self.moltiplicatore_tempo_change, font_size=20)
        menu.add.vertical_margin(10)
        menu.add.text_input("Years: ", default=1000000, input_type=pygame_menu.locals.INPUT_INT, onchange=self.on_change_time, font_size=20)
        menu.add.vertical_margin(10)
        menu.add.text_input("Start span: ", default=10, input_type=pygame_menu.locals.INPUT_INT, onchange=self.on_change_start_span, font_size=20)
        menu.add.vertical_margin(10)
        menu.add.toggle_switch("Record video", self.is_video_enabled, onchange=self.toggle_video, font_size=20)
        menu.add.vertical_fill()
        menu.add.button("QUIT", pygame_menu.events.EXIT)
        menu.add.vertical_margin(10)
        return menu
    
    def run_menu(self, menu):
        while True:
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    exit()
                    
            if menu.is_enabled():
                menu.update(events)
                menu.draw(self.screen)
            self.clock.tick(60)
            pygame.display.flip()
            
    def show_legend_sim(self):
        font = pygame.font.Font(None, 24)
        hide_menu_text = font.render(f"SPACE BAR:     Hide Menu", True, (255, 255, 255))
        time_step_text = font.render(f"ESC:     Go to menu", True, (255, 255, 255))
        black_hole_text = font.render(f"B:      Add Black Hole", True, (255, 255, 255))
        body_text = font.render(f"A:    Add Body", True, (255, 255, 255))
        stop_recording = font.render(f"T:    Stop Recording", True, (255, 255, 255))
        self.screen.blit(hide_menu_text, (10, 60))
        self.screen.blit(time_step_text, (10, 80))
        self.screen.blit(black_hole_text, (10, 100))
        self.screen.blit(body_text, (10, 120))
        self.screen.blit(stop_recording, (10, 140))
        pygame.display.flip()