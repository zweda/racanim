import random
import pygame
from models.position import Position, distance


class Tile(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super(Tile, self).__init__()

        if random.random() < 0.1:
            self.value = 4
        else:
            self.value = 2

        self.value_increased = False
        self.moving = False
        self.death_on_impact = False

        self.position = Position(x, y)
        self.position_to = Position(x, y)

        self.pixel_position = Position(x * 200 + (x + 1) * 10, y * 200 + (y + 1) * 10)
        self.pixel_position_to = Position(x * 200 + (x + 1) * 10, y * 200 + (y + 1) * 10)
        self.surface = pygame.Surface((200, 200))

        self.colour = None
        self.set_colour()

    def set_colour(self):
        if self.value == 2:
            self.colour = (238, 228, 218)
        elif self.value == 4:
            self.colour = (237, 224, 200)
        elif self.value == 8:
            self.colour = (242, 177, 121)
        elif self.value == 16:
            self.colour = (234, 149, 99)
        elif self.value == 32:
            self.colour = (246, 124, 95)
        elif self.value == 64:
            self.colour = (246, 94, 59)
        elif self.value == 128:
            self.colour = (237, 207, 114)
        elif self.value == 256:
            self.colour = (237, 204, 97)
        elif self.value == 512:
            self.colour = (237, 200, 80)
        elif self.value == 1024:
            self.colour = (237, 197, 63)
        elif self.value == 2048:
            self.colour = (237, 197, 1)
        elif self.value == 4096:
            self.colour = (94, 218, 146)

    def draw(self, screen, font):
        if not self.death_on_impact or self.moving:
            self.surface.fill(self.colour)
            screen.blit(self.surface, (self.pixel_position.x, self.pixel_position.y))

            if self.value < 8:
                text_colour = (40, 40, 40)
            else:
                text_colour = (240, 240, 240)

            text = font.render(str(self.value), True, text_colour, self.colour)
            text_rect = text.get_rect()
            text_rect.center = self.pixel_position.x + 100, self.pixel_position.y + 100
            screen.blit(text, text_rect)

    def move_to(self, to: Position):
        self.position_to = Position(to.x, to.y)
        self.pixel_position_to = Position(to.x * 200 + (to.x + 1) * 10,
                                          to.y * 200 + (to.y + 1) * 10)
        self.moving = True

    def move(self, speed: int):
        if self.moving:
            if distance(self.pixel_position, self.pixel_position_to) > speed:
                move_direction = Position(self.position_to.x - self.position.x, self.position_to.y - self.position.y)
                move_direction.normalize()
                move_direction.mult(speed)
                self.pixel_position.add(move_direction)
            else:
                self.moving = False
                self.pixel_position = Position(self.pixel_position_to.x, self.pixel_position_to.y)
                self.position = Position(self.position_to.x, self.position_to.y)
