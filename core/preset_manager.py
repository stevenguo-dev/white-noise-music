"""
Preset Manager

Saves and loads user sound presets (combinations of active sounds
with their volume levels) as JSON.
"""

import json
import os


class PresetManager:
    """Manages saved sound presets."""

    def __init__(self, presets_file):
        self.presets_file = presets_file
        self.presets = {}
        self._load()

    def _load(self):
        if os.path.exists(self.presets_file):
            try:
                with open(self.presets_file, 'r', encoding='utf-8') as f:
                    self.presets = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.presets = {}

    def _save(self):
        os.makedirs(os.path.dirname(self.presets_file) or '.', exist_ok=True)
        with open(self.presets_file, 'w', encoding='utf-8') as f:
            json.dump(self.presets, f, indent=2)

    def add_preset(self, name, sound_data):
        """Save a preset.  sound_data = {sound_key: volume, ...}"""
        self.presets[name] = sound_data
        self._save()

    def remove_preset(self, name):
        if name in self.presets:
            del self.presets[name]
            self._save()

    def get_preset(self, name):
        return self.presets.get(name)

    def get_all_presets(self):
        return dict(self.presets)

    def get_preset_names(self):
        return list(self.presets.keys())
