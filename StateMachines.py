from statemachine import StateMachine, State

import SoundManager


class GameStateMachine(StateMachine):
    game_active = State("Active", initial=True)
    game_frozen = State("Frozen")
    game_over = State("Game Over")

    freeze = game_active.to(game_frozen)
    unfreeze = game_frozen.to(game_active)

    end_game = game_active.to(game_over) | game_frozen.to(game_over)
    restart = game_over.to(game_active)

    def __init__(self):
        super().__init__()
        self.freeze_timer = 0

    def on_enter_game_frozen(self, duration=1.5):
        # duration in seconds
        self.freeze_timer = duration

    def on_exit_game_frozen(self):
        SoundManager.sound_manager.play("unfreeze")

    def update(self, dt):
        if self.game_frozen.is_active:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.unfreeze()