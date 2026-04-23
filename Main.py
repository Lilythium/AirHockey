import random
from sys import exit

import pygame

import GameObjects
import RinkObjects
import particles
from GUI import TextBox, Text

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
leftEdge = RinkObjects.VerticalEdge(screen, screen_center, leftGoal)
rightEdge = RinkObjects.VerticalEdge(screen, screen_center, rightGoal)
edges = [leftEdge, rightEdge]
rink_objects = pygame.sprite.Group()
rink_objects.add(divider, leftGoal, rightGoal)

particle_manager = particles.ParticleManager()
puck = GameObjects.GamePuck((190, 60, 60), particle_manager, edges, screen, screen_center)
compPlayer = GameObjects.ComputerPaddle((50, 50, 50), (screen.get_width() - 30, screen.get_height() // 2 - 25), screen,
                                        screen_center, rightGoal, puck)

game_objects = pygame.sprite.Group()
game_objects.add(player, compPlayer, puck)
player.divider = divider
compPlayer.divider = divider
puck.paddles = [player, compPlayer]

# game screen GUI

timeDisplay = TextBox(
    pos=(screen_center[0], 30),
    width=170,
    height=60,
    text="88:88",
    box_color='Black',
    text_color='Red',
    fontOption=0
)
leftScore = Text(
    pos=(30, 40),
    width=60,
    height=80,
    text="0",
    fontOption=1
)
rightScore = Text(
    pos=(screen.get_width() - 30, 40),
    width=60,
    height=80,
    text="0",
    fontOption=1
)

gui_objects = pygame.sprite.Group()
gui_objects.add(timeDisplay, leftScore, rightScore)

# game variables
scores = [0, 0]
game_time = 180


# game functions
def trigger_score(player_num):
    scores[player_num] += 1
    # spawn particles here
    spawn_goal_burst(
        pos=puck.rect.center,
        puck_vel=puck.vel,
        count=50
    )
    # trigger UI update for score display
    update_score_display()
    puck.reset()
    player.reset()
    compPlayer.reset()


def update_score_display():
    leftScore.update_text(f"{scores[0]}")
    rightScore.update_text(f"{scores[1]}")


def spawn_goal_burst(pos, puck_vel, count=50):
    for _ in range(count):
        spawn_pos = pygame.math.Vector2(pos) + pygame.math.Vector2(
            random.uniform(-10, 10),
            random.uniform(-6, 6)
        )
        spawn_pos += puck_vel.normalize() * 5
        # particle_manager.add(
        #     particles.GoalBurst(
        #         spawn_pos,
        #         screen_center,
        #         puck_vel=puck_vel,
        #         lifetime=random.randint(20, 35),
        #         mode="core"
        #     )
        # )

        if random.random() < 0.8:
            particle_manager.add(
                particles.GoalBurst(
                    spawn_pos,
                    screen_center,
                    puck_vel=puck_vel,
                    mode="outer"
                )
            )


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

    gui_objects.draw(screen)

    pygame.display.update()
    dt = clock.tick(60) / 1000
