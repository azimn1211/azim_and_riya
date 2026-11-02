#!/usr/bin/env python3
"""Paint every floral asset of the site into website/assets/flowers/*.webp.

All artwork is generated here (no third-party images).  Branches are painted
upright with the root at the bottom-centre so the page can sway them from the
root with the layered "whip" animation.

    python3 tools/paint_assets.py            # everything
    python3 tools/paint_assets.py wreath     # one or more by name
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from watercolor import Canvas  # noqa: E402
from watercolor import curve_from, tangent  # noqa: E402
from flora import (PLUM, PEACH, BLUSH, FROND, FROND_SOFT, GOLD, SAGE,  # noqa: E402
                   flower, bud, leaf, frond, sprig, splatter, berry_stem)

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'website', 'assets', 'flowers'))
UP = -math.pi / 2
ASSETS = {}


def asset(name, w, h, seed):
    def deco(fn):
        ASSETS[name] = (fn, w, h, seed)
        return fn
    return deco


# ---------------------------------------------------------------------------
# Upright branches (root at bottom centre) — these sway on the page
# ---------------------------------------------------------------------------

@asset('frond-a', 440, 900, 3)
def _(cv):
    frond(cv, 200, 895, UP + 0.04, 800, 0.42, FROND, n=15, leaf_len=0.25)


@asset('frond-b', 440, 900, 5)
def _(cv):
    frond(cv, 268, 895, UP - 0.04, 780, -0.45, FROND, n=14, leaf_len=0.25)


@asset('frond-soft', 440, 900, 8)
def _(cv):
    frond(cv, 215, 895, UP, 790, 0.3, FROND_SOFT, n=14, leaf_len=0.25)


@asset('sprig-gold', 420, 900, 13)
def _(cv):
    pts = sprig(cv, 210, 895, UP + 0.06, 780, -0.38, GOLD, n=8, leaf_len=0.27)
    berry_stem(cv, pts[18][0], pts[18][1], UP + 0.45, 220, 0.3, count=6)


@asset('sprig-sage', 420, 900, 21)
def _(cv):
    sprig(cv, 200, 895, UP - 0.05, 780, 0.36, SAGE, n=8, leaf_ratio=0.3, leaf_len=0.27)


@asset('stem-peach', 420, 900, 31)
def _(cv):
    pts = sprig(cv, 210, 895, UP + 0.08, 640, -0.22, SAGE, n=4, start=0.25, leaf_len=0.26)
    x, y = pts[-1]
    leaf(cv, x - 20, y + 40, UP - 1.1, 120, 40, GOLD)
    bud(cv, x + 70, y + 60, UP + 0.6, 46, PEACH, sepal=FROND)
    flower(cv, x, y - 95, 125, PEACH, rot=0.4, tilt=0.8, style='rose')


@asset('stem-plum', 420, 900, 37)
def _(cv):
    pts = sprig(cv, 210, 895, UP - 0.06, 640, 0.24, GOLD, n=4, start=0.25, leaf_len=0.26)
    x, y = pts[-1]
    bud(cv, x - 80, y + 70, UP - 0.7, 44, PLUM)
    flower(cv, x, y - 95, 128, PLUM, rot=-0.3, tilt=0.82, style='peony')


@asset('stem-buds', 300, 760, 41)
def _(cv):
    pts = frond(cv, 150, 755, UP + 0.04, 520, -0.3, FROND_SOFT, n=6, leaf_len=0.22, start=0.3)
    x, y = pts[-1]
    bud(cv, x, y, UP - 0.1, 60, PEACH, sepal=FROND)
    bud(cv, pts[38][0] + 6, pts[38][1], UP + 0.9, 46, PLUM)
    bud(cv, pts[26][0] - 6, pts[26][1], UP - 1.0, 40, BLUSH, sepal=FROND)


# ---------------------------------------------------------------------------
# Flower clusters (static heads laid over the swaying branches)
# ---------------------------------------------------------------------------

@asset('cluster-a', 1000, 900, 51)
def _(cv):
    ox, oy = 60, 50
    # foliage peeking out behind the heads
    sprig(cv, 520 + ox, 380 + oy, -0.35, 300, 0.25, GOLD, n=5)
    frond(cv, 470 + ox, 300 + oy, -0.9, 330, 0.3, FROND, n=9, leaf_len=0.3)
    frond(cv, 300 + ox, 520 + oy, 2.1, 240, -0.3, FROND, n=8, leaf_len=0.3)
    sprig(cv, 250 + ox, 560 + oy, 1.75, 200, 0.3, GOLD, n=4)
    leaf(cv, 560 + ox, 520 + oy, 0.55, 170, 58, SAGE)
    # heads
    flower(cv, 210 + ox, 610 + oy, 150, PEACH, rot=0.6, tilt=0.86, style='rose')
    flower(cv, 380 + ox, 330 + oy, 235, PLUM, rot=0.2, tilt=0.9, style='peony')
    bud(cv, 640 + ox, 250 + oy, -0.5, 54, PEACH, sepal=FROND)
    bud(cv, 600 + ox, 600 + oy, 0.6, 48, PLUM)
    leaf(cv, 130 + ox, 420 + oy, 3.6, 130, 44, GOLD)
    splatter(cv, 620 + ox, 420 + oy, 100, 45)


@asset('cluster-b', 900, 820, 57)
def _(cv):
    ox, oy = 30, 70
    frond(cv, 380 + ox, 360 + oy, -2.5, 300, -0.3, FROND, n=8, leaf_len=0.3)
    sprig(cv, 470 + ox, 300 + oy, -1.25, 260, 0.3, GOLD, n=5)
    frond(cv, 520 + ox, 420 + oy, 0.2, 250, 0.25, FROND_SOFT, n=8, leaf_len=0.3)
    leaf(cv, 300 + ox, 480 + oy, 2.6, 160, 54, SAGE)
    flower(cv, 560 + ox, 430 + oy, 150, PLUM, rot=-0.4, tilt=0.88, style='peony')
    flower(cv, 340 + ox, 330 + oy, 190, PEACH, rot=0.1, tilt=0.86, style='rose')
    bud(cv, 170 + ox, 230 + oy, -2.4, 50, PLUM)
    bud(cv, 520 + ox, 170 + oy, -1.3, 44, BLUSH, sepal=FROND)
    splatter(cv, 260 + ox, 520 + oy, 90, 40)


@asset('cluster-c', 640, 560, 63)
def _(cv):
    frond(cv, 320, 290, -0.4, 230, 0.3, FROND, n=7, leaf_len=0.3)
    sprig(cv, 280, 300, -2.6, 200, -0.3, GOLD, n=4)
    flower(cv, 300, 300, 150, PLUM, rot=0.5, tilt=0.9, style='peony')
    bud(cv, 460, 420, 0.7, 40, PEACH, sepal=FROND)
    splatter(cv, 330, 320, 110, 25)


# ---------------------------------------------------------------------------
# Hero wreath — an oval of fronds and gold leaves with two flower clusters
# ---------------------------------------------------------------------------

@asset('wreath', 1000, 1240, 71)
def _(cv):
    cx, cy, rx, ry = 500, 640, 360, 500

    def at(t):
        return cx + rx * math.cos(t), cy + ry * math.sin(t)

    def tan(t):
        return math.atan2(ry * math.cos(t), -rx * math.sin(t))

    # vine: alternating fronds / sprigs laid tangentially, clockwise
    steps = 22
    for i in range(steps):
        t = -math.pi / 2 + 2 * math.pi * i / steps + cv.rng.uniform(-0.04, 0.04)
        x, y = at(t)
        a = tan(t) + cv.rng.uniform(-0.12, 0.12)
        L = cv.rng.uniform(170, 230)
        kind = i % 3
        if kind == 0:
            frond(cv, x, y, a, L, 0.35, FROND, n=7, leaf_len=0.3, layers=8)
        elif kind == 1:
            sprig(cv, x, y, a, L, 0.3, GOLD, n=4, leaf_len=0.3, layers=12)
        else:
            frond(cv, x, y, a, L * 0.9, 0.3, FROND_SOFT, n=6, leaf_len=0.3, layers=8)
    # small blooms dotted along the ring
    for t, pal in ((0.15, PEACH), (2.2, BLUSH), (-1.05, PEACH), (3.55, PLUM)):
        x, y = at(t)
        bud(cv, x, y, tan(t) + 0.6, 34, pal, sepal=FROND)
    # top-left cluster
    tx, ty = at(-2.25)
    frond(cv, tx + 30, ty + 20, -0.1, 300, 0.35, FROND, n=9)
    sprig(cv, tx, ty, 2.0, 260, -0.3, GOLD, n=5)
    flower(cv, tx - 40, ty + 130, 105, PEACH, rot=0.4, style='rose')
    flower(cv, tx + 40, ty - 10, 150, PLUM, rot=0.1, style='peony')
    bud(cv, tx + 190, ty - 70, -0.6, 42, PEACH, sepal=FROND)
    splatter(cv, tx + 120, ty - 40, 90, 30)
    # bottom-right cluster
    bx, by = at(0.85)
    frond(cv, bx - 20, by - 10, 3.0, 280, -0.3, FROND, n=8)
    sprig(cv, bx, by, -1.1, 240, 0.3, GOLD, n=5)
    flower(cv, bx + 50, by - 90, 92, PLUM, rot=-0.5, style='peony')
    flower(cv, bx - 10, by + 30, 128, PEACH, rot=0.2, style='rose')
    bud(cv, bx - 160, by + 70, 2.6, 38, PLUM)
    splatter(cv, bx - 60, by + 40, 80, 25)


# ---------------------------------------------------------------------------
# Flower beds
# ---------------------------------------------------------------------------

def _bed(cv, W, H, scale, heads):
    rng = cv.rng
    base = H + 20 * scale
    # back layer: fronds and sprigs fanning upward
    n = int(W / (70 * scale))
    for i in range(n):
        x = (i + 0.5) * W / n + rng.uniform(-20, 20) * scale
        a = UP + rng.uniform(-0.75, 0.75)
        L = rng.uniform(260, 420) * scale
        kind = rng.random()
        if kind < 0.45:
            frond(cv, x, base, a, L, rng.uniform(-0.4, 0.4), FROND, n=9, layers=8)
        elif kind < 0.75:
            sprig(cv, x, base, a, L, rng.uniform(-0.4, 0.4), GOLD, n=6, layers=12)
        else:
            frond(cv, x, base, a, L, rng.uniform(-0.4, 0.4), FROND_SOFT, n=8, layers=8)
    for i in range(int(n * 0.6)):
        x = rng.uniform(0.05, 0.95) * W
        berry_stem(cv, x, base - 40 * scale, UP + rng.uniform(-0.6, 0.6),
                   rng.uniform(160, 260) * scale, rng.uniform(-0.3, 0.3))
    # buds on stems standing above the heads
    for i in range(int(n * 0.45)):
        x0 = rng.uniform(0.06, 0.94) * W
        a = UP + rng.uniform(-0.45, 0.45)
        L = rng.uniform(230, 340) * scale
        pts = curve_from(x0, base, a, L, rng.uniform(-0.3, 0.3), n=30)
        cv.stroke_line(pts, FROND['stem'], 0.8, max(1.0, 5 * scale))
        pal = rng.choice((PEACH, PLUM, BLUSH))
        leaf(cv, pts[12][0], pts[12][1], tangent(pts, 12) + rng.choice((-1, 1)) * 0.8,
             70 * scale, 22 * scale, rng.choice((SAGE, GOLD)), layers=10)
        bud(cv, pts[-1][0], pts[-1][1], tangent(pts, len(pts) - 1),
            rng.uniform(34, 48) * scale, pal, sepal=FROND)
    # heads
    for fx, fy, R, pal, style in heads:
        flower(cv, fx * W, H - fy * scale, R * scale, pal, rot=rng.uniform(-0.6, 0.6),
               tilt=rng.uniform(0.8, 0.9), style=style)
    # foreground leaves
    for i in range(int(n * 0.5)):
        x = rng.uniform(0.03, 0.97) * W
        a = UP + rng.choice((-1, 1)) * rng.uniform(0.7, 1.3)
        leaf(cv, x, H + 10, a, rng.uniform(110, 170) * scale, rng.uniform(34, 50) * scale,
             rng.choice((SAGE, GOLD)))
    splatter(cv, W * 0.5, H * 0.35, W * 0.3, int(W / 16), rmax=2.6 * scale)


@asset('bed-footer', 1800, 660, 81)
def _(cv):
    _bed(cv, 1800, 660, 1.0, [
        (0.07, 70, 120, PEACH, 'rose'), (0.22, 110, 155, PLUM, 'peony'),
        (0.36, 60, 135, BLUSH, 'rose'), (0.5, 120, 190, PEACH, 'rose'),
        (0.64, 60, 140, PLUM, 'peony'), (0.79, 110, 160, PEACH, 'rose'),
        (0.93, 70, 125, PLUM, 'peony'),
    ])


@asset('bed-intro', 1200, 420, 87)
def _(cv):
    _bed(cv, 1200, 420, 0.62, [
        (0.06, 40, 120, PLUM, 'peony'), (0.24, 70, 150, PEACH, 'rose'),
        (0.5, 40, 120, BLUSH, 'rose'), (0.75, 75, 160, PLUM, 'peony'),
        (0.94, 40, 120, PEACH, 'rose'),
    ])


def main(names):
    os.makedirs(OUT, exist_ok=True)
    for name in names or ASSETS:
        fn, w, h, seed = ASSETS[name]
        cv = Canvas(w, h, ss=2, seed=seed)
        fn(cv)
        img = cv.to_image()
        bbox = img.getbbox()
        a = img.getchannel('A')
        edges = {'L': a.crop((0, 0, 1, h)), 'T': a.crop((0, 0, w, 1)),
                 'R': a.crop((w - 1, 0, w, h)), 'B': a.crop((0, h - 1, w, h))}
        hit = ''.join(k for k, e in edges.items() if e.getextrema()[1] > 40)
        path = os.path.join(OUT, name + '.webp')
        img.save(path, 'WEBP', quality=86, method=6)
        print(f'{name:12s} {w}x{h}  touches-edge={hit or "-":4s} {os.path.getsize(path) // 1024} KB')


if __name__ == '__main__':
    main(sys.argv[1:])
