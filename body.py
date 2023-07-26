import numpy as cp
from numba import jit
import pygame

@jit(fastmath=True)
def generate_gradient(start_color, end_color, num_steps):
    # Calculate the step size for each color channel
    r_step = (end_color[0] - start_color[0]) / (num_steps - 1)
    g_step = (end_color[1] - start_color[1]) / (num_steps - 1)
    b_step = (end_color[2] - start_color[2]) / (num_steps - 1)

    gradient = []
    for i in range(num_steps):
        # Calculate the current color value for each channel
        r = int(start_color[0] + r_step * i)
        g = int(start_color[1] + g_step * i)
        b = int(start_color[2] + b_step * i)

        gradient.append((r, g, b))

    return gradient

start_color = (0, 255, 0)  # Green
end_color = (255, 0, 0)    # Red
num_steps = 15

colors = generate_gradient(start_color, end_color, num_steps)

def normalize_value(value, min_value, max_value):
    return int(120 + (value - min_value) * (255 - 120) / (max_value - min_value))

def get_star_color_by_ke(ke):
    index = min(range(len(colors)), key=lambda i: abs(colors[i][0] - ke))
    return colors[index]

def get_star_color_by_vel(vel):
    vel = cp.sqrt(vel[0]**2 + vel[1]**2 + vel[2]**2)*5
    index = min(range(len(colors)), key=lambda i: abs(colors[i][0] - vel))
    return colors[index]

@jit(fastmath=True)
def get_star_color_by_mass(mass):
    if 0 <= mass <= 50.0:
        return (255, 255, 255, 110)   # Light Sky Blue
    elif 50.1 <= mass <= 100.0:
        return (255, 218, 185, 130)     # Deep Sky Blue
    elif 100.1 <= mass <= 250.0:
        return (255, 247, 239, 150)   # White
    elif 250.1 <= mass <= 500.0:
        return (243, 244, 255, 190)     # Gold
    elif 550.1 <= mass <= 1000.0:
        return (202, 216, 255, 210)     # Orange
    elif 1000.1 <= mass <= 1200.0:
        return (170, 191, 255, 220)      # Orange Red
    elif 1200.1 <= mass <= 1500.0:
        return (155, 176, 255, 240)     # Firebrick
    elif 1500.1 <= mass <= 10000:
        return (155, 176, 255, 255)       # Dark Red
    else:
        return (155, 176, 255, 255)
    
@jit(fastmath=True)
def generate_star_mass(star_count, star_classification_mass, star_classification_fraction):
    mass = cp.array([5.0])
    desired_shape = (star_count, 1)
    for type in star_classification_mass:
        count = star_classification_fraction[type] * star_count
        count = max(count, 1)
        tmp = cp.random.uniform(star_classification_mass[type][0]*1*10**2, star_classification_mass[type][1]*1*10**2, size=(int(count), 1))
        mass = cp.vstack((mass, tmp))
    
    if desired_shape[0] < mass.shape[0]:
        diff = mass.shape[0] - desired_shape[0]
        mass = mass[:len(mass)-diff]
        
    num_elements_to_add = desired_shape[0] - mass.shape[0]
    if num_elements_to_add > 0:
        mass = cp.pad(mass, ((0, num_elements_to_add), (0, 0)), mode='mean')
    mass[0] = mass.mean()
    return mass


@jit(fastmath=True)
def is_particle_outside_box(x, y, xmin, ymin, xmax, ymax):
    """
    Check if the particle's coordinates (x, y) are outside the bounding box.

    Args:
    x, y: The current position coordinates of the particle.
    xmin, ymin: The top-left coordinates of the bounding box.
    xmax, ymax: The bottom-right coordinates of the bounding box.

    Returns:
    True if the particle is outside the bounding box, False otherwise.
    """
    if x < xmin or x > xmax or y < ymin or y > ymax:
        return True
    return False

def addBody(pos, mass, vel, acc, N, body_pos, body_mass_min, body_mass_max):
    """
    Add 3 black holes to the simulation
    pos is a N x 3 matrix of positions
    mass is an N x 1 vector of masses
    N is the number of particles
    """

    # Generate 3 random positions for the black holes
    # bh_pos = cp.random.randn(N,3)
        
    # Generate 3 random masses for the black holes
    bh_mass = cp.random.uniform(body_mass_min, body_mass_max, size=(N, 1))
    body_pos = cp.array([body_pos[0], body_pos[1], 0])
    # Add the black holes to the simulation
    pos = cp.vstack((pos, body_pos))
    mass = cp.vstack((mass, bh_mass))
    vel = cp.vstack((vel, cp.zeros((1,3))))
    acc = cp.vstack((acc, cp.zeros((1,3))))

    return pos, mass, vel, acc

@jit(fastmath=True)
def place_particles_in_circle(ParticlesCount, window_size, start_span):
    center_x, center_y = window_size[0] / 2, window_size[1] / 2
    radius = start_span / 2  # Assuming start_span represents the diameter of the circular area

    # Generate random angles in radians between 0 and 2*pi
    angles = cp.random.uniform(0, 2 * cp.pi, size=ParticlesCount)

    # Generate random radial distances with square root for more uniform particle distribution
    r = cp.sqrt(cp.random.uniform(0, 1, size=ParticlesCount)) * radius

    # Convert polar coordinates to Cartesian coordinates
    x = center_x + r * cp.cos(angles)
    y = center_y + r * cp.sin(angles)

    # Set z-coordinate to 0 (assuming 2D space)
    z = cp.zeros(ParticlesCount)

    # Combine x, y, and z coordinates to get the positions array
    pos = cp.column_stack((x, y, z))

    return pos

@jit(fastmath=True)
def place_particles_in_square(ParticlesCount, window_size, start_span):
    center_x, center_y = window_size[0] / 2, window_size[1] / 2

    # Generate random x and y coordinates within the rectangle boundaries
    x = cp.random.uniform(center_x - start_span / 2, center_x + start_span / 2, size=ParticlesCount)
    y = cp.random.uniform(center_y - (start_span * 0.5) / 2, center_y + (start_span * 0.5) / 2, size=ParticlesCount)

    # Set z-coordinate to 0 (assuming 2D space)
    z = cp.zeros(ParticlesCount)

    # Combine x, y, and z coordinates to get the positions array
    return cp.column_stack((x, y, z))

@jit(fastmath=True)
def is_black_hole(mass):
    """
    Check if the mass is a black hole.

    Args:
    mass: The mass of the particle.

    Returns:
    True if the mass is a black hole, False otherwise.
    """
    if mass >= 1*10**5 and mass <= 1*10**6:
        return True
    return False

def addBlackHoles(pos, mass, vel, acc, N, body_pos):
    """
    Add 3 black holes to the simulation
    pos is a N x 3 matrix of positions
    mass is an N x 1 vector of masses
    N is the number of particles
    """

    # Generate 3 random positions for the black holes
    # bh_pos = cp.random.randn(N,3)
        
    body_pos = cp.array([body_pos[0], body_pos[1], 0])
    # Generate 3 random masses for the black holes
    bh_mass = cp.random.uniform(1*10**4, 1*10**6, size=(N, 1))

    # Add the black holes to the simulation
    pos = cp.vstack((pos, body_pos))
    mass = cp.vstack((mass, bh_mass))
    vel = cp.vstack((vel, cp.zeros((1,3))))
    acc = cp.vstack((acc, cp.zeros((1,3))))

    return pos, mass, vel, acc

@jit(fastmath=True)
def getAcc(pos, mass, G, softening):
    """
    Calculate the acceleration on each particle due to Newton's Law 
    pos  is a N x 3 matrix of positions
    mass is an N x 1 vector of masses
    G is Newton's Gravitational constant
    softening is the softening length
    a is a N x 3 matrix of accelerations
    """
    # positions r = [x,y,z] for all the particles
    x = pos[:,0:1]
    y = pos[:,1:2]
    z = pos[:,2:3]

    # matrix that stores all the pairwise particle separations: r_j - r_i
    dx = x.T - x
    dy = y.T - y
    dz = z.T - z

    # matrix that stores 1/r^3 for all the pairwise particle separations
    inv_r3 = (dx**2 + dy**2 + dz**2 + softening**2)**(-1.5)
    
    ax = G * (dx * inv_r3) @ mass
    ay = G * (dy * inv_r3) @ mass
    az = G * (dz * inv_r3) @ mass

    # pack together the acceleration components
    a = cp.hstack((ax,ay,az))

    return a

@jit(fastmath=True)
def getEnergy( pos, vel, mass, G ):
	"""
	Get kinetic energy (KE) and potential energy (PE) of simulation
	pos is N x 3 matrix of positions
	vel is N x 3 matrix of velocities
	mass is an N x 1 vector of masses
	G is Newton's Gravitational constant
	KE is the kinetic energy of the system
	PE is the potential energy of the system
	"""
	# Kinetic Energy:
	KE = 0.5 * cp.sum(cp.sum( mass * vel**2 ))

	# Potential Energy:

	# positions r = [x,y,z] for all particles
	x = pos[:,0:1]
	y = pos[:,1:2]
	z = pos[:,2:3]

	# matrix that stores all pairwise particle separations: r_j - r_i
	dx = x.T - x
	dy = y.T - y
	dz = z.T - z

	# matrix that stores 1/r for all particle pairwise particle separations 
	inv_r = cp.sqrt(dx**2 + dy**2 + dz**2)
	inv_r[inv_r>0] = 1.0/inv_r[inv_r>0]

	# sum over upper triangle, to count each interaction only once
	PE = G * cp.sum(cp.sum(cp.triu(-(mass*mass.T)*inv_r,1)))
	
	return KE, PE