import random

import pygame


class Particle:
    def __init__(self, pos, vel, lifetime):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.lifetime = lifetime
        self.alive = True

    def update(self, dt):
        self.pos += self.vel * dt
        self.lifetime -= dt

        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface):
        pass


class PuckGhost(Particle):
    def __init__(self, pos, size, lifetime=.2, color=(255, 255, 255)):
        super().__init__(pos, (0, 0), lifetime)

        self.size = size
        self.color = color

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)

        self.max_lifetime = lifetime

    def update(self, dt):
        super().update(dt)

        # fade alpha based on lifetime ratio
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        self.image.set_alpha(alpha)

    def draw(self, surface):
        rect = self.image.get_rect(center=self.pos)
        surface.blit(self.image, rect)


class GoalBurst(Particle):
    def __init__(self, pos, screen_center, puck_vel, lifetime=0.4, mode="core"):
        self.mode = mode
        if puck_vel.length_squared() > 0:
            base_dir = (-puck_vel).normalize()
        else:
            base_dir = pygame.math.Vector2(1, 0)

        random_dir = pygame.math.Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        )

        if random_dir.length_squared() > 0:
            random_dir = random_dir.normalize()

        direction_weight = 0.85

        spread_dir = (base_dir * direction_weight + random_dir * (1 - direction_weight))
        if spread_dir.length_squared() > 0:
            spread_dir = spread_dir.normalize()

        puck_speed = puck_vel.length()

        if mode == "core":
            speed = random.uniform(120, 240) + (puck_speed ** 1.2) * 24
            self.dampen = 0.94 + min(puck_speed / 60, 0.04)
            self.radius = random.randint(2, 5)

        else:  # outer burst
            spread_dir = random_dir
            speed = random.uniform(60, 180)
            self.dampen = 0.8
            self.radius = random.randint(6, 14)
            lifetime *= 1.15

        vel = spread_dir * speed
        self.puck_vel = puck_vel

        super().__init__(pos, vel, lifetime)

        self.screen_center = pygame.math.Vector2(screen_center)
        self.color = (255, 215, 0)

        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        if mode == "outer":
            self.image.set_alpha(180)

        self.max_lifetime = lifetime

    def update(self, dt):
        direction = self.screen_center - self.pos

        if self.mode == "core":
            self.vel.x += direction.x * 0.003 * dt
        else:
            self.vel.x += direction.x * 0.0005 * dt
            self.vel.y += random.uniform(-0.03, 0.03) * dt

        if direction.y != 0:
            puck_y_sign = 1 if self.puck_vel.y >= 0 else -1

            if self.mode == "outer":
                self.vel.y += puck_y_sign * 0.08 * dt
            else:
                self.vel.y += puck_y_sign * 0.05 * dt

        self.vel *= self.dampen ** dt

        super().update(dt)

        alpha = int(255 * (self.lifetime / self.max_lifetime))
        self.image.set_alpha(alpha)

    def draw(self, surface):
        rect = self.image.get_rect(center=self.pos)
        surface.blit(self.image, rect)


class ParticleManager:
    def __init__(self):
        self.particles = []

    def add(self, particle):
        self.particles.append(particle)

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)

        # remove dead particles
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)
