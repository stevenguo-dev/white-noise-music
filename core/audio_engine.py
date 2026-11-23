"""
Audio Engine

Manages multiple simultaneous sound channels with individual
volume controls and a master volume.
"""

import os
from kivy.core.audio import SoundLoader


class AudioChannel:
    """A single audio channel with play/stop and volume control."""

    def __init__(self, filepath, name):
        self.filepath = filepath
        self.name = name
        self.sound = SoundLoader.load(filepath)
        self._volume = 0.5
        self._is_playing = False
        if self.sound:
            self.sound.loop = True
            self.sound.volume = self._volume

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = max(0.0, min(1.0, value))
        if self.sound:
            self.sound.volume = self._volume * AudioEngine.master_volume

    @property
    def is_playing(self):
        return self._is_playing

    def play(self):
        if self.sound:
            self.sound.play()
            self._is_playing = True

    def stop(self):
        if self.sound:
            self.sound.stop()
            self._is_playing = False

    def toggle(self):
        if self._is_playing:
            self.stop()
        else:
            self.play()

    def update_master_volume(self, master):
        if self.sound:
            self.sound.volume = self._volume * master


class AudioEngine:
    """Manages all audio channels with a master volume."""

    master_volume = 1.0

    def __init__(self, sounds_dir):
        self.sounds_dir = sounds_dir
        self.channels = {}

    def load_sounds(self):
        """Load all .wav files from the sounds directory."""
        if not os.path.isdir(self.sounds_dir):
            return
        for fname in sorted(os.listdir(self.sounds_dir)):
            if fname.lower().endswith('.wav'):
                key = fname[:-4]
                path = os.path.join(self.sounds_dir, fname)
                self.channels[key] = AudioChannel(path, key)

    def play(self, name):
        if name in self.channels:
            self.channels[name].play()

    def stop(self, name):
        if name in self.channels:
            self.channels[name].stop()

    def toggle(self, name):
        if name in self.channels:
            self.channels[name].toggle()
            return self.channels[name].is_playing
        return False

    def set_volume(self, name, volume):
        if name in self.channels:
            self.channels[name].volume = volume

    def set_master_volume(self, volume):
        AudioEngine.master_volume = max(0.0, min(1.0, volume))
        for ch in self.channels.values():
            ch.update_master_volume(AudioEngine.master_volume)

    def stop_all(self):
        for ch in self.channels.values():
            ch.stop()

    def get_active_sounds(self):
        """Return {name: volume} for all currently playing sounds."""
        return {
            name: ch.volume
            for name, ch in self.channels.items()
            if ch.is_playing
        }

    def load_preset(self, preset_data):
        """Stop all, then play sounds from preset at saved volumes."""
        self.stop_all()
        for name, volume in preset_data.items():
            if name in self.channels:
                self.channels[name].volume = volume
                self.channels[name].play()
