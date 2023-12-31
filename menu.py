import pygame
import pygame_menu

class Menu:
    def __init__(self, screen, window_size, ParticlesCount, softening, moltiplicatore_tempo, on_change_particles_count, on_softening_change, moltiplicatore_tempo_change, simulation, clock, time, on_change_time, on_change_start_span, show_settings_menu, is_settings_menu_open, surface, start_shape_change):
        self.screen = screen
        self.window_size = window_size
        self.ParticlesCount = ParticlesCount
        self.softening = softening
        self.moltiplicatore_tempo = moltiplicatore_tempo
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
        self.show_settings_menu = show_settings_menu
        self.is_settings_menu_open = is_settings_menu_open
        self.surface = surface
        self.start_shape_change = start_shape_change
        
    def get_menu(self):
        mytheme = pygame_menu.Theme()
        myimage = pygame_menu.baseimage.BaseImage(
            image_path="./stars_bg.jpg",
            drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL
        )
        mytheme.background_color = myimage

        menu = pygame_menu.Menu(
                'N-Body Simulation',
                columns=2,
                rows=18,
                width=self.window_size[0],
                height=self.window_size[1],
                theme=mytheme)
        return menu
    
    def get_settings_menu(self):
        menu = pygame_menu.Menu(
                'Settings',
                columns=2,
                rows=18,
                width=self.window_size[0],
                height=self.window_size[1],
                theme=pygame_menu.themes.THEME_DARK)
        return menu

    def draw_menu(self, menu: pygame_menu.Menu):
        menu.add.vertical_margin(10)
        menu.add.button("RUN SIMULATION", self.simulation.run_job, font_color=(255,255,255))
        menu.add.vertical_fill()
        menu.add.text_input("Particles Count: ", align=pygame_menu.locals.ALIGN_LEFT, default=self.ParticlesCount, input_type=pygame_menu.locals.INPUT_INT, onchange=self.on_change_particles_count, font_size=20, font_color=(255,255,255))
        menu.add.vertical_margin(10)
        menu.add.text_input("Softening: ", align=pygame_menu.locals.ALIGN_LEFT, default=self.softening, input_type=pygame_menu.locals.INPUT_FLOAT, onchange=self.on_softening_change, font_size=20, font_color=(255,255,255))
        menu.add.vertical_margin(10)
        menu.add.text_input("Time multiplier: ", align=pygame_menu.locals.ALIGN_LEFT, default=self.moltiplicatore_tempo/1*10**-8, input_type=pygame_menu.locals.INPUT_FLOAT, onchange=self.moltiplicatore_tempo_change, font_size=20, font_color=(255,255,255))
        menu.add.vertical_margin(10)
        menu.add.text_input("Years: ", align=pygame_menu.locals.ALIGN_LEFT, default=1_000_000_000, input_type=pygame_menu.locals.INPUT_INT, onchange=self.on_change_time, font_size=20, font_color=(255,255,255))
        menu.add.vertical_margin(10)
        menu.add.text_input("Start span: ", align=pygame_menu.locals.ALIGN_LEFT, default=200, input_type=pygame_menu.locals.INPUT_INT, onchange=self.on_change_start_span, font_size=20, font_color=(255,255,255))
        menu.add.vertical_margin(10)
        menu.add.dropselect("Start shape: ", align=pygame_menu.locals.ALIGN_LEFT, items=[("Circle", 0), ("Square", 1)], onchange=self.start_shape_change, default=0, selection_option_font_size=15, font_size=20, font_color=(255,255,255))
        menu.add.vertical_fill()
        menu.add.label("Made by InfinitySoftware", font_size=15, font_color=(255,255,255))
        menu.add.button("QUIT", pygame_menu.events.EXIT, font_color=(255,255,255))
        menu.add.vertical_margin(40)
        menu.add.horizontal_margin(10)
        menu.center_content()
        return menu
    
    def close_settings_menu(self):
        self.is_settings_menu_open = False
    
    def draw_settings_menu(self, menu: pygame_menu.Menu):
        menu.add.vertical_margin(10)
        menu.add.button("BACK", self.close_settings_menu)
        menu.add.vertical_margin(10)
    
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
            
    def run_settings_menu(self, menu):
        while self.is_settings_menu_open:
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    exit()
                    
            if menu.is_enabled():
                menu.update(events)
                menu.draw(self.screen)
            self.clock.tick(60)
            pygame.display.flip()
    
    def stop_menu(self, menu: pygame_menu.Menu):
        menu.disable()
        self.clock.tick(60)
        pygame.display.flip()
        
    def show_legend_sim(self):
        font = pygame.font.Font(None, 22)
        
        hide_menu_text = font.render("SPACE BAR:     Hide controls", True, (255, 255, 255))
        time_step_text = font.render("ESC:     Go to menu", True, (255, 255, 255))
        black_hole_text = font.render("B:      Add Black Hole", True, (255, 255, 255))
        body_text = font.render("A:    Add Body", True, (255, 255, 255))
        stop_recording = font.render("R:    Start/Stop Recording", True, (255, 255, 255))
        show_ke = font.render("K:   Show Kinetic Energy", True, (255,255,255))
        show_velocity = font.render("V:   Show Velocity", True, (255,255,255))
        
        self.surface.blit(hide_menu_text, (10, 120))
        self.surface.blit(time_step_text, (10, 140))
        self.surface.blit(black_hole_text, (10, 160))
        self.surface.blit(body_text, (10, 180))
        self.surface.blit(stop_recording, (10, 200))
        self.surface.blit(show_ke, (10, 220))
        self.surface.blit(show_velocity, (10, 240))