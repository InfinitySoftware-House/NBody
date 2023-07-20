import pygame
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
from pygame.locals import *

def setup_opengl(window_size):
    pygame.init()
    display = pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL Particle System")

def create_shader(shader_type, source):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    success = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not success:
        raise RuntimeError(glGetShaderInfoLog(shader))
    return shader

def create_program(vertex_shader_source, fragment_shader_source):
    program = glCreateProgram()
    vertex_shader = create_shader(GL_VERTEX_SHADER, vertex_shader_source)
    fragment_shader = create_shader(GL_FRAGMENT_SHADER, fragment_shader_source)
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    success = glGetProgramiv(program, GL_LINK_STATUS)
    if not success:
        raise RuntimeError(glGetProgramInfoLog(program))
    return program

def draw_particles(vbo_pos, vbo_color, particle_count):
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_pos)
    glVertexPointer(3, GL_FLOAT, 0, None)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_color)
    glColorPointer(3, GL_FLOAT, 0, None)

    glDrawArrays(GL_POINTS, 0, particle_count)

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)

def main():
    window_size = (800, 600)
    setup_opengl(window_size)

    # Create particle data (positions and colors)
    particle_count = 1000
    positions = np.random.uniform(-1.0, 1.0, size=(particle_count, 3))
    colors = np.random.uniform(0.0, 1.0, size=(particle_count, 3))

    # Generate vertex buffer objects (VBO) for positions and colors
    vbo_pos = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_pos)
    glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)

    vbo_color = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_color)
    glBufferData(GL_ARRAY_BUFFER, colors, GL_STATIC_DRAW)

    # Vertex shader to transform positions
    vertex_shader_source = """
        #version 330 core
        layout (location = 0) in vec3 in_position;
        layout (location = 1) in vec3 in_color;
        out vec3 out_color;
        void main()
        {
            gl_Position = vec4(in_position, 1.0);
            out_color = in_color;
        }
    """

    # Fragment shader to handle colors
    fragment_shader_source = """
        #version 330 core
        in vec3 out_color;
        out vec4 frag_color;
        void main()
        {
            frag_color = vec4(out_color, 1.0);
        }
    """

    # Create the shader program
    shader_program = create_program(vertex_shader_source, fragment_shader_source)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Use the shader program
        glUseProgram(shader_program)

        # Draw the particles
        draw_particles(vbo_pos, vbo_color, particle_count)

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
