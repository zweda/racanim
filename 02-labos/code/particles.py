import pyglet
import random
from typing import List

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, 'Susatav čestica')
win_icon = pyglet.resource.image('window-icon.png')
window.set_icon(win_icon)

particle_img = pyglet.resource.image('cestica.bmp')
particle_img.anchor_x = particle_img.width // 2
particle_img.anchor_y = particle_img.height // 2

MAX_NUMBER_OF_PARTICLES = 50
PARTICLE_SCALE = 0.15
MAX_PARTICLE_AGE = 100
PARTICLES_ORIGIN_X = WINDOW_WIDTH // 2
PARTICLES_ORIGIN_Y = WINDOW_HEIGHT // 2
SPEED_SCALE = 1
INDICATE_AGE = False

class Particle:
    def __init__(self, sprite: pyglet.sprite.Sprite):
        self.sprite = sprite
        self.age = 0
        self.x_direction = random.randint(-15, 15)
        self.y_direction = random.randint(-15, 15)


batch = pyglet.graphics.Batch()
particles: List[Particle] = []

def add_particle():
    if len(particles) < MAX_NUMBER_OF_PARTICLES:
        particle = pyglet.sprite.Sprite(particle_img, x=PARTICLES_ORIGIN_X, y=PARTICLES_ORIGIN_Y, batch=batch)
        particle.scale = PARTICLE_SCALE
        if INDICATE_AGE:
            particle.color = (0, 255, 100)
        particles.append(Particle(particle))

def calculate_color(particle: Particle):
    color = particle.sprite.color
    red = color[0]
    green = color[1]
    if green == 255:
        red += particle.age // 2
        if red > 255:
            red = 255
    if red == 255:
        green -= particle.age // 2
        if green < 0:
            green = 0

    return red, green, 100

def increase_particle_age():
    global particles
    particles_tmp: List[Particle] = particles
    for particle in particles:
        particle.age += random.randint(0, 5)
        if INDICATE_AGE:
            particle.sprite.color = calculate_color(particle)
        if particle.age > MAX_PARTICLE_AGE:
            particles_tmp.remove(particle)
    particles = particles_tmp


def change_particle_postion():
    for particle in particles:
        particle.sprite.x += particle.x_direction * SPEED_SCALE
        particle.sprite.y += particle.y_direction * SPEED_SCALE

def do_loop(*args):
    add_particle()
    increase_particle_age()
    change_particle_postion()

@window.event
def on_mouse_press(x, y, button, modifiers):
    global PARTICLES_ORIGIN_X, PARTICLES_ORIGIN_Y
    if button == pyglet.window.mouse.LEFT:
        PARTICLES_ORIGIN_X = x
        PARTICLES_ORIGIN_Y = y

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global PARTICLES_ORIGIN_X, PARTICLES_ORIGIN_Y
    if buttons & pyglet.window.mouse.LEFT:
        PARTICLES_ORIGIN_X = x + dx
        PARTICLES_ORIGIN_Y = y + dy

@window.event
def on_key_press(symbol, modifiers):
    global INDICATE_AGE, SPEED_SCALE
    if symbol == pyglet.window.key.SPACE:
        INDICATE_AGE = True
    if symbol == pyglet.window.key.LSHIFT:
        SPEED_SCALE = 2

@window.event
def on_key_release(symbol, modifiers):
    global INDICATE_AGE, SPEED_SCALE
    if symbol == pyglet.window.key.SPACE:
        INDICATE_AGE = False
    if symbol == pyglet.window.key.LSHIFT:
        SPEED_SCALE = 1


@window.event
def on_draw():
    window.clear()
    batch.draw()


if __name__ == '__main__':
    pyglet.clock.schedule_interval(do_loop, 0.05)
    pyglet.app.run()
