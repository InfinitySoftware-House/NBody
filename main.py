import pygame
import pygame_menu
import scipy
import scipy.constants
import simulation as sim
import menu as m

# Sim default parameters
ParticlesCount          = 1000   # Number of bodies
t                       = 0      # current time of the simulation
tEnd                    = 1000.0   # time at which simulation ends
dt                      = 0.01   # timestep
softening               = 1    # softening length
G                       = scipy.constants.G # Newton's Gravitational Constant
moltiplicatore_tempo    = 1*10**9
is_video_enabled        = False

# Callbacks
def on_change_particles_count(value):
   simulation.ParticlesCount = int(value)
   
def on_softening_change(value):
   simulation.softening = float(value)
   
def moltiplicatore_tempo_change(value):
    simulation.moltiplicatore_tempo = value * 1*10**7
    
def toggle_video(value):
    simulation.is_video_enabled = value
    
def on_change_time(value):
    simulation.tEnd = float(value) / 100

# Initialize Pygame
pygame.init()
clock = pygame.time.Clock()

window_size = (1280, 720)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("N-Body Simulation")

simulation = sim.Simulation(window_size=window_size, screen=screen, clock=clock, ParticlesCount=ParticlesCount, t=t, 
                                tEnd=tEnd, dt=dt, softening=softening, G=G, is_video_enabled=is_video_enabled, 
                                moltiplicatore_tempo=moltiplicatore_tempo, on_change_particles_count=on_change_particles_count, 
                                on_softening_change=on_softening_change, toggle_video=toggle_video, moltiplicatore_tempo_change=moltiplicatore_tempo_change, 
                                on_change_time=on_change_time)


menuClass = m.Menu(screen=screen, window_size=window_size, simulation=simulation, ParticlesCount=ParticlesCount, 
                   softening=softening, moltiplicatore_tempo=moltiplicatore_tempo, is_video_enabled=is_video_enabled, 
                   toggle_video=toggle_video, on_softening_change=on_softening_change, on_change_particles_count=on_change_particles_count, 
                   moltiplicatore_tempo_change=moltiplicatore_tempo_change, clock=clock, time=tEnd, on_change_time=on_change_time)

menu = menuClass.get_menu()
menu = menuClass.draw_menu(menu)
menuClass.run_menu(menu)