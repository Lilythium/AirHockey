import os
import random
import sys

import pygame


def resource_path(rel):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


pygame.mixer.init()


class SoundManager:
    def __init__(self):
        self._sfx_volume = 1.0

        self._hit_sounds = [
            pygame.mixer.Sound(resource_path('audio/hitSounds/puckHit_1.wav')),
            pygame.mixer.Sound(resource_path('audio/hitSounds/puckHit_2.wav')),
            pygame.mixer.Sound(resource_path('audio/hitSounds/puckHit_3.wav')),
        ]

        self._game_sounds = {
            "complete": pygame.mixer.Sound(resource_path('audio/gameSounds/game-complete.mp3')),
            "start": pygame.mixer.Sound(resource_path('audio/gameSounds/game-start.mp3')),
            "unfreeze": pygame.mixer.Sound(resource_path('audio/gameSounds/game-unfreeze.mp3')),
            "goal": pygame.mixer.Sound(resource_path('audio/gameSounds/game-goal.mp3')),
        }

        self._apply_volume()

    # Volume control
    @property
    def sfx_volume(self) -> float:
        return self._sfx_volume

    @sfx_volume.setter
    def sfx_volume(self, value: float):
        self._sfx_volume = max(0.0, min(1.0, value))
        self._apply_volume()

    def _apply_volume(self):
        for sound in self._hit_sounds:
            sound.set_volume(self._sfx_volume)
        for sound in self._game_sounds.values():
            sound.set_volume(self._sfx_volume)

    # Playback
    def play_hit(self):
        """Play a random puck-hit sound."""
        random.choice(self._hit_sounds).play()

    def play(self, name: str):
        """Play a game sound by name: 'complete', 'start', 'unfreeze', 'goal'."""
        sound = self._game_sounds.get(name)
        if sound:
            sound.play()
        else:
            print(f"[SoundManager] Unknown sound: '{name}'")


sound_manager = SoundManager()
