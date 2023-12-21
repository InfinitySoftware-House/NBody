import pygame
import scipy
import scipy.constants
import simulation as sim
import menu as m
from pygame.locals import *

# Sim default parameters
ParticlesCount          = 1000                  # Number of bodies
t                       = 0                     # current time of the simulation
tEnd                    = 1_000_000_000         # time at which simulation ends
dt                      = 0.01                  # timestep
softening               = 20                    # softening length
G                       = scipy.constants.G     # Newton's Gravitational Constant
moltiplicatore_tempo    = 20*10**9
is_video_enabled        = False
is_settings_menu_open   = False
start_shape             = 0

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
    
def on_change_start_span(value):
    simulation.start_span = value
    
def show_settings_menu():
    settingsMenu = menuClass.get_settings_menu()
    menuClass.is_settings_menu_open = True
    menuClass.draw_settings_menu(settingsMenu)
    menuClass.run_settings_menu(settingsMenu)
    
def start_shape_change(value, val2):
    simulation.start_shape = val2

# Initialize Pygame
pygame.init()
pygame.display.set_caption("N-Body Simulation")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

window_size = (1280,720)
flags = DOUBLEBUF | RESIZABLE | HWSURFACE
screen = pygame.display.set_mode(window_size, flags)
infinite_screen = pygame.Surface((4000, 4000))
pygame.display.update()
pygame.event.set_allowed([QUIT, KEYDOWN, MOUSEBUTTONDOWN])

simulation = sim.Simulation(window_size=window_size, screen=screen, clock=clock, ParticlesCount=ParticlesCount, t=t, 
                                tEnd=tEnd, dt=dt, softening=softening, G=G, is_video_enabled=is_video_enabled, 
                                moltiplicatore_tempo=moltiplicatore_tempo, on_change_particles_count=on_change_particles_count, 
                                on_softening_change=on_softening_change, toggle_video=toggle_video, moltiplicatore_tempo_change=moltiplicatore_tempo_change, 
                                on_change_time=on_change_time, on_change_start_span=on_change_start_span, start_span=200,
                                show_settings_menu=show_settings_menu, is_settings_menu_open=is_settings_menu_open, surface=infinite_screen, start_shape=start_shape, start_shape_change=start_shape_change)

menuClass = m.Menu(screen=screen, window_size=window_size, simulation=simulation, ParticlesCount=ParticlesCount, 
                   softening=softening, moltiplicatore_tempo=moltiplicatore_tempo, on_softening_change=on_softening_change, on_change_particles_count=on_change_particles_count, 
                   moltiplicatore_tempo_change=moltiplicatore_tempo_change, clock=clock, time=tEnd, on_change_time=on_change_time, on_change_start_span=on_change_start_span, show_settings_menu=show_settings_menu,
                   is_settings_menu_open=is_settings_menu_open, surface=infinite_screen, start_shape_change=start_shape_change)

menu = menuClass.get_menu()
menu = menuClass.draw_menu(menu)
menuClass.run_menu(menu)