import pygame
from sys import exit
from start_screen import StartScreen
from game import GameScreen

pygame.init()
screen = pygame.display.set_mode((950, 450))
pygame.display.set_caption('Air Hockey')
clock = pygame.time.Clock()
dt = 0.01
current_screen = StartScreen(screen)

while True:
    events = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()
        events.append(event)

    result = current_screen.update(dt, events)
    if result == "game":
        current_screen = GameScreen(screen)
    elif result == "start":
        current_screen = StartScreen(screen)

    current_screen.draw()
    pygame.display.update()
    dt = min(clock.tick(60) / 1500, 0.02)
