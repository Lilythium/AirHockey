import pygame


class Divider(pygame.sprite.Sprite):
    def __init__(self, screen, screen_center):
        super().__init__()
        self.image = pygame.Surface((5, screen.get_height()))
        self.image.fill((200, 5, 5))
        self.rect = self.image.get_rect(center=screen_center)


class Goal(pygame.sprite.Sprite):
    def __init__(self, screen, xPos=0):
        super().__init__()

        width = screen.get_height() // 3.75
        height = screen.get_height() // 3.25

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        color = (130, 200, 255)

        pygame.draw.ellipse(self.image, color, self.image.get_rect())

        self.rect = self.image.get_rect(center=(xPos, screen.get_height() // 2))


class VerticalEdge:
    def __init__(self, screen, screen_center, goal: Goal):
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
