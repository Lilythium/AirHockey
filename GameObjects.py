import random

import pygame

import particles
from RinkObjects import Goal

pygame.mixer.init()
hit_sounds = [
    pygame.mixer.Sound('audio/hitSounds/puckHit_1.wav'),
    pygame.mixer.Sound('audio/hitSounds/puckHit_2.wav'),
    pygame.mixer.Sound('audio/hitSounds/puckHit_3.wav')
]


class Puck(pygame.sprite.Sprite):
    def __init__(self, color, screen_center, radius=25):
        super().__init__()
        self.screen_center = screen_center
        diameter = radius * 2
        self.radius = radius
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=screen_center)
        self.pos = pygame.math.Vector2(screen_center)
        self.vel = pygame.math.Vector2(0, 0)

    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))


class GamePuck(Puck):
    def __init__(self, color, particle_manager, edge_group, screen, screen_center, friction=0.6,
                 wall_elasticity=0.9,
                 player_elasticity=0.8):
        super().__init__(color, screen_center, 20)
        self.paddles = None
        self.friction = friction
        self.wall_elasticity = wall_elasticity
        self.player_elasticity = player_elasticity
        self.particle_manager = particle_manager

        self.ghost_timer = 0
        self.ghost_interval = 0.001
        self.ghost_speed_threshold = 1500

        self.last_sound_effect_trigger = 0

        self.edges = edge_group
        self.prev_pos = pygame.Vector2(self.pos)

        self.screen = screen

    def update(self, dt):
        self.apply_friction(dt)
        self.prev_pos = pygame.Vector2(self.pos)
        super().update(dt)

        self.handle_wall_collision()
        self.handle_player_collision()

        if self.last_sound_effect_trigger > 0:
            self.last_sound_effect_trigger -= dt

        if self.vel.length() > self.ghost_speed_threshold:
            self.handle_trail_effect(dt)
        else:
            self.ghost_timer = 0

    def reset(self):
        self.vel = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(self.screen_center)
        self.prev_pos = pygame.math.Vector2(self.screen_center)
        self.rect.center = self.screen_center

    def handle_trail_effect(self, dt):
        self.ghost_timer += dt

        if self.ghost_timer >= self.ghost_interval:
            self.ghost_timer = 0

            self.particle_manager.add(
                particles.PuckGhost(
                    pos=self.rect.center,
                    size=self.rect.width,
                    lifetime=0.25
                )
            )

    def apply_friction(self, dt):
        self.vel *= self.friction ** dt

    def produce_collision_sound(self):
        if self.last_sound_effect_trigger <= 0:
            self.last_sound_effect_trigger = 0.1
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
        for edge in self.edges:
            for edgeRect in [edge.topRect, edge.bottomRect]:
                if self.vel.x > 0:
                    boundary_x = edgeRect.left
                else:
                    boundary_x = edgeRect.right

                crossed = (
                        (self.prev_pos.x - boundary_x) * (self.pos.x - boundary_x) <= 0
                )

                if not crossed:
                    continue

                if (not (edgeRect.top <= self.pos.y + self.radius <= edgeRect.bottom) and
                        not (edgeRect.top <= self.pos.y - self.radius <= edgeRect.bottom)):
                    continue

                if self.vel.x > 0:
                    normal = pygame.math.Vector2(-1, 0)
                    self.pos.x = boundary_x - self.radius
                else:
                    normal = pygame.math.Vector2(1, 0)
                    self.pos.x = boundary_x + self.radius

                self.resolve_collision(normal=normal, elasticity=self.wall_elasticity)
                self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Vertical
        if self.pos.y - self.radius < 0:  # Hit Top
            self.produce_collision_sound()
            self.pos.y = self.radius
            self.vel.y *= -self.wall_elasticity
        elif self.pos.y + self.radius > self.screen.get_height():  # Hit Bottom
            self.produce_collision_sound()
            self.pos.y = self.screen.get_height() - self.radius
            self.vel.y *= -self.wall_elasticity

        self.rect.center = self.pos

    def handle_player_collision(self):
        for paddle in self.paddles:
            paddle_center = pygame.math.Vector2(paddle.rect.center)
            puck_center = pygame.math.Vector2(self.rect.center)

            collision_normal = puck_center - paddle_center
            distance = collision_normal.length()

            if distance >= self.radius + paddle.radius:
                continue

            if distance == 0:
                collision_normal = pygame.math.Vector2(1, 0)
                distance = 1

            overlap = self.radius + paddle.radius - distance

            self.resolve_collision(
                normal=collision_normal,
                overlap=overlap,
                other_vel=paddle.vel,
                elasticity=self.player_elasticity
            )
            self.rect.center = (round(self.pos.x), round(self.pos.y))


class Paddle(Puck):
    def __init__(self, color, starting_pos, screen, screen_center, speed=25):
        super().__init__(color, screen_center)
        self.smoothed_dir = None
        self.speed = speed
        self.vel = pygame.math.Vector2(0, 0)
        self.starting_pos = pygame.math.Vector2(starting_pos)
        self.pos = pygame.math.Vector2(starting_pos)
        self.rect.center = starting_pos
        self.divider = None
        self.screen_center = screen_center
        self.screen = screen

    def reset(self):
        self.pos = self.starting_pos
        self.rect.center = self.starting_pos

    def update(self, dt):
        old_pos = pygame.math.Vector2(self.rect.center)
        direction = self.get_direction()

        if direction is None or direction.length_squared() == 0:
            self.vel = pygame.math.Vector2(0, 0)
            return

        dir_normalized = direction.normalize()

        distance_to_target = direction.length()
        movement_step = min(distance_to_target, self.speed * dt)
        movement = dir_normalized * movement_step

        self.rect.centerx += movement.x
        self.rect.centery += movement.y

        self.handle_collision()

        self.vel = (pygame.math.Vector2(self.rect.center) - old_pos) / dt

    def get_direction(self) -> pygame.Vector2:
        return None

    def handle_collision(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen.get_width():
            self.rect.right = self.screen.get_width()
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen.get_height():
            self.rect.bottom = self.screen.get_height()
        self.pos = pygame.math.Vector2(self.rect.center)


class PlayerPaddle(Paddle):
    def __init__(self, color, starting_pos, screen, screen_center, speed=1500):
        super().__init__(color, starting_pos, screen, screen_center, speed)

    def reset(self):
        super().reset()
        pygame.mouse.set_pos(self.starting_pos)

    def get_mouse_target(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        min_x = self.radius
        max_x = self.divider.rect.left - self.radius
        min_y = self.radius
        max_y = self.screen.get_height() - self.radius

        clamped_x = max(min_x, min(mouse_x, max_x))
        clamped_y = max(min_y, min(mouse_y, max_y))

        return pygame.math.Vector2(clamped_x, clamped_y)

    def get_direction(self) -> pygame.Vector2:
        target = self.get_mouse_target()

        direction = target - pygame.math.Vector2(self.rect.center)

        if direction.length_squared() < 4:
            return pygame.math.Vector2(0, 0)
        return direction


class ComputerPaddle(Paddle):
    def __init__(self, color, starting_pos, screen, screen_center, goal: Goal, puck: GamePuck, speed=1500):
        super().__init__(color, starting_pos, screen, screen_center, speed)
        self.goal = goal
        self.puck = puck

        self.reaction_time = 0.15
        self.reaction_timer = 0
        self.cached_target = pygame.Vector2(self.rect.center)
        self.move_vel = pygame.Vector2(0, 0)

    def get_direction(self) -> pygame.Vector2:
        if self.puck.pos.x < self.screen_center[0]:
            target = pygame.Vector2(self.starting_pos)
        else:
            target = self.cached_target

            # --- Overshoot logic ---
            to_target = target - pygame.Vector2(self.rect.center)
            if to_target.length_squared() > 0 and to_target.length() < 150:
                speed_factor = min(self.move_vel.length() / self.speed, 1)
                overshoot_amount = 15 + 25 * speed_factor
                overshoot_dir = to_target.normalize()
                target += overshoot_dir * overshoot_amount
            # -----------------------

        if self.divider:
            min_x = self.divider.rect.right + self.radius
            target.x = max(target.x, min_x)

        direction = target - pygame.Vector2(self.rect.center)

        if direction.length_squared() < 250:
            return pygame.Vector2(0, 0)

        return direction

    def handle_collision(self):
        super().handle_collision()

        if self.divider:
            if self.rect.left < self.divider.rect.right:
                self.rect.left = self.divider.rect.right
                self.pos = pygame.math.Vector2(self.rect.center)

    def update(self, dt):
        if random.random() < dt * 2:
            self.reaction_time = random.uniform(0.1, 0.25)

        self.reaction_timer -= dt

        if self.reaction_timer <= 0:
            self.reaction_timer = self.reaction_time

            prediction_time = 0.2
            puck_pos = self.puck.pos + self.puck.vel * prediction_time
            self.cached_target = pygame.Vector2(puck_pos.x, puck_pos.y)

            error = pygame.Vector2(
                random.uniform(-25, 25),
                random.uniform(-25, 25)
            )
            self.cached_target += error

        old_pos = pygame.math.Vector2(self.rect.center)
        direction = self.get_direction()

        if direction is None or direction.length_squared() == 0:
            self.vel = pygame.math.Vector2(0, 0)
            return

        desired_vel = direction.normalize() * self.speed
        self.move_vel = self.move_vel.lerp(desired_vel, 0.15)
        movement = self.move_vel * dt

        self.rect.centerx += movement.x
        self.rect.centery += movement.y

        self.handle_collision()

        self.vel = (pygame.math.Vector2(self.rect.center) - old_pos) / dt
