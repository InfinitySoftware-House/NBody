import uuid
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.constants

def getAcc( pos, mass, G, softening ):
	"""
    Calculate the acceleration on each particle due to Newton's Law 
	pos  is an N x 3 matrix of positions
	mass is an N x 1 vector of masses
	G is Newton's Gravitational constant
	softening is the softening length
	a is N x 3 matrix of accelerations
	"""
	# positions r = [x,y,z] for all particles
	x = pos[:,0:1]
	y = pos[:,1:2]
	z = pos[:,2:3]

	# matrix that stores all pairwise particle separations: r_j - r_i
	dx = x.T - x
	dy = y.T - y
	dz = z.T - z

	# matrix that stores 1/r^3 for all particle pairwise particle separations 
	inv_r3 = (dx**2 + dy**2 + dz**2 + softening**2)
	inv_r3[inv_r3>0] = inv_r3[inv_r3>0]**(-1.5)

	ax = G * (dx * inv_r3) @ mass
	ay = G * (dy * inv_r3) @ mass
	az = G * (dz * inv_r3) @ mass
	
	# pack together the acceleration components
	a = np.hstack((ax,ay,az))

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
	KE = 0.5 * np.sum(np.sum( mass * vel**2 ))


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
	inv_r = np.sqrt(dx**2 + dy**2 + dz**2)
	inv_r[inv_r>0] = 1.0/inv_r[inv_r>0]

	# sum over upper triangle, to count each interaction only once
	PE = G * np.sum(np.sum(np.triu(-(mass*mass.T)*inv_r,1)))
	
	return KE, PE


""" N-body simulation """

# Simulation parameters
N         = 5000    # Number of particles
t         = 0      # current time of the simulation
tEnd      = 10.0   # time at which simulation ends
dt        = 0.01   # timestep
softening = 0.1    # softening length
G         = scipy.constants.G  # Newton's Gravitational Constant
plotRealTime = True # switch on for plotting as the simulation goes along

# Generate Initial Conditions
np.random.seed(17)            # set the random number generator seed

# mass = 20.0*np.ones((N,1))/N  # total mass of particles is 20
# Generate random masses
mass_min = 100.0
mass_max = 1*10**8
mass = np.random.uniform(mass_min, mass_max, size=(N, 1))

# Normalize masses to sum up to 20.0
total_mass = np.sum(mass)
# mass /= total_mass
# mass *= 20.0
pos  = np.random.randn(N,3)   # randomly selected positions
vel = np.zeros((N, 3))

# Convert to Center-of-Mass frame
vel -= np.mean(mass * vel,0) / np.mean(mass)

# calculate initial gravitational accelerations
acc = getAcc( pos, mass, G, softening )

# calculate initial energy of system
KE, PE  = getEnergy( pos, vel, mass, G )

# number of timesteps
Nt = int(np.ceil(tEnd/dt))

# save energies, particle orbits for plotting trails
pos_save = np.zeros((N,3,Nt+1))
pos_save[:,:,0] = pos
KE_save = np.zeros(Nt+1)
KE_save[0] = KE
PE_save = np.zeros(Nt+1)
PE_save[0] = PE
t_all = np.arange(Nt+1)*dt

# prep figure
# fig = plt.figure(figsize=(14, 10), dpi=80, facecolor="black")
fig = plt.figure(figsize=(14, 10), dpi=80, facecolor="black")
gs = fig.add_gridspec(1, 1)  # A single subplot that spans the entire figure
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('black')
manager = plt.get_current_fig_manager()
manager.full_screen_toggle()
"""
Create Your Own N-body Simulation (With Python)
Philip Mocz (2020) Princeton Univeristy, @PMocz

Simulate orbits of stars interacting due to gravity
Code calculates pairwise forces according to Newton's Law of Gravity
"""
def update_plot(i, ax1, pos_save, pos, vel, t, acc):
    # (1/2) kick
    vel += acc * dt/2.0
    
    # drift
    pos += vel * dt
    
    # update accelerations
    acc = getAcc( pos, mass, G, softening )
    
    # (1/2) kick
    vel += acc * dt/2.0
    
    # update time
    t += dt
    
    # get energy of system
    KE, PE  = getEnergy( pos, vel, mass, G )
    
    # save energies, positions for plotting trail
    pos_save[:,:,i+1] = pos
    KE_save[i+1] = KE
    PE_save[i+1] = PE

    # plot in real time
    if plotRealTime or (i == Nt-1):
        plt.cla()
        xx = pos_save[:,0,max(i-50,0):i+1]
        yy = pos_save[:,1,max(i-50,0):i+1]
        # plt.scatter(xx,yy,s=1,color=[.7,.7,1])
        plt.scatter(pos[:,0],pos[:,1],s=mass[:,0]*5*10**(-10),color='red')
        ax1.set(xlim=(0, 0), ylim=(-1, 1))
        ax1.set_aspect('auto')
        ax1.set_xticks([-2,-1,0,1,2])
        ax1.set_yticks([-2,-1,0,1,2])
        
        # Add a text annotation for the current time step
        ax1.text(-2, 2.0, f"Time step: {i}/{Nt}", fontsize=12, color='white', ha='left', va='top')
        ax1.text(-2, 2.1, f"Total bodies: {N}", fontsize=12, color='white', ha='left', va='top')
        
        plt.pause(0.0001)

animation = FuncAnimation(fig, update_plot, fargs=(ax1, pos_save, pos, vel, t, acc), frames=Nt, interval=50)

# Save the animation as an mp4 file
animation.save(f'nbody_animation_{uuid.uuid4()}.gif', writer='pillow', fps=30)

# plt.show()