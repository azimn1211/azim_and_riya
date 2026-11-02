#!/usr/bin/env python3
"""Tileable warm paper texture for the invitation sheet (website/assets/paper.webp)."""
import os

import numpy as np
from PIL import Image

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'website', 'assets', 'paper.webp'))
N = 640


def periodic_noise(rng, sigma, aniso=(1.0, 1.0)):
    """Gaussian-filtered white noise via FFT, so it wraps seamlessly."""
    white = rng.standard_normal((N, N))
    fy = np.fft.fftfreq(N)[:, None] * aniso[0]
    fx = np.fft.fftfreq(N)[None, :] * aniso[1]
    filt = np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))
    out = np.real(np.fft.ifft2(np.fft.fft2(white) * filt))
    return out / (np.abs(out).max() + 1e-9)


def main():
    rng = np.random.default_rng(19)
    blotch = periodic_noise(rng, 60)
    cloud = periodic_noise(rng, 14)
    grain = periodic_noise(rng, 0.8)
    fibres = periodic_noise(rng, 2.2, aniso=(0.25, 1.0))   # stretched: faint fibres

    base = np.array([252, 248, 241], np.float32)
    shade = 1 + 0.02 * blotch + 0.014 * cloud + 0.038 * grain - 0.035 * np.clip(fibres, 0, 1)
    warm = np.array([0.0, -2.0, -5.0], np.float32)[None, None, :] * np.clip(blotch, 0, 1)[..., None]
    img = np.clip(base[None, None, :] * shade[..., None] + warm, 0, 255).astype(np.uint8)
    Image.fromarray(img, 'RGB').save(OUT, 'WEBP', quality=90, method=6)
    print(OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main()
