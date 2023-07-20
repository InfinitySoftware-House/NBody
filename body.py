import math
import numpy as cp

def get_star_brightness(mass):
    if 100.0 <= mass <= 250.0:
        return 10   # Light Sky Blue
    elif 250.1 <= mass <= 500.0:
        return 20   # Deep Sky Blue
    elif 500.1 <= mass <= 800.0:
        return 50   # White
    elif 800.1 <= mass <= 1200.0:
        return 100     # Gold
    elif 1200.1 <= mass <= 2500.0:
        return 150     # Orange
    elif 2500.1 <= mass <= 6000.0:
        return 200      # Orange Red
    elif 6000.1 <= mass <= 10000.0:
        return 225     # Firebrick
    elif 10000.1 <= mass <= 1e11:
        return 255      # Dark Red
    else:
        return 255

def get_star_color_by_mass(mass):
    if 100.0 <= mass <= 250.0:
        return (255, 140, 102, get_star_brightness(mass))   # Light Sky Blue
    elif 250.1 <= mass <= 500.0:
        return (255, 218, 185, get_star_brightness(mass))     # Deep Sky Blue
    elif 500.1 <= mass <= 800.0:
        return (255, 247, 239, get_star_brightness(mass))   # White
    elif 800.1 <= mass <= 1200.0:
        return (243, 244, 255, get_star_brightness(mass))     # Gold
    elif 1200.1 <= mass <= 2500.0:
        return (202, 216, 255, get_star_brightness(mass))     # Orange
    elif 2500.1 <= mass <= 6000.0:
        return (170, 191, 255, get_star_brightness(mass))      # Orange Red
    elif 6000.1 <= mass <= 10000.0:
        return (155, 176, 255, get_star_brightness(mass))     # Firebrick
    elif 10000.1 <= mass <= 1e11:
        return (155, 176, 255, get_star_brightness(mass))       # Dark Red
    else:
        return (155, 176, 255, get_star_brightness(mass))


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
    bh_mass = cp.random.uniform(100, 10000, size=(N, 1))

    # Set the masses of the black holes to be very large
    bh_mass *= 1*10**2

    # Add the black holes to the simulation
    pos = cp.vstack((pos, body_pos))
    mass = cp.vstack((mass, bh_mass))
    vel = cp.vstack((vel, cp.zeros((1,3))))
    acc = cp.vstack((acc, cp.zeros((1,3))))

    return pos, mass, vel, acc

def getAcc( pos, mass, G, softening ):
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