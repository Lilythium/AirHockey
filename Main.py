import random
from sys import exit

import pygame

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((900, 400))
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
        self.image = pygame.Surface((6, screen.get_height()))
        self.image.fill((200, 5, 5))
        self.rect = self.image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))


class Puck(pygame.sprite.Sprite):
    def __init__(self, color, radius=25):
        super().__init__()
        diameter = radius * 2
        self.radius = radius
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(5, 2)

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos


class GamePuck(Puck):
    def __init__(self, color, player, friction=0.995, wall_elasticity=0.9, player_elasticity=0.8):
        super().__init__(color, 20)
        self.player = player
        self.friction = friction
        self.wall_elasticity = wall_elasticity
        self.player_elasticity = player_elasticity

        self.last_sound_effect_trigger = 0

    def update(self):
        self.apply_friction()
        super().update()

        self.handle_wall_collision()
        self.handle_player_collision()

        if self.last_sound_effect_trigger > 0:
            self.last_sound_effect_trigger -= 1

    def apply_friction(self):
        self.vel *= self.friction

    def produce_collision_sound(self):
        if self.last_sound_effect_trigger <= 0:
            self.last_sound_effect_trigger += 15
            random.choice(hit_sounds).play()


    def handle_wall_collision(self):
        """Bounce off screen edges using center position and radius."""
        # Horizontal
        if self.pos.x - self.radius < 0:  # Hit Left
            self.produce_collision_sound()
            self.pos.x = self.radius
            self.vel.x *= -self.wall_elasticity
        elif self.pos.x + self.radius > screen.get_width():  # Hit Right
            self.produce_collision_sound()
            self.pos.x = screen.get_width() - self.radius
            self.vel.x *= -self.wall_elasticity

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
        """Bounce off the player using pure circle collision."""
        player_center = pygame.math.Vector2(self.player.rect.center)
        puck_center = pygame.math.Vector2(self.rect.center)

        collision_normal = puck_center - player_center
        distance = collision_normal.length()

        # Collision Check
        if distance >= self.radius + self.player.radius:
            return

        # Avoid division by zero
        if distance == 0:
            collision_normal = pygame.math.Vector2(1, 0)
            distance = 1

        collision_normal.normalize_ip()

        # Separate puck from player
        overlap = self.radius + self.player.radius - distance
        if overlap > 0:
            self.pos += collision_normal * overlap
            self.rect.center = self.pos

        rel_vel = self.vel - self.player.vel
        rel_vel_dot_normal = rel_vel.dot(collision_normal)

        if rel_vel_dot_normal < 0:
            self.produce_collision_sound()
            self.vel -= (1 + self.player_elasticity) * rel_vel_dot_normal * collision_normal


class PlayerPuck(Puck):
    def __init__(self, color, speed=20):
        super().__init__(color)
        self.divider = None
        self.speed = speed
        self.vel = pygame.math.Vector2(0, 0)

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
player = PlayerPuck((50, 50, 50))
divider = Divider()
puck = GamePuck((0, 0, 0), player)
game_objects = pygame.sprite.Group()
game_objects.add(Divider(), player, puck)
player.divider = divider

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(ice_color)
    game_objects.draw(screen)
    game_objects.update()
    pygame.display.update()
    clock.tick(60)
