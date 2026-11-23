"""
Sleep Music App
───────────────
A soothing ambient-sound mixer for better sleep.

Features
  - 11 procedurally generated ambient sounds
  - Individual volume sliders per sound
  - Layer multiple sounds simultaneously
  - Master volume control
  - Sleep timer (auto-stop after set duration)
  - Save / load favourite presets
  - Dark, sleep-friendly UI

Usage
  python main.py
"""

import os
import sys
import threading

# ── Kivy configuration (must happen before any kivy import) ────────
os.environ.setdefault('KIVY_LOG_LEVEL', 'warning')

from kivy.config import Config                          # noqa: E402
Config.set('graphics', 'width', '420')
Config.set('graphics', 'height', '750')
Config.set('graphics', 'resizable', 'True')

from kivy.app import App                                # noqa: E402
from kivy.core.window import Window                     # noqa: E402
from kivy.uix.boxlayout import BoxLayout                # noqa: E402
from kivy.uix.gridlayout import GridLayout              # noqa: E402
from kivy.uix.scrollview import ScrollView              # noqa: E402
from kivy.uix.label import Label                        # noqa: E402
from kivy.uix.button import Button                      # noqa: E402
from kivy.uix.popup import Popup                        # noqa: E402
from kivy.uix.textinput import TextInput                # noqa: E402
from kivy.properties import (StringProperty,             # noqa: E402
                              NumericProperty,
                              BooleanProperty,
                              ListProperty)
from kivy.clock import Clock                             # noqa: E402
from kivy.metrics import dp, sp                          # noqa: E402
from kivy.lang import Builder                            # noqa: E402

from core.sound_generator import SoundGenerator          # noqa: E402
from core.audio_engine import AudioEngine                # noqa: E402
from core.timer_manager import TimerManager              # noqa: E402
from core.preset_manager import PresetManager            # noqa: E402

# ── Paths ──────────────────────────────────────────────────────────
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(APP_DIR, 'generated_sounds')
PRESETS_FILE = os.path.join(APP_DIR, 'user_data', 'presets.json')

# ── Sound catalogue (order shown in the UI) ────────────────────────
SOUND_CATALOGUE = [
    {'key': 'rain',        'icon': 'Rain',   'name': 'Rain',        'color': [0.18, 0.25, 0.42, 1]},
    {'key': 'ocean',       'icon': 'Ocean',  'name': 'Ocean Waves', 'color': [0.12, 0.24, 0.40, 1]},
    {'key': 'forest',      'icon': 'Forest', 'name': 'Forest',      'color': [0.12, 0.32, 0.18, 1]},
    {'key': 'wind',        'icon': 'Wind',   'name': 'Wind',        'color': [0.24, 0.28, 0.38, 1]},
    {'key': 'thunder',     'icon': 'Storm',  'name': 'Thunder',     'color': [0.22, 0.18, 0.32, 1]},
    {'key': 'stream',      'icon': 'Creek',  'name': 'Stream',      'color': [0.14, 0.30, 0.32, 1]},
    {'key': 'campfire',    'icon': 'Fire',   'name': 'Campfire',    'color': [0.40, 0.20, 0.10, 1]},
    {'key': 'white_noise', 'icon': 'White',  'name': 'White Noise', 'color': [0.28, 0.28, 0.32, 1]},
    {'key': 'pink_noise',  'icon': 'Pink',   'name': 'Pink Noise',  'color': [0.35, 0.20, 0.28, 1]},
    {'key': 'brown_noise', 'icon': 'Brown',  'name': 'Brown Noise', 'color': [0.28, 0.18, 0.12, 1]},
    {'key': 'heartbeat',   'icon': 'Heart',  'name': 'Heartbeat',   'color': [0.38, 0.12, 0.18, 1]},
]

# ── Theme definitions ──────────────────────────────────────────────
THEMES = {
    'dark': {
        # Root / window
        'bg':             [0.04, 0.045, 0.07, 1],
        'bar':            [0.06, 0.065, 0.10, 1],
        'title':          [0.78, 0.80, 0.94, 1],
        'muted_text':     [0.50, 0.55, 0.72, 1],
        'scrollbar':      [0.25, 0.28, 0.42, 0.5],
        'topbar_btn_bg':  [0.17, 0.19, 0.26, 1],
        'btn_fg':         [1, 1, 1, 0.9],
        'stop_btn_bg':    [0.48, 0.12, 0.12, 1],
        'theme_toggle_bg':[0.50, 0.44, 0.14, 1],
        # Popup
        'popup_bg':       [0.07, 0.08, 0.13, 0.96],
        'popup_title':    [0.80, 0.82, 0.95, 1],
        'popup_btn':      [0.17, 0.22, 0.38, 1],
        'popup_close':    [0.22, 0.24, 0.32, 1],
        'popup_sep':      [0.28, 0.30, 0.38, 1],
        'popup_save':     [0.14, 0.40, 0.22, 1],
        'popup_delete':   [0.44, 0.14, 0.14, 1],
        'popup_load':     [0.17, 0.22, 0.44, 1],
        'input_bg':       [0.14, 0.16, 0.24, 1],
        'input_fg':       [0.88, 0.88, 0.95, 1],
        'input_hint':     [0.38, 0.42, 0.55, 1],
        'preset_name':    [0.82, 0.84, 0.95, 1],
        'empty_text':     [0.48, 0.50, 0.60, 1],
        # Card
        'card_base':      [0.10, 0.11, 0.16, 1],
        'card_icon':      [0.92, 0.92, 1.0, 0.9],
        'card_name':      [0.72, 0.74, 0.88, 1],
        'card_btn_active': [0.16, 0.48, 0.28, 1],
        'card_btn_normal': [0.20, 0.22, 0.30, 1],
        'card_btn_text':  [1, 1, 1, 0.9],
        'card_vol_label': [0.50, 0.52, 0.65, 1],
    },
    'light': {
        # Root / window
        'bg':             [0.94, 0.95, 0.96, 1],
        'bar':            [0.98, 0.98, 1.0, 1],
        'title':          [0.15, 0.17, 0.28, 1],
        'muted_text':     [0.40, 0.42, 0.52, 1],
        'scrollbar':      [0.60, 0.62, 0.68, 0.5],
        'topbar_btn_bg':  [0.82, 0.84, 0.90, 1],
        'btn_fg':         [0.12, 0.12, 0.18, 0.95],
        'stop_btn_bg':    [0.82, 0.28, 0.28, 1],
        'theme_toggle_bg':[0.22, 0.24, 0.45, 1],
        # Popup
        'popup_bg':       [0.96, 0.96, 0.98, 0.98],
        'popup_title':    [0.18, 0.20, 0.32, 1],
        'popup_btn':      [0.58, 0.62, 0.78, 1],
        'popup_close':    [0.76, 0.78, 0.84, 1],
        'popup_sep':      [0.72, 0.74, 0.80, 1],
        'popup_save':     [0.30, 0.68, 0.40, 1],
        'popup_delete':   [0.82, 0.34, 0.34, 1],
        'popup_load':     [0.44, 0.52, 0.80, 1],
        'input_bg':       [1.0, 1.0, 1.0, 1],
        'input_fg':       [0.12, 0.12, 0.18, 1],
        'input_hint':     [0.58, 0.60, 0.68, 1],
        'preset_name':    [0.18, 0.20, 0.32, 1],
        'empty_text':     [0.50, 0.52, 0.58, 1],
        # Card
        'card_base':      [1.0, 1.0, 1.0, 1],
        'card_icon':      [0.18, 0.20, 0.34, 0.9],
        'card_name':      [0.36, 0.38, 0.50, 1],
        'card_btn_active': [0.24, 0.64, 0.38, 1],
        'card_btn_normal': [0.78, 0.80, 0.88, 1],
        'card_btn_text':  [0.12, 0.12, 0.18, 0.95],
        'card_vol_label': [0.48, 0.50, 0.60, 1],
    },
}

# KV layout is auto-loaded by Kivy (sleepmusic.kv matches SleepMusicApp)


# ═══════════════════════════════════════════════════════════════════
#  Sound Card Widget
# ═══════════════════════════════════════════════════════════════════

def _light_active_color(dark_color):
    """Brighten active card color for light mode."""
    return [
        min(dark_color[0] + 0.42, 1.0),
        min(dark_color[1] + 0.42, 1.0),
        min(dark_color[2] + 0.42, 1.0),
        1,
    ]


class SoundCard(BoxLayout):
    """A card representing one ambient sound with play/stop + volume."""

    sound_key      = StringProperty('')
    sound_name     = StringProperty('')
    icon_label     = StringProperty('')
    card_color     = ListProperty([0.10, 0.11, 0.16, 1])
    active_color   = ListProperty([0.10, 0.11, 0.16, 1])
    volume_value   = NumericProperty(50)
    is_active      = BooleanProperty(False)

    # Theme-bound colors (defaults = dark)
    icon_color     = ListProperty([0.92, 0.92, 1.0, 0.9])
    name_color     = ListProperty([0.72, 0.74, 0.88, 1])
    btn_active_color = ListProperty([0.16, 0.48, 0.28, 1])
    btn_normal_color = ListProperty([0.20, 0.22, 0.30, 1])
    btn_text_color = ListProperty([1, 1, 1, 0.9])
    vol_label_color = ListProperty([0.50, 0.52, 0.65, 1])

    _dark_active   = [0.10, 0.11, 0.16, 1]
    _light_active  = [1.0, 1.0, 1.0, 1]

    def __init__(self, info, audio_engine, theme='dark', **kwargs):
        self.audio_engine   = audio_engine
        self.sound_key      = info['key']
        self.sound_name     = info['name']
        self.icon_label     = info['icon']
        self._dark_active   = list(info['color'])
        self._light_active  = _light_active_color(info['color'])
        self.apply_theme(theme)
        super().__init__(**kwargs)

    def apply_theme(self, theme):
        t = THEMES[theme]
        self._base_color    = list(t['card_base'])
        self.active_color   = list(self._dark_active if theme == 'dark'
                                   else self._light_active)
        self.icon_color     = list(t['card_icon'])
        self.name_color     = list(t['card_name'])
        self.btn_active_color = list(t['card_btn_active'])
        self.btn_normal_color = list(t['card_btn_normal'])
        self.btn_text_color = list(t['card_btn_text'])
        self.vol_label_color = list(t['card_vol_label'])
        # Update card bg based on current state
        if self.is_active:
            self.card_color = list(self.active_color)
        else:
            self.card_color = list(self._base_color)

    def on_toggle(self, state):
        if state == 'down':
            self.audio_engine.play(self.sound_key)
            self.is_active  = True
            self.card_color = list(self.active_color)
        else:
            self.audio_engine.stop(self.sound_key)
            self.is_active  = False
            self.card_color = list(self._base_color)

    def on_volume_change(self, value):
        self.volume_value = value
        self.audio_engine.set_volume(self.sound_key, value / 100.0)

    def set_playing(self, playing, volume=None):
        """Programmatically update this card's state."""
        btn = self.ids.get('play_btn')
        if btn:
            btn.state = 'down' if playing else 'normal'
        if volume is not None:
            self.volume_value = volume * 100
            slider = self.ids.get('volume_slider')
            if slider:
                slider.value = volume * 100


# ═══════════════════════════════════════════════════════════════════
#  Root Widget (main screen)
# ═══════════════════════════════════════════════════════════════════

class RootWidget(BoxLayout):
    timer_text    = StringProperty('Timer')
    timer_running = BooleanProperty(False)
    is_loading    = BooleanProperty(True)
    master_volume = NumericProperty(80)

    # ── Theme-bound colour properties ─────────────────────────────
    is_dark          = BooleanProperty(True)
    theme_btn_text   = StringProperty('Light')
    bg_color         = ListProperty(THEMES['dark']['bg'])
    bar_color        = ListProperty(THEMES['dark']['bar'])
    title_color      = ListProperty(THEMES['dark']['title'])
    muted_text       = ListProperty(THEMES['dark']['muted_text'])
    scrollbar_color  = ListProperty(THEMES['dark']['scrollbar'])
    topbar_btn_bg    = ListProperty(THEMES['dark']['topbar_btn_bg'])
    btn_fg           = ListProperty(THEMES['dark']['btn_fg'])
    stop_btn_bg      = ListProperty(THEMES['dark']['stop_btn_bg'])
    theme_toggle_bg  = ListProperty(THEMES['dark']['theme_toggle_bg'])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_theme  = 'dark'
        self.audio_engine   = AudioEngine(SOUNDS_DIR)
        self.timer_manager  = TimerManager(
            on_tick=self._on_timer_tick,
            on_complete=self._on_timer_complete,
        )
        self.preset_manager = PresetManager(PRESETS_FILE)
        self.sound_cards    = {}       # key → SoundCard
        Clock.schedule_once(self._start_generation, 0.5)

    # ── Sound generation (background thread) ──────────────────────

    def _start_generation(self, _dt):
        threading.Thread(target=self._generate, daemon=True).start()

    def _generate(self):
        gen = SoundGenerator(SOUNDS_DIR)
        gen.generate_all()
        Clock.schedule_once(self._sounds_ready, 0)

    def _sounds_ready(self, _dt):
        self.is_loading = False
        self.audio_engine.load_sounds()
        self.audio_engine.set_master_volume(self.master_volume / 100.0)
        self._build_cards()

    def _build_cards(self):
        grid = self.ids.sound_grid
        grid.clear_widgets()
        for info in SOUND_CATALOGUE:
            card = SoundCard(info, self.audio_engine, theme=self.current_theme)
            self.sound_cards[info['key']] = card
            grid.add_widget(card)

    # ── Theme switching ───────────────────────────────────────────

    def toggle_theme(self):
        """Switch between dark and light mode."""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.is_dark = (self.current_theme == 'dark')
        self._apply_theme()

    def _apply_theme(self):
        t = THEMES[self.current_theme]
        # Root properties
        self.bg_color        = list(t['bg'])
        self.bar_color       = list(t['bar'])
        self.title_color     = list(t['title'])
        self.muted_text      = list(t['muted_text'])
        self.scrollbar_color = list(t['scrollbar'])
        self.topbar_btn_bg   = list(t['topbar_btn_bg'])
        self.btn_fg          = list(t['btn_fg'])
        self.stop_btn_bg     = list(t['stop_btn_bg'])
        self.theme_toggle_bg = list(t['theme_toggle_bg'])
        self.theme_btn_text  = 'Light' if self.current_theme == 'dark' else 'Dark'
        # Window clear color
        Window.clearcolor = tuple(t['bg'])
        # Update each sound card
        for card in self.sound_cards.values():
            card.apply_theme(self.current_theme)

    # ── Volume / playback ─────────────────────────────────────────

    def on_master_volume_change(self, value):
        self.master_volume = value
        self.audio_engine.set_master_volume(value / 100.0)

    def stop_all_sounds(self):
        self.audio_engine.stop_all()
        for card in self.sound_cards.values():
            card.set_playing(False)

    # ── Timer popup ───────────────────────────────────────────────

    def show_timer_popup(self):
        t = THEMES[self.current_theme]
        content = BoxLayout(orientation='vertical', spacing=dp(10),
                            padding=dp(14))

        content.add_widget(Label(
            text='Sleep Timer', font_size=sp(19), bold=True,
            size_hint_y=None, height=dp(36),
            color=t['popup_title']))

        popup = Popup(
            title='', content=content,
            size_hint=(0.85, 0.55), separator_height=0,
            background_color=t['popup_bg'])

        # Duration buttons
        btn_grid = GridLayout(cols=3, spacing=dp(8),
                              size_hint_y=None, height=dp(100))
        for mins in (15, 30, 45, 60, 90, 120):
            b = Button(text=f'{mins} min', font_size=sp(13),
                       background_normal='',
                       background_color=t['popup_btn'],
                       color=t['btn_fg'])
            b.bind(on_release=lambda _, m=mins: self._start_timer(m, popup))
            btn_grid.add_widget(b)
        content.add_widget(btn_grid)

        # Active timer info
        if self.timer_manager.is_running:
            content.add_widget(Label(
                text=f'Running: {self.timer_manager.get_time_string()}',
                font_size=sp(15), color=(0.92, 0.58, 0.28, 1),
                size_hint_y=None, height=dp(36)))
            cancel = Button(text='Cancel Timer', font_size=sp(13),
                            size_hint_y=None, height=dp(42),
                            background_normal='',
                            background_color=t['popup_delete'],
                            color=(1, 1, 1, 0.9))
            cancel.bind(on_release=lambda _: self._cancel_timer(popup))
            content.add_widget(cancel)

        close = Button(text='Close', font_size=sp(13),
                       size_hint_y=None, height=dp(42),
                       background_normal='',
                       background_color=t['popup_close'],
                       color=t['btn_fg'])
        close.bind(on_release=popup.dismiss)
        content.add_widget(close)
        popup.open()

    def _start_timer(self, minutes, popup):
        self.timer_manager.start(minutes)
        self.timer_running = True
        self.timer_text = self.timer_manager.get_time_string()
        popup.dismiss()

    def _cancel_timer(self, popup):
        self.timer_manager.stop()
        self.timer_running = False
        self.timer_text = 'Timer'
        popup.dismiss()

    def _on_timer_tick(self, _remaining):
        self.timer_text = self.timer_manager.get_time_string()

    def _on_timer_complete(self):
        self.timer_running = False
        self.timer_text = 'Timer'
        self.stop_all_sounds()

    # ── Presets popup ─────────────────────────────────────────────

    def show_presets_popup(self):
        t = THEMES[self.current_theme]
        content = BoxLayout(orientation='vertical', spacing=dp(10),
                            padding=dp(14))

        content.add_widget(Label(
            text='Sound Presets', font_size=sp(19), bold=True,
            size_hint_y=None, height=dp(36),
            color=t['popup_title']))

        popup = Popup(
            title='', content=content,
            size_hint=(0.88, 0.72), separator_height=0,
            background_color=t['popup_bg'])

        # ── Save row ──
        save_row = BoxLayout(size_hint_y=None, height=dp(42),
                             spacing=dp(8))
        name_input = TextInput(
            hint_text='Preset name...', font_size=sp(13),
            multiline=False, size_hint_x=0.62,
            background_color=t['input_bg'],
            foreground_color=t['input_fg'],
            cursor_color=(0.40, 0.60, 1, 1),
            hint_text_color=t['input_hint'])
        save_btn = Button(
            text='Save', font_size=sp(12),
            size_hint_x=0.38, background_normal='',
            background_color=t['popup_save'],
            color=(1, 1, 1, 0.9))
        save_btn.bind(on_release=lambda _: self._save_preset(
            name_input.text, popup))
        save_row.add_widget(name_input)
        save_row.add_widget(save_btn)
        content.add_widget(save_row)

        # ── Separator ──
        content.add_widget(Label(
            text='─' * 42, font_size=sp(9), size_hint_y=None,
            height=dp(16), color=t['popup_sep']))

        # ── Preset list ──
        presets = self.preset_manager.get_all_presets()
        if presets:
            scroll = ScrollView(do_scroll_x=False)
            plist = BoxLayout(orientation='vertical', spacing=dp(6),
                              size_hint_y=None, padding=[0, dp(4)])
            plist.bind(minimum_height=plist.setter('height'))

            for pname, pdata in presets.items():
                row = BoxLayout(size_hint_y=None, height=dp(42),
                                spacing=dp(6))
                row.add_widget(Label(
                    text=pname, font_size=sp(13), bold=True,
                    size_hint_x=0.40, color=t['preset_name'],
                    halign='left', valign='center'))
                load_b = Button(
                    text='Load', font_size=sp(12), size_hint_x=0.30,
                    background_normal='',
                    background_color=t['popup_load'],
                    color=t['btn_fg'])
                load_b.bind(on_release=lambda _, n=pname:
                            self._load_preset(n, popup))
                del_b = Button(
                    text='Delete', font_size=sp(12), size_hint_x=0.30,
                    background_normal='',
                    background_color=t['popup_delete'],
                    color=(1, 1, 1, 0.9))
                del_b.bind(on_release=lambda _, n=pname:
                           self._delete_preset(n, popup))
                row.add_widget(load_b)
                row.add_widget(del_b)
                plist.add_widget(row)

            scroll.add_widget(plist)
            content.add_widget(scroll)
        else:
            content.add_widget(Label(
                text='No presets yet.\nPlay some sounds, then save!',
                font_size=sp(13), color=t['empty_text'],
                halign='center'))

        close = Button(text='Close', font_size=sp(13),
                       size_hint_y=None, height=dp(42),
                       background_normal='',
                       background_color=t['popup_close'],
                       color=t['btn_fg'])
        close.bind(on_release=popup.dismiss)
        content.add_widget(close)
        popup.open()

    def _save_preset(self, name, popup):
        if not name.strip():
            return
        active = self.audio_engine.get_active_sounds()
        if active:
            self.preset_manager.add_preset(name.strip(), active)
            popup.dismiss()
            self.show_presets_popup()     # refresh

    def _load_preset(self, name, popup):
        data = self.preset_manager.get_preset(name)
        if data:
            self.stop_all_sounds()
            self.audio_engine.load_preset(data)
            for key, vol in data.items():
                if key in self.sound_cards:
                    self.sound_cards[key].set_playing(True, vol)
            popup.dismiss()

    def _delete_preset(self, name, popup):
        self.preset_manager.remove_preset(name)
        popup.dismiss()
        self.show_presets_popup()         # refresh


# ═══════════════════════════════════════════════════════════════════
#  Application
# ═══════════════════════════════════════════════════════════════════

class SleepMusicApp(App):
    title = 'Sleep Music'

    def build(self):
        Window.clearcolor = (0.04, 0.045, 0.07, 1)
        return RootWidget()

    def on_stop(self):
        root = self.root
        if hasattr(root, 'audio_engine'):
            root.audio_engine.stop_all()
        if hasattr(root, 'timer_manager'):
            root.timer_manager.stop()


# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    SleepMusicApp().run()
