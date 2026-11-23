"""
Procedural Ambient Sound Generator

Generates WAV files for various ambient sounds using numpy.
Each sound is a 10-second loop designed for seamless playback.
"""

import os
import wave
import numpy as np

SAMPLE_RATE = 44100
DURATION = 10  # seconds per loop
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit


class SoundGenerator:
    """Generates ambient sound WAV files procedurally."""

    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _save_wav(self, filename, samples):
        """Save numpy float samples as a 16-bit WAV file."""
        filepath = os.path.join(self.output_dir, filename)
        samples = np.clip(samples, -1.0, 1.0)
        int_samples = (samples * 32767).astype(np.int16)
        with wave.open(filepath, 'w') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(int_samples.tobytes())
        return filepath

    def _apply_fade(self, samples, fade_duration=0.3):
        """Apply fade-in and fade-out for cleaner looping."""
        fade_len = int(fade_duration * SAMPLE_RATE)
        fade_len = min(fade_len, len(samples) // 4)
        samples[:fade_len] *= np.linspace(0, 1, fade_len)
        samples[-fade_len:] *= np.linspace(1, 0, fade_len)
        return samples

    def _lowpass(self, data, kernel_size=10):
        """Simple moving-average low-pass filter."""
        kernel = np.ones(kernel_size) / kernel_size
        return np.convolve(data, kernel, mode='same')

    # ── Individual sound generators ─────────────────────────────────

    def generate_white_noise(self):
        n = SAMPLE_RATE * DURATION
        samples = np.random.normal(0, 0.3, n)
        return self._save_wav('white_noise.wav', self._apply_fade(samples))

    def generate_pink_noise(self):
        """Pink noise via spectral shaping (1/√f)."""
        n = SAMPLE_RATE * DURATION
        white = np.fft.rfft(np.random.randn(n))
        freqs = np.fft.rfftfreq(n, d=1.0 / SAMPLE_RATE)
        freqs[0] = 1  # avoid divide-by-zero
        pink_filter = 1.0 / np.sqrt(freqs)
        pink_filter[0] = 0  # kill DC
        pink = np.fft.irfft(white * pink_filter, n=n)
        pink = pink / np.max(np.abs(pink)) * 0.4
        return self._save_wav('pink_noise.wav', self._apply_fade(pink))

    def generate_brown_noise(self):
        """Brown noise via cumulative sum of white noise."""
        n = SAMPLE_RATE * DURATION
        brown = np.cumsum(np.random.randn(n))
        brown = brown / np.max(np.abs(brown)) * 0.4
        return self._save_wav('brown_noise.wav', self._apply_fade(brown))

    def generate_rain(self):
        """Rain: filtered noise + raindrop impacts."""
        n = SAMPLE_RATE * DURATION
        noise = np.random.normal(0, 0.15, n)
        # Raindrop impacts
        num_drops = n // 80
        positions = np.random.randint(0, n, num_drops)
        for pos in positions:
            drop_len = np.random.randint(40, 180)
            end = min(pos + drop_len, n)
            amp = np.random.uniform(0.04, 0.18)
            t = np.arange(end - pos)
            noise[pos:end] += amp * np.exp(-t / 30.0) * np.random.randn(end - pos)
        noise = self._lowpass(noise, 6)
        noise = noise / np.max(np.abs(noise)) * 0.45
        return self._save_wav('rain.wav', self._apply_fade(noise))

    def generate_ocean(self):
        """Ocean waves: modulated filtered noise."""
        n = SAMPLE_RATE * DURATION
        t = np.linspace(0, DURATION, n)
        # Wave envelope (slow oscillation)
        envelope = 0.3 + 0.3 * np.sin(2 * np.pi * 0.1 * t)
        envelope += 0.12 * np.sin(2 * np.pi * 0.24 * t + 1.2)
        noise = np.random.normal(0, 1, n)
        noise = self._lowpass(noise, 18)
        ocean = noise * envelope
        ocean = ocean / np.max(np.abs(ocean)) * 0.45
        return self._save_wav('ocean.wav', self._apply_fade(ocean))

    def generate_wind(self):
        """Wind: slowly varying filtered noise."""
        n = SAMPLE_RATE * DURATION
        t = np.linspace(0, DURATION, n)
        mod = 0.3 + 0.2 * np.sin(2 * np.pi * 0.15 * t)
        mod += 0.1 * np.sin(2 * np.pi * 0.07 * t + 0.5)
        noise = self._lowpass(np.random.normal(0, 1, n), 22)
        wind = noise * mod
        wind = wind / np.max(np.abs(wind)) * 0.4
        return self._save_wav('wind.wav', self._apply_fade(wind))

    def generate_forest(self):
        """Forest: gentle rustling + bird chirps."""
        n = SAMPLE_RATE * DURATION
        bg = self._lowpass(np.random.normal(0, 0.05, n), 30)
        # Bird chirps
        for _ in range(8):
            start = np.random.randint(0, n - SAMPLE_RATE)
            freq = np.random.uniform(2000, 5000)
            chirp_len = np.random.randint(SAMPLE_RATE // 20, SAMPLE_RATE // 5)
            ct = np.linspace(0, chirp_len / SAMPLE_RATE, chirp_len)
            freq_mod = freq + 500 * np.sin(2 * np.pi * 15 * ct)
            chirp = 0.08 * np.sin(2 * np.pi * freq_mod * ct)
            chirp *= np.exp(-3 * ct / ct[-1])
            end = min(start + chirp_len, n)
            bg[start:end] += chirp[:end - start]
        bg = bg / np.max(np.abs(bg)) * 0.35
        return self._save_wav('forest.wav', self._apply_fade(bg))

    def generate_thunder(self):
        """Thunder: rain base + rumbling bursts."""
        n = SAMPLE_RATE * DURATION
        rain = self._lowpass(np.random.normal(0, 0.1, n), 8)
        for _ in range(2):
            start = np.random.randint(0, n - 2 * SAMPLE_RATE)
            length = np.random.randint(SAMPLE_RATE, 2 * SAMPLE_RATE)
            rt = np.linspace(0, length / SAMPLE_RATE, length)
            rumble = self._lowpass(np.random.normal(0, 0.5, length), 50)
            rumble *= np.exp(-2 * rt / rt[-1])
            end = min(start + length, n)
            rain[start:end] += rumble[:end - start]
        rain = rain / np.max(np.abs(rain)) * 0.45
        return self._save_wav('thunder.wav', self._apply_fade(rain))

    def generate_stream(self):
        """Babbling stream: water trickling with splashes."""
        n = SAMPLE_RATE * DURATION
        t = np.linspace(0, DURATION, n)
        water = self._lowpass(np.random.normal(0, 0.3, n), 3)
        mod = 1.0 + 0.3 * np.sin(2 * np.pi * 3 * t)
        mod += 0.2 * np.sin(2 * np.pi * 7.3 * t)
        water *= mod
        for _ in range(5):
            pos = np.random.randint(0, n - 5000)
            slen = np.random.randint(2000, 5000)
            splash = np.random.normal(0, 0.2, slen) * np.exp(-np.linspace(0, 8, slen))
            water[pos:pos + slen] += splash
        water = water / np.max(np.abs(water)) * 0.4
        return self._save_wav('stream.wav', self._apply_fade(water))

    def generate_campfire(self):
        """Campfire: hissing base + crackles and pops."""
        n = SAMPLE_RATE * DURATION
        hiss = self._lowpass(np.random.normal(0, 0.08, n), 10)
        for _ in range(200):
            pos = np.random.randint(0, n - 1000)
            clen = np.random.randint(80, 600)
            amp = np.random.uniform(0.08, 0.35)
            crack = amp * np.random.randn(clen) * np.exp(-np.linspace(0, 10, clen))
            end = min(pos + clen, n)
            hiss[pos:end] += crack[:end - pos]
        hiss = hiss / np.max(np.abs(hiss)) * 0.4
        return self._save_wav('campfire.wav', self._apply_fade(hiss))

    def generate_heartbeat(self):
        """Slow heartbeat at resting rate (60 bpm)."""
        n = SAMPLE_RATE * DURATION
        hb = np.zeros(n)
        interval = SAMPLE_RATE  # 60 bpm = 1 beat/sec
        for i in range(0, n, interval):
            # Lub
            lub_len = int(SAMPLE_RATE * 0.1)
            if i + lub_len < n:
                lt = np.linspace(0, 0.1, lub_len)
                hb[i:i + lub_len] += 0.5 * np.sin(2 * np.pi * 60 * lt) * np.exp(-30 * lt)
            # Dub
            dub_start = i + int(SAMPLE_RATE * 0.2)
            dub_len = int(SAMPLE_RATE * 0.08)
            if dub_start + dub_len < n:
                dt = np.linspace(0, 0.08, dub_len)
                hb[dub_start:dub_start + dub_len] += 0.35 * np.sin(2 * np.pi * 80 * dt) * np.exp(-35 * dt)
        if np.max(np.abs(hb)) > 0:
            hb = hb / np.max(np.abs(hb)) * 0.5
        return self._save_wav('heartbeat.wav', hb)

    # ── Generate all sounds ─────────────────────────────────────────

    def generate_all(self, force=False):
        """Generate all sound files. Skips existing unless force=True."""
        generators = {
            'rain': self.generate_rain,
            'ocean': self.generate_ocean,
            'forest': self.generate_forest,
            'wind': self.generate_wind,
            'thunder': self.generate_thunder,
            'stream': self.generate_stream,
            'campfire': self.generate_campfire,
            'white_noise': self.generate_white_noise,
            'pink_noise': self.generate_pink_noise,
            'brown_noise': self.generate_brown_noise,
            'heartbeat': self.generate_heartbeat,
        }
        generated = []
        for name, func in generators.items():
            filepath = os.path.join(self.output_dir, f'{name}.wav')
            if force or not os.path.exists(filepath):
                print(f"  Generating: {name}...")
                func()
                generated.append(name)
            else:
                print(f"  Cached:     {name}")
        return generated
