import pygame


class Particle:
    def __init__(self, pos, vel, lifetime):
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.lifetime = lifetime
        self.alive = True

    def update(self):
        self.pos += self.vel
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.alive = False

    def draw(self, surface):
        pass


class PuckGhost(Particle):
    def __init__(self, pos, size, lifetime=20, color=(255, 255, 255)):
        super().__init__(pos, (0, 0), lifetime)

        self.size = size
        self.color = color

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)

        self.max_lifetime = lifetime

    def update(self):
        super().update()

        # fade alpha based on lifetime ratio
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

    def update(self):
        for particle in self.particles:
            particle.update()

        # remove dead particles
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)
