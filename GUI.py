import pygame
import math

fonts = [
    'fonts/CursedTimerUlil-Aznm.ttf',
    'fonts/Chewy-Regular.ttf'
]


class Text(pygame.sprite.Sprite):
    def __init__(self, pos, text, fontOption=0, width=None, height=None, color='Black'):
        super().__init__()

        self.pos = pos
        self.text = text
        self.color = color
        self.width = width
        self.height = height

        if height is not None:
            self.font_size = int(height * 0.8)
        else:
            self.font_size = 35

        self.font = pygame.font.Font(fonts[fontOption], self.font_size)

        self.image = None
        self.rect = None

        self.update_text(text)

    def update_text(self, text):
        self.text = text
        self.image = self.font.render(self.text, True, self.color)

        if self.width and self.height:
            self.rect = self.image.get_rect(center=self.pos)
        else:
            self.rect = self.image.get_rect(center=self.pos)


class TextBox(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, text, box_color, text_color, fontOption=0):
        super().__init__()

        self.width = width
        self.height = height
        self.box_color = box_color
        self.text_color = text_color

        self.font_size = int(height * 0.8)
        self.font = pygame.font.Font(fonts[fontOption], self.font_size)

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.set_alpha(235)

        self.rect = self.image.get_rect(center=pos)

        self.update_text(text)

    def update_text(self, text):
        self.image.fill(self.box_color)
        text_surf = self.font.render(text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2 + int(self.height * 0.05)))

        self.image.blit(text_surf, text_rect)


class NotificationText(Text):
    def __init__(self, pos, text, fontOption=0, width=None, height=None, color='Black', duration=2.5):
        super().__init__(pos, text, fontOption, width, height, color)

        self.base_image = self.font.render(self.text, True, self.color)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=self.pos)

        self.max_duration = duration
        self.duration = duration
        self.elapsed = 0

        self.base_font_size = self.font_size
        self.alpha = 255

        self.font_path = fonts[fontOption]
        self.font = pygame.font.Font(self.font_path, self.font_size)

    def update(self, dt):
        self.elapsed += dt
        self.duration = self.max_duration - self.elapsed

        if self.duration <= 0:
            self.kill()
            return

        t = self.elapsed / self.max_duration

        # Scale
        oscillations = 1.5
        amplitude = 0.25
        base_scale = 1.1

        scale = base_scale + amplitude * math.sin(t * oscillations * 2 * math.pi + math.pi / 2)

        new_width = int(self.base_image.get_width() * scale)
        new_height = int(self.base_image.get_height() * scale)

        self.image = pygame.transform.smoothscale(self.base_image, (new_width, new_height))
        # Fade out
        if self.duration <= 0.35:
            fade_t = self.duration / 0.25
            self.alpha = int(255 * fade_t)
        else:
            self.alpha = 255

        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=self.pos)

