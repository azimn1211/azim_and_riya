"""Watercolor botanicals in the palette of Azim & Riya's printed card."""
import math

from watercolor import (hexc, mix, xform, petal_shape, place, leaf_shape,
                        curve_from, tangent, ribbon)

# Palettes sampled by eye from the printed card -------------------------------
PLUM = dict(deep=hexc('#191524'), mid=hexc('#37314c'), light=hexc('#78769a'),
            hi=hexc('#adb0c9'), core=hexc('#120f19'),
            stamen=hexc('#c9973c'), anther=hexc('#efcb6d'))
PEACH = dict(deep=hexc('#a84e27'), mid=hexc('#d9844f'), light=hexc('#f0b68a'),
             hi=hexc('#fadcc4'), core=hexc('#8a3a1b'),
             stamen=hexc('#c0732f'), anther=hexc('#e7a157'))
BLUSH = dict(deep=hexc('#a8625a'), mid=hexc('#d39a8f'), light=hexc('#ecc7bd'),
             hi=hexc('#f9e8e2'), core=hexc('#844842'),
             stamen=hexc('#c99545'), anther=hexc('#e8bf6a'))
FROND = dict(base=hexc('#1c1523'), tip=hexc('#463a52'), stem=hexc('#221a29'))
FROND_SOFT = dict(base=hexc('#4a3f5c'), tip=hexc('#8b80a0'), stem=hexc('#4a3f5c'))
GOLD = dict(base=hexc('#a77d3c'), tip=hexc('#e2c68f'), vein=hexc('#7d5d27'),
            stem=hexc('#8f6d33'))
SAGE = dict(base=hexc('#6b6650'), tip=hexc('#b4ad8b'), vein=hexc('#4f4b39'),
            stem=hexc('#625d47'))
GOLD_DOT = hexc('#c3994a')


def _circle(r, n=16, v=0.7):
    return [(math.cos(2 * math.pi * i / n) * r, math.sin(2 * math.pi * i / n) * r, v)
            for i in range(n)]


def _crescent(r_out, r_in, a0, a1, shift, n=18):
    """Band between an outer arc and a shifted inner arc (a cupped petal rim)."""
    am = (a0 + a1) / 2
    sx, sy = math.cos(am) * shift, math.sin(am) * shift
    outer = [(math.cos(a0 + (a1 - a0) * i / n) * r_out,
              math.sin(a0 + (a1 - a0) * i / n) * r_out, 0.6) for i in range(n + 1)]
    inner = [(sx + math.cos(a1 - (a1 - a0) * i / n) * r_in,
              sy + math.sin(a1 - (a1 - a0) * i / n) * r_in, 0.3) for i in range(n + 1)]
    return outer + inner


def flower(cv, cx, cy, R, pal, rot=0.0, tilt=0.88, style='peony', detail=1.0):
    """A watercolor peony/rose seen from the front.

    style 'peony': loose rings of large petals around a gold stamen boss.
    style 'rose' : tighter rings closing into a cupped spiral centre.
    """
    rng = cv.rng
    T = lambda pts: xform(pts, cx, cy, rot, 1.0, tilt)
    Tp = lambda x, y: T([(x, y, 1)])[0][:2]
    lay = max(10, int(24 * detail))

    if style == 'peony':
        rings = [(6, 1.00, 1.15, 1.00), (6, 0.84, 1.10, 0.75), (6, 0.66, 1.05, 0.5),
                 (5, 0.48, 1.0, 0.3)]
    else:
        rings = [(6, 1.00, 1.15, 1.0), (6, 0.82, 1.1, 0.72), (5, 0.64, 1.05, 0.45),
                 (5, 0.47, 1.0, 0.22)]

    for ri, (n, lf, wf, lt) in enumerate(rings):
        if ri > 0:   # soft shadow where the next ring sits on the previous one
            cv.wash(T(_circle(R * lf * 0.8)), pal['deep'], layers=10, alpha=0.06,
                    opacity=0.3 + 0.08 * ri, edge=0.15, var=0.18, grain=0.1)
        off = rng.uniform(0, 2 * math.pi)
        for k in range(n):
            ang = off + 2 * math.pi * k / n + rng.uniform(-0.22, 0.22)
            L = R * lf * rng.uniform(0.86, 1.06)
            W = L * wf * rng.uniform(0.9, 1.12)
            shp = petal_shape(L, W, notch=rng.uniform(0.0, 0.09), curl=rng.uniform(-0.1, 0.1),
                              ruffle=0.05, rng=rng)
            shp = [(x, y + R * 0.04, v) for (x, y, v) in shp]
            pts = T(place(shp, 0, 0, ang))
            base = Tp(0, 0)
            tip = Tp(math.cos(ang) * (L + R * 0.04), math.sin(ang) * (L + R * 0.04))
            tipcol = mix(pal['mid'], pal['light'], lt)
            color = ('linear', base, tip, [
                (0.0, pal['deep']),
                (0.45, mix(pal['deep'], tipcol, 0.55)),
                (0.88, tipcol),
                (1.0, mix(tipcol, pal['hi'], 0.55)),
            ])
            cv.wash(pts, color, layers=lay, alpha=0.085, var=0.11, edge=0.85,
                    edge_dark=0.3, edge_sigma=1.6)
            if lt > 0.3 and rng.random() < 0.55:   # light catching the curled rim
                rim = _crescent(L * 0.5, L * 0.42, -0.75, 0.75, -L * 0.06)
                rim = [(x + L * 0.5 + R * 0.04, y, v) for (x, y, v) in rim]
                cv.wash(T(xform(rim, 0, 0, ang)), pal['hi'], layers=8, alpha=0.08,
                        opacity=0.3, edge=0.3, var=0.1, edge_dark=0)

    if style == 'peony':
        core_r = R * 0.2
        cv.wash(T(_circle(core_r)), ('radial', Tp(0, 0), core_r * 1.1,
                                     [(0, pal['core']), (1, pal['deep'])]),
                layers=14, alpha=0.14, var=0.16, edge=0.4)
        for _ in range(int(60 * detail) + 10):
            a = rng.uniform(0, 2 * math.pi)
            r1 = R * rng.uniform(0.03, 0.08)
            r2 = R * rng.uniform(0.13, 0.3)
            a2 = a + rng.uniform(-0.3, 0.3)
            p1 = Tp(math.cos(a) * r1, math.sin(a) * r1)
            p2 = Tp(math.cos(a2) * r2, math.sin(a2) * r2)
            cv.stroke_line([p1, p2], pal['stamen'], 0.6, max(0.5, R * 0.005))
            cv.dot(p2[0], p2[1], R * rng.uniform(0.011, 0.02), pal['anther'], 0.92)
        for _ in range(16):
            a = rng.uniform(0, 2 * math.pi)
            r = R * rng.uniform(0.0, 0.06)
            p = Tp(math.cos(a) * r, math.sin(a) * r)
            cv.dot(p[0], p[1], R * 0.016, pal['stamen'], 0.85)
    else:
        # cupped centre: crescents spiralling inward, darkening as they close
        a = rng.uniform(0, 2 * math.pi)
        r = R * 0.36
        for i in range(7):
            span = rng.uniform(1.6, 2.4)
            col = mix(pal['mid'], pal['deep'], 0.25 + i * 0.1)
            cr = _crescent(r, r * 0.8, a, a + span, r * 0.22)
            cv.wash(T(cr), col, layers=12, alpha=0.13, var=0.08, edge=1.1, edge_dark=0.4)
            a += span * 0.62 + rng.uniform(0.2, 0.6)
            r *= 0.8
        cv.wash(T(_circle(R * 0.05)), pal['core'], layers=8, alpha=0.08, opacity=0.6,
                var=0.25, edge=0.3)


def bud(cv, x, y, ang, size, pal, sepal=FROND):
    """Closed bud pointing toward `ang` with two sepals."""
    rng = cv.rng
    for k in (0, 2, 1):
        a = ang + (k - 1) * 0.32
        L = size * (1.0 - abs(k - 1) * 0.15)
        shp = petal_shape(L, size * 0.75, base_w=0.4)
        pts = place(shp, x, y, a)
        tip = (x + math.cos(a) * L, y + math.sin(a) * L)
        cv.wash(pts, ('linear', (x, y), tip, [(0, pal['deep']), (0.6, pal['mid']),
                                              (1, pal['light'])]),
                layers=14, alpha=0.11, var=0.1, edge=0.9)
    for s in (-1, 1, 0):
        L = size * (0.5 if s else 0.36)
        lp = place(leaf_shape(L, size * 0.17, bend=-s * 0.12), x, y, ang + s * 0.42)
        cv.wash(lp, ('linear', (x, y), (x + math.cos(ang) * L, y + math.sin(ang) * L),
                     [(0, sepal['base']), (1, sepal['tip'])]),
                layers=10, alpha=0.1, opacity=0.85, var=0.1, edge=0.5)


def leaf(cv, x, y, ang, length, width, pal, vein=True, layers=16, bend=0.0, alpha=0.1):
    rng = cv.rng
    shp = leaf_shape(length, width, asym=rng.uniform(-0.15, 0.15), bend=bend)
    pts = place(shp, x, y, ang)
    tip = (x + math.cos(ang) * length, y + math.sin(ang) * length)
    cv.wash(pts, ('linear', (x, y), tip, [(0, pal['base']), (0.55, mix(pal['base'], pal['tip'], 0.55)),
                                          (1, pal['tip'])]),
            layers=layers, alpha=alpha, var=0.09, edge=0.8, edge_dark=0.25)
    if vein and 'vein' in pal:
        mid = place([(bend * length * t * t * 0.5, length * t) for t in (0.02, 0.4, 0.75, 0.93)],
                    x, y, ang)
        cv.stroke_line(mid, pal['vein'], 0.28, max(0.5, width * 0.045))


def frond(cv, x0, y0, ang, length, bend, pal=FROND, n=13, leaf_len=0.34, leaf_ratio=0.17,
          spread=0.95, start=0.1, layers=10, wobble=0.004):
    """Palm-like frond: curving stem with narrow leaflets on both sides."""
    rng = cv.rng
    pts = curve_from(x0, y0, ang, length, bend, n=60, wobble=wobble, rng=rng)
    cv.wash(ribbon(pts, length * 0.016, length * 0.004), pal['stem'], layers=4,
            alpha=0.3, var=0.01, base_depth=1, layer_depth=1, edge=0.2)
    for i in range(n):
        s = start + (1 - start) * i / (n - 1)
        idx = min(len(pts) - 1, int(s * (len(pts) - 1)))
        px, py = pts[idx]
        t = tangent(pts, idx)
        for side in (-1, 1):
            a = t + side * spread * (1 - 0.5 * s) + rng.uniform(-0.1, 0.1)
            L = length * leaf_len * (1 - 0.7 * s ** 1.3) * rng.uniform(0.85, 1.1)
            shp = leaf_shape(L, L * leaf_ratio * rng.uniform(0.85, 1.15),
                             asym=rng.uniform(-0.2, 0.2), bend=side * rng.uniform(0.02, 0.1))
            lp = place(shp, px, py, a)
            tip = (px + math.cos(a) * L, py + math.sin(a) * L)
            cv.wash(lp, ('linear', (px, py), tip, [(0, pal['base']), (1, pal['tip'])]),
                    layers=layers, alpha=0.13, var=0.08, edge=0.6, edge_dark=0.2)
    a = tangent(pts, len(pts) - 1)
    L = length * leaf_len * 0.4
    lp = place(leaf_shape(L, L * leaf_ratio * 1.2), pts[-1][0], pts[-1][1], a)
    cv.wash(lp, pal['base'], layers=layers, alpha=0.13, var=0.08, edge=0.6)
    return pts


def sprig(cv, x0, y0, ang, length, bend, pal=GOLD, n=7, leaf_len=0.3, leaf_ratio=0.34,
          spread=0.7, start=0.12, layers=16, wobble=0.004):
    """Eucalyptus/willow-like sprig: alternate lanceolate leaves."""
    rng = cv.rng
    pts = curve_from(x0, y0, ang, length, bend, n=50, wobble=wobble, rng=rng)
    cv.wash(ribbon(pts, length * 0.012, length * 0.004), pal['stem'], layers=4,
            alpha=0.3, var=0.01, base_depth=1, layer_depth=1, edge=0.2)
    side = rng.choice((-1, 1))
    for i in range(n):
        s = start + (1 - start) * i / max(1, n - 1)
        idx = min(len(pts) - 1, int(s * (len(pts) - 1)))
        px, py = pts[idx]
        t = tangent(pts, idx)
        a = t + side * spread * rng.uniform(0.8, 1.15)
        L = length * leaf_len * (1 - 0.45 * s) * rng.uniform(0.85, 1.1)
        leaf(cv, px, py, a, L, L * leaf_ratio, pal, layers=layers,
             bend=side * rng.uniform(0.0, 0.08))
        side = -side
    a = tangent(pts, len(pts) - 1)
    L = length * leaf_len * 0.6
    leaf(cv, pts[-1][0], pts[-1][1], a, L, L * leaf_ratio, pal, layers=layers)
    return pts


def splatter(cv, x, y, spread, count, rgb=GOLD_DOT, rmin=0.7, rmax=2.8, alpha=(0.35, 0.85)):
    rng = cv.rng
    for _ in range(count):
        d = abs(rng.gauss(0, spread))
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(rmin, rmax) * (1 if rng.random() > 0.12 else 1.9)
        cv.dot(x + math.cos(a) * d, y + math.sin(a) * d, r, rgb, rng.uniform(*alpha))


def berry_stem(cv, x0, y0, ang, length, bend, rgb=GOLD_DOT, stem=GOLD['stem'], count=7):
    """Fine stem with small gold berries — the card's golden filler."""
    rng = cv.rng
    pts = curve_from(x0, y0, ang, length, bend, n=30)
    cv.stroke_line(pts, stem, 0.7, max(0.7, length * 0.007))
    for i in range(count):
        s = 0.3 + 0.7 * i / max(1, count - 1)
        idx = min(len(pts) - 1, int(s * (len(pts) - 1)))
        px, py = pts[idx]
        t = tangent(pts, idx) + rng.choice((-1, 1)) * rng.uniform(0.5, 1.1)
        L = length * rng.uniform(0.06, 0.12)
        ex, ey = px + math.cos(t) * L, py + math.sin(t) * L
        cv.stroke_line([(px, py), (ex, ey)], stem, 0.6, max(0.5, length * 0.004))
        cv.dot(ex, ey, length * rng.uniform(0.012, 0.02), rgb, 0.9)
