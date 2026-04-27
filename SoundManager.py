import os
import random
import sys

import pygame


def resource_path(rel):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


if not pygame.mixer.get_init():
    pygame.mixer.init()


class SoundManager:
    def __init__(self):
        self._sfx_volume = 1.0
        self._music_volume = 1.0

        self._hit_sounds = [
            s for s in [
                self._load_sound('audio/hitSounds/puckHit_1.wav'),
                self._load_sound('audio/hitSounds/puckHit_2.wav'),
                self._load_sound('audio/hitSounds/puckHit_3.wav'),
            ] if s
        ]

        self._game_sounds = {
            "complete": pygame.mixer.Sound(resource_path('audio/gameSounds/game-complete.mp3')),
            "start": pygame.mixer.Sound(resource_path('audio/gameSounds/game-start.mp3')),
            "unfreeze": pygame.mixer.Sound(resource_path('audio/gameSounds/game-unfreeze.mp3')),
            "goal": pygame.mixer.Sound(resource_path('audio/gameSounds/game-goal.mp3')),
        }

        pygame.mixer.music.load(resource_path('audio/music/Nice Brealk.mp3'))
        pygame.mixer.music.set_volume(1.0)

        self._apply_volume()

    # Volume control
    @property
    def sfx_volume(self) -> float:
        return self._sfx_volume

    @property
    def music_volume(self) -> float:
        return self._music_volume

    @sfx_volume.setter
    def sfx_volume(self, value: float):
        self._sfx_volume = max(0.0, min(1.0, value))
        self._apply_volume()

    def set_music_volume(self, value: float):
        pygame.mixer.music.set_volume(max(0.0, min(1.0, value)))

    def _apply_volume(self):
        for sound in self._hit_sounds:
            sound.set_volume(self._sfx_volume)
        for sound in self._game_sounds.values():
            sound.set_volume(self._sfx_volume)
        pygame.mixer.music.set_volume(self._music_volume)

    def _load_sound(self, path):
        try:
            return pygame.mixer.Sound(resource_path(path))
        except pygame.error as e:
            print(f"[SoundManager] Failed to load {path}: {e}")
            return None

    # Playback
    def play_hit(self):
        if self._hit_sounds:
            random.choice(self._hit_sounds).play()

    def play(self, name: str):
        """Play a game sound by name: 'complete', 'start', 'unfreeze', 'goal'."""
        sound = self._game_sounds.get(name)
        if sound:
            sound.play()
        else:
            print(f"[SoundManager] Unknown sound: '{name}'")

    def play_music(self, loops=-1):
        pygame.mixer.music.play(loops)

    def stop_music(self):
        pygame.mixer.music.stop()


sound_manager = SoundManager()
