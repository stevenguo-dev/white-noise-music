"""
Sleep Timer Manager

Provides a countdown timer that triggers a callback on completion
(used to auto-stop all sounds after a set duration).
"""

from kivy.clock import Clock


class TimerManager:
    """Countdown timer for sleep mode."""

    def __init__(self, on_tick=None, on_complete=None):
        self.remaining_seconds = 0
        self.is_running = False
        self._event = None
        self.on_tick = on_tick
        self.on_complete = on_complete

    def start(self, minutes):
        """Start a countdown of *minutes* minutes."""
        self.stop()
        self.remaining_seconds = int(minutes * 60)
        self.is_running = True
        self._event = Clock.schedule_interval(self._tick, 1.0)

    def stop(self):
        """Cancel the current timer."""
        if self._event:
            self._event.cancel()
            self._event = None
        self.is_running = False
        self.remaining_seconds = 0

    def _tick(self, _dt):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            if self.on_tick:
                self.on_tick(self.remaining_seconds)
            if self.remaining_seconds <= 0:
                self.is_running = False
                if self._event:
                    self._event.cancel()
                    self._event = None
                if self.on_complete:
                    self.on_complete()

    def get_time_string(self):
        """Return remaining time as MM:SS."""
        m, s = divmod(self.remaining_seconds, 60)
        return f"{m:02d}:{s:02d}"
