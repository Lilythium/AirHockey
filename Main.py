import random
from sys import exit

import pygame

import particles

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((950, 450))
screen_center = (screen.get_width() // 2, screen.get_height() // 2)
pygame.display.set_caption('Air Hockey')
clock = pygame.time.Clock()

ice_color = (200, 230, 255)
hit_sounds = [
    pygame.mixer.Sound('audio/hitSounds/puckHit_1.wav'),
    pygame.mixer.Sound('audio/hitSounds/puckHit_2.wav'),
    pygame.mixer.Sound('audio/hitSounds/puckHit_3.wav')
]


# Game Objects
class Divider(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((5, screen.get_height()))
        self.image.fill((200, 5, 5))
        self.rect = self.image.get_rect(center=screen_center)


class Goal(pygame.sprite.Sprite):
    def __init__(self, xPos=0):
        super().__init__()

        width = screen.get_height() // 3.75
        height = screen.get_height() // 3.25

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        color = (130, 200, 255)

        pygame.draw.ellipse(self.image, color, self.image.get_rect())

        self.rect = self.image.get_rect(center=(xPos, screen.get_height() // 2))


class VerticalEdge:
    def __init__(self, goal: Goal):
        self.goal = goal

        extend = 50
        edge_x = goal.rect.centerx

        if goal.rect.centerx < screen_center[0]:
            # Extend left
            x = edge_x - extend
            width = extend
        else:
            # Extend right
            x = edge_x
            width = extend

        self.topRect = pygame.Rect(
            x,
            0,
            width,
            goal.rect.top
        )

        self.bottomRect = pygame.Rect(
            x,
            goal.rect.bottom,
            width,
            screen.get_height() - goal.rect.bottom
        )


class Puck(pygame.sprite.Sprite):
    def __init__(self, color, radius=25):
        super().__init__()
        diameter = radius * 2
        self.radius = radius
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=screen_center)
        self.pos = pygame.math.Vector2(screen_center)
        self.vel = pygame.math.Vector2(0, 0)

    def update(self):
        self.pos += self.vel
        self.rect.center = (round(self.pos.x), round(self.pos.y))


class GamePuck(Puck):
    def __init__(self, color, player, particle_manager, edge_group, friction=0.995, wall_elasticity=0.9,
                 player_elasticity=0.8):
        super().__init__(color, 20)
        self.player = player
        self.friction = friction
        self.wall_elasticity = wall_elasticity
        self.player_elasticity = player_elasticity
        self.particle_manager = particle_manager

        self.ghost_timer = 0
        self.ghost_interval = 0.33
        self.ghost_speed_threshold = 10

        self.last_sound_effect_trigger = 0

        self.edges = edge_group
        self.prev_pos = pygame.Vector2(self.pos)

    def update(self):
        self.apply_friction()
        self.prev_pos = pygame.Vector2(self.pos)
        super().update()

        self.handle_wall_collision()
        self.handle_player_collision()

        if self.last_sound_effect_trigger > 0:
            self.last_sound_effect_trigger -= 1

        if self.vel.length() > self.ghost_speed_threshold:
            self.handle_trail_effect()
        else:
            self.ghost_timer = 0

    def reset(self):
        self.vel = pygame.math.Vector2(0, 0)
        self.pos = screen_center

    def handle_trail_effect(self):
        self.ghost_timer += 1

        if self.ghost_timer >= self.ghost_interval:
            self.ghost_timer = 0

            self.particle_manager.add(
                particles.PuckGhost(
                    pos=self.rect.center,
                    size=self.rect.width,
                    lifetime=15
                )
            )

    def apply_friction(self):
        self.vel *= self.friction

    def produce_collision_sound(self):
        if self.last_sound_effect_trigger <= 0:
            self.last_sound_effect_trigger += 15
            random.choice(hit_sounds).play()

    def resolve_collision(self, normal, overlap=0, other_vel=pygame.math.Vector2(0, 0), elasticity=1.0):
        # Ensure normal is normalized
        if normal.length() == 0:
            return
        normal = normal.normalize()

        # Separate objects
        if overlap > 0:
            self.pos += normal * overlap
            self.rect.center = self.pos

        # Relative velocity
        rel_vel = self.vel - other_vel
        rel_vel_dot_normal = rel_vel.dot(normal)

        # Only bounce if moving into the surface
        if rel_vel_dot_normal < 0:
            self.produce_collision_sound()
            self.vel -= (1 + elasticity) * rel_vel_dot_normal * normal

    def handle_wall_collision(self):
        """Bounce off-screen edges using center position and radius."""
        for edge in self.edges:
            if self.rect.centery < screen_center[1]:
                edgeRect = edge.topRect
            else:
                edgeRect = edge.bottomRect

            # Determine which vertical boundary we care about
            if self.vel.x > 0:
                boundary_x = edgeRect.left
            else:
                boundary_x = edgeRect.right

            # Check if we crossed the boundary this frame
            crossed = (
                    (self.prev_pos.x - boundary_x) * (self.pos.x - boundary_x) <= 0
            )

            if not crossed:
                continue

            # Check if y is within the vertical span of the edge
            if not (edgeRect.top <= self.pos.y <= edgeRect.bottom):
                continue

            # Collision normal (pure horizontal wall)
            if self.vel.x > 0:
                normal = pygame.math.Vector2(-1, 0)
            else:
                normal = pygame.math.Vector2(1, 0)

            # Snap puck to boundary (prevents sinking)
            if self.vel.x > 0:
                self.pos.x = boundary_x - self.radius
            else:
                self.pos.x = boundary_x + self.radius

            self.resolve_collision(
                normal=normal,
                elasticity=self.wall_elasticity
            )

        # Vertical
        if self.pos.y - self.radius < 0:  # Hit Top
            self.produce_collision_sound()
            self.pos.y = self.radius
            self.vel.y *= -self.wall_elasticity
        elif self.pos.y + self.radius > screen.get_height():  # Hit Bottom
            self.produce_collision_sound()
            self.pos.y = screen.get_height() - self.radius
            self.vel.y *= -self.wall_elasticity

        # Sync the rect
        self.rect.center = self.pos

    def handle_player_collision(self):
        player_center = pygame.math.Vector2(self.player.rect.center)
        puck_center = pygame.math.Vector2(self.rect.center)

        collision_normal = puck_center - player_center
        distance = collision_normal.length()

        if distance >= self.radius + self.player.radius:
            return

        if distance == 0:
            collision_normal = pygame.math.Vector2(1, 0)
            distance = 1

        overlap = self.radius + self.player.radius - distance

        self.resolve_collision(
            normal=collision_normal,
            overlap=overlap,
            other_vel=self.player.vel,
            elasticity=self.player_elasticity
        )


class PlayerPuck(Puck):
    def __init__(self, color, starting_pos, speed=22):
        super().__init__(color)
        self.divider = None
        self.speed = speed
        self.vel = pygame.math.Vector2(0, 0)
        self.starting_pos = starting_pos
        self.pos = self.starting_pos
        self.rect.center = self.starting_pos

    def reset(self):
        self.pos = self.starting_pos
        self.rect.center = self.starting_pos
        pygame.mouse.set_pos(self.starting_pos)

    def update(self):
        old_pos = pygame.math.Vector2(self.rect.center)

        mouse_pos = pygame.mouse.get_pos()
        direction = pygame.math.Vector2(mouse_pos) - pygame.math.Vector2(self.rect.center)
        distance = direction.length()

        if distance != 0:
            direction = direction.normalize()
            movement = direction * min(self.speed, distance)
            self.rect.centerx += movement.x
            self.rect.centery += movement.y

        # Collision with divider
        if self.rect.right > self.divider.rect.left:
            self.rect.right = self.divider.rect.left

        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen.get_width():
            self.rect.right = screen.get_width()
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen.get_height():
            self.rect.bottom = screen.get_height()

        new_pos = pygame.math.Vector2(self.rect.center)
        self.vel = new_pos - old_pos


# Sprite setup
player = PlayerPuck((50, 50, 50), (30, screen.get_height() // 2 - 25))
pygame.mouse.set_pos((30, screen.get_height() // 2 - 25))
pygame.mouse.set_visible(False)

divider = Divider()
leftGoal = Goal()
rightGoal = Goal(xPos=screen.get_width())
leftEdge = VerticalEdge(leftGoal)
rightEdge = VerticalEdge(rightGoal)
edges = [leftEdge, rightEdge]
rink_objects = pygame.sprite.Group()
rink_objects.add(divider, leftGoal, rightGoal)

particle_manager = particles.ParticleManager()
puck = GamePuck((0, 0, 0), player, particle_manager, edges)
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
