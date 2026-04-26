import random
from math import ceil
from GameObjects import hit_sounds
import pygame

import GameObjects
import RinkObjects
import particles
from GUI import TextBox, Text, NotificationText, FlashingText
from StateMachines import GameStateMachine

ice_color = (200, 230, 255)
fonts = ['fonts/CursedTimerUlil-Aznm.ttf', 'fonts/Chewy-Regular.ttf']


class GameScreen:
    def __init__(self, screen):
        self.screen = screen
        self.screen_center = (screen.get_width() // 2, screen.get_height() // 2)

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        # --- Rink ---
        self.divider = RinkObjects.Divider(screen, self.screen_center)
        self.leftGoal = RinkObjects.Goal(screen)
        self.rightGoal = RinkObjects.Goal(screen, xPos=screen.get_width())
        self.leftEdge = RinkObjects.VerticalEdge(screen, self.screen_center, self.leftGoal)
        self.rightEdge = RinkObjects.VerticalEdge(screen, self.screen_center, self.rightGoal)

        self.rink_objects = pygame.sprite.Group()
        self.rink_objects.add(self.divider, self.leftGoal, self.rightGoal)

        # --- Game objects ---
        self.particle_manager = particles.ParticleManager()
        self.puck = GameObjects.GamePuck(
            (190, 60, 60), self.particle_manager,
            [self.leftEdge, self.rightEdge], screen, self.screen_center
        )
        self.player = GameObjects.PlayerPaddle(
            (50, 50, 50), (30, screen.get_height() // 2), screen, self.screen_center
        )
        pygame.mouse.set_pos((30, screen.get_height() // 2))

        self.comp = GameObjects.ComputerPaddle(
            (50, 50, 50), (screen.get_width() - 30, screen.get_height() // 2),
            screen, self.screen_center, self.rightGoal, self.puck, side='right'
        )

        for paddle in (self.player, self.comp):
            paddle.divider = self.divider

        self.game_objects = pygame.sprite.Group(self.player, self.comp, self.puck)
        self.puck.paddles = [self.player, self.comp]

        # --- GUI ---
        self.timeDisplay = TextBox(
            pos=(self.screen_center[0], 30), width=170, height=60,
            text="03:00", box_color='Black', text_color='Red', fontOption=0
        )
        self.leftScore = Text(pos=(30, 40), width=60, height=80, text="0", fontOption=1)
        self.rightScore = Text(pos=(screen.get_width() - 30, 40), width=60, height=80, text="0", fontOption=1)

        # hud_objects drawn during active play; overlay_objects drawn on game over
        self.hud_objects = pygame.sprite.Group(self.timeDisplay, self.leftScore, self.rightScore)
        self.overlay_objects = pygame.sprite.Group()

        # --- State ---
        self.scores = [0, 0]
        self.game_time = 10.0

        self.game_state = GameStateMachine()
        self.game_state.freeze(duration=1)

        self.window_focused = True
        self.focus_resume_timer = 0.0

        self.game_over = False
        self.game_over_elapsed = 0.0
        self.attract_left = None

        self._game_over_font = pygame.font.Font(fonts[1], 42)

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.WINDOWFOCUSLOST:
                self.window_focused = False
            elif event.type == pygame.WINDOWFOCUSGAINED:
                self.window_focused = True
                self.focus_resume_timer = 1.0

            if self.game_over and event.type == pygame.KEYDOWN:
                for sound in hit_sounds:
                    sound.set_volume(1.0)
                return "start"

        # game over runs regardless of focus — attract mode should keep going
        if self.game_over:
            self._update_attract(dt)
        else:
            frozen_by_focus = not self.window_focused or self.focus_resume_timer > 0
            if frozen_by_focus:
                if self.window_focused:
                    self.focus_resume_timer = max(0.0, self.focus_resume_timer - dt)
            else:
                self._update_game(dt)

        self.particle_manager.update(dt)
        self.hud_objects.update(dt)
        self.overlay_objects.update(dt)

        return None

    def draw(self):
        self.screen.fill(ice_color)
        self.rink_objects.draw(self.screen)
        self.particle_manager.draw(self.screen)
        self.game_objects.draw(self.screen)

        if self.game_over:
            self.overlay_objects.draw(self.screen)
        else:
            self.hud_objects.draw(self.screen)

    # Internal helpers

    def _update_game(self, dt):
        self.game_state.update(dt)

        if self.game_state.game_active.is_active:
            # Goal check
            if self.puck.pos.x < -self.puck.radius:
                self._trigger_score(1, dt)
            elif self.puck.pos.x > self.screen.get_width() + self.puck.radius:
                self._trigger_score(0, dt)

            self.game_time -= dt
            self._update_timer(self.game_time)

            if self.game_time <= 0:
                self.game_state.end_game()
                self._enter_game_over(dt)
                return

            self.rink_objects.update(dt)
            self.game_objects.update(dt)

        elif self.game_state.game_frozen.is_active:
            pygame.mouse.set_pos(self.player.rect.center)

    def _update_attract(self, dt):
        if self.puck.pos.x < -self.puck.radius:
            self.scores[1] += 1
            self._update_score_display()
            self._reset_attract()
        elif self.puck.pos.x > self.screen.get_width() + self.puck.radius:
            self.scores[0] += 1
            self._update_score_display()
            self._reset_attract()

        self.rink_objects.update(dt)
        self.game_objects.update(dt)

    def _enter_game_over(self, dt):
        self.game_over = True
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)

        self.attract_left = GameObjects.ComputerPaddle(
            (50, 50, 50), (30, self.screen.get_height() // 2),
            self.screen, self.screen_center,
            self.leftGoal, self.puck, side='left'
        )
        self.attract_left.divider = self.divider

        self.game_objects.remove(self.player)
        self.game_objects.add(self.attract_left)
        self.puck.paddles = [self.attract_left, self.comp]

        self.overlay_objects.add(FlashingText(
            pos=self.screen_center,
            text="Press any key to restart",
            fontOption=1,
            height=60,
            color=(30, 30, 80),
            flash_speed=1.5,
            min_alpha=40,
        ))

        self.puck.vel = pygame.math.Vector2(
            random.choice([-450, 450]), random.uniform(-200, 200)
        )
        for sound in hit_sounds:
            sound.set_volume(0.2)
        self.game_objects.update(dt)

    def _reset_attract(self):
        self.puck.reset()
        self.attract_left.reset()
        self.comp.reset()
        self.puck.vel = pygame.math.Vector2(
            random.choice([-450, 450]), random.uniform(-200, 200)
        )

    def _trigger_score(self, player_num, dt):
        self.scores[player_num] += 1
        self._spawn_goal_burst(self.puck.rect.center, self.puck.vel)
        self._update_score_display()
        self.game_state.freeze(duration=1.5)
        self._spawn_notif(f"Player {player_num + 1} Scored!")
        self.puck.reset()
        self.player.reset()
        self.comp.reset()
        self.game_objects.update(dt)

    def _update_score_display(self):
        self.leftScore.update_text(str(self.scores[0]))
        self.rightScore.update_text(str(self.scores[1]))

    def _update_timer(self, time_remaining):
        t = ceil(time_remaining)
        minutes = min(t // 60, 99)
        seconds = t % 60
        self.timeDisplay.update_text(
            f"{'0' if minutes < 10 else ''}{minutes}:{'0' if seconds < 10 else ''}{seconds}"
        )

    def _spawn_notif(self, text, duration=1.75):
        self.hud_objects.add(NotificationText(
            pos=self.screen_center, text=text, fontOption=1,
            width=self.screen.get_width() // 2, height=80, duration=duration
        ))

    def _spawn_goal_burst(self, pos, puck_vel, count=50):
        for _ in range(count):
            spawn_pos = pygame.math.Vector2(pos) + pygame.math.Vector2(
                random.uniform(-10, 10), random.uniform(-6, 6)
            )
            if puck_vel.length_squared() > 0:
                spawn_pos += puck_vel.normalize() * 5
            if random.random() < 0.8:
                self.particle_manager.add(
                    particles.GoalBurst(spawn_pos, self.screen_center, puck_vel=puck_vel, mode="outer")
                )
