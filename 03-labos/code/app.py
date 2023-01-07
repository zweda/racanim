import pygame
from pygame.locals import *
from models.player import Player
from models.position import Position

pygame.init()
screen = pygame.display.set_mode((850, 900))
pygame.display.set_caption('2048')
favicon = pygame.image.load('./resources/logo.png')
pygame.display.set_icon(favicon)
font = pygame.font.SysFont('arial.ttf', 50)

player = Player()


def draw():
    pygame.display.set_caption('2048')
    screen.fill((187, 173, 160))
    for i in range(4):
        for j in range(4):
            background_surface = pygame.Surface((200, 200))
            background_surface.fill((205, 193, 180))
            screen.blit(background_surface, (i * 200 + (i + 1) * 10, j * 200 + (j + 1) * 10))

    text = font.render(f"Score: {player.score}", True, (240, 240, 240), (187, 173, 160))
    screen.blit(text, (10, 4 * 200 + 5 * 10 + 5))

    player.move()
    player.draw(screen, font)

    if player.dead:
        surf = pygame.Surface((400, 300))
        surf.fill((104, 91, 91))
        surf_rect = surf.get_rect()
        surf_rect.center = 850 // 2, 850 // 2
        screen.blit(surf, surf_rect)

        sentences = [font.render("Game Over.", True, (240, 240, 240), (104, 91, 91)),
                     font.render("Your score was:", True, (240, 240, 240), (104, 91, 91)),
                     font.render(f"{player.score}", True, (234, 149, 99), (104, 91, 91)),
                     font.render("Press R to retry.", True, (240, 240, 240), (104, 91, 91))]
        for idx, text in enumerate(sentences):
            text_rect = text.get_rect()
            text_rect.center = 850 // 2, 850 // 2 + (idx - 1.5) * 60
            screen.blit(text, text_rect)

    pygame.display.flip()


# game loop
running = True

if __name__ == '__main__':
    while running:
        draw()
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_r and player.dead:
                    player = Player()
                elif event.key != K_r and player.done_moving():
                    if event.key == K_UP:
                        player.move_direction = Position(0, -1)
                    elif event.key == K_DOWN:
                        player.move_direction = Position(0, 1)
                    elif event.key == K_LEFT:
                        player.move_direction = Position(-1, 0)
                    elif event.key == K_RIGHT:
                        player.move_direction = Position(1, 0)
                    player.move_tiles()
