from sys import exit
import pygame
import particles
import GameObjects
import RinkObjects

pygame.init()

screen = pygame.display.set_mode((950, 450))
screen_center = (screen.get_width() // 2, screen.get_height() // 2)
pygame.display.set_caption('Air Hockey')
clock = pygame.time.Clock()

ice_color = (200, 230, 255)

# Sprite setup
player = GameObjects.PlayerPaddle((50, 50, 50), (30, screen.get_height() // 2 - 25), screen, screen_center)
pygame.mouse.set_pos((30, screen.get_height() // 2 - 25))
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

divider = RinkObjects.Divider(screen, screen_center)
leftGoal = RinkObjects.Goal(screen)
rightGoal = RinkObjects.Goal(screen, xPos=screen.get_width())
leftEdge = RinkObjects.VerticalEdge(leftGoal, screen, screen_center)
rightEdge = RinkObjects.VerticalEdge(rightGoal, screen, screen_center)
edges = [leftEdge, rightEdge]
rink_objects = pygame.sprite.Group()
rink_objects.add(divider, leftGoal, rightGoal)

particle_manager = particles.ParticleManager()
puck = GameObjects.GamePuck((0, 0, 0), player, particle_manager, edges, screen, screen_center)
game_objects = pygame.sprite.Group()
game_objects.add(player, puck)
player.divider = divider

# game variables
scores = [0, 0]
game_time = 180


# game functions
def trigger_score(player_num):
    scores[player_num] += 1
    # spawn particles here
    # trigger UI update for score display
    print(scores)
    puck.reset()
    player.reset()


while True:
    # inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

    # game logic
    if puck.pos[0] < 0 - puck.radius:
        trigger_score(1)
    elif puck.pos[0] > screen.get_width() + puck.radius:
        trigger_score(0)

    # rendering and updates
    screen.fill(ice_color)

    rink_objects.draw(screen)
    rink_objects.update()

    particle_manager.update()
    particle_manager.draw(screen)

    game_objects.draw(screen)
    game_objects.update()

    pygame.display.update()
    clock.tick(60)
