import math
import os
import sys

import pygame


def resource_path(rel):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


fonts = [
    resource_path('fonts/CursedTimerUlil-Aznm.ttf'),
    resource_path('fonts/Chewy-Regular.ttf'),
]

ice_color = (200, 230, 255)


class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.elapsed = 0.0

        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

        title_font = pygame.font.Font(fonts[1], 90)
        prompt_font = pygame.font.Font(fonts[1], 36)

        self.title_surf = title_font.render("Air Hockey", True, (30, 30, 80))
        self.prompt_surf = prompt_font.render("Press any key to start", True, (60, 60, 120))

    def update(self, dt, events):
        self.elapsed += dt
        for event in events:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return "game"
        return None

    def draw(self):
        self.screen.fill(ice_color)
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2

        title_rect = self.title_surf.get_rect(center=(cx, cy - 55))
        self.screen.blit(self.title_surf, title_rect)

        alpha = int(160 + 95 * math.sin(self.elapsed * 3.0))
        prompt = self.prompt_surf.copy()
        prompt.set_alpha(alpha)
        self.screen.blit(prompt, prompt.get_rect(center=(cx, cy + 50)))
