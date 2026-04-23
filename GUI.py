import pygame

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

