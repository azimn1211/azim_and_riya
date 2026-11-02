"""Procedural watercolor painting primitives (pycairo + numpy).

Every wash is a base polygon that is recursively deformed, then re-deformed
and stacked dozens of times at low opacity into a private density map.  From
that density we derive real watercolor behaviour before compositing:

* edge darkening  - pigment pools at the wet edge: density - blur(density)
* granulation     - fine noise modulates the pigment that settles
* blooms          - low-frequency noise varies the wash strength
"""
import math
import random

import cairo
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def xform(pts, cx=0.0, cy=0.0, rot=0.0, sx=1.0, sy=1.0):
    """Scale, rotate, then translate points (keeps a 3rd 'variance' coord)."""
    ca, sa = math.cos(rot), math.sin(rot)
    out = []
    for p in pts:
        x, y = p[0] * sx, p[1] * sy
        q = (cx + x * ca - y * sa, cy + x * sa + y * ca)
        out.append(q + tuple(p[2:]))
    return out


class Canvas:
    """Transparent painting surface rendered at `ss`x supersampling."""

    def __init__(self, w, h, ss=2, seed=1):
        self.w, self.h, self.ss = w, h, ss
        self.W, self.H = w * ss, h * ss
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.W, self.H)
        self.ctx = cairo.Context(self.surf)
        self.ctx.scale(ss, ss)
        self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        self.rng = random.Random(seed)
        nrng = np.random.default_rng(seed)
        fine = gaussian_filter(nrng.standard_normal((self.H, self.W)).astype(np.float32), 0.9 * ss)
        self.fine = fine / (np.abs(fine).max() + 1e-6)
        low = gaussian_filter(nrng.standard_normal((self.H // 4 + 1, self.W // 4 + 1)).astype(np.float32), 6)
        low = np.kron(low, np.ones((4, 4), np.float32))[:self.H, :self.W]
        self.low = low / (np.abs(low).max() + 1e-6)

    # ---- polygon deformation -------------------------------------------
    def _subdivide(self, pts, var):
        rng = self.rng
        out = []
        n = len(pts)
        for i in range(n):
            x1, y1, v1 = pts[i][:3]
            x2, y2, v2 = pts[(i + 1) % n][:3]
            out.append((x1, y1, v1))
            seg = math.hypot(x2 - x1, y2 - y1)
            v = (v1 + v2) / 2
            sd = seg * var * v
            out.append(((x1 + x2) / 2 + rng.gauss(0, sd),
                        (y1 + y2) / 2 + rng.gauss(0, sd),
                        v * rng.uniform(0.85, 1.15)))
        return out

    def deform(self, pts, depth, var):
        pts = [p if len(p) >= 3 else (p[0], p[1], 1.0) for p in pts]
        for _ in range(depth):
            pts = self._subdivide(pts, var)
        return pts

    # ---- colour fields ----------------------------------------------------
    def _color_field(self, color, x0, y0, w, h):
        """Return (h, w, 3) rgb for a solid, linear or radial colour spec."""
        if not isinstance(color[0], str):
            return np.broadcast_to(np.array(color, np.float32), (h, w, 3))
        ys, xs = np.mgrid[y0:y0 + h, x0:x0 + w].astype(np.float32)
        xs /= self.ss
        ys /= self.ss
        kind = color[0]
        if kind == 'linear':
            (ax, ay), (bx, by), stops = color[1], color[2], color[3]
            dx, dy = bx - ax, by - ay
            t = ((xs - ax) * dx + (ys - ay) * dy) / max(dx * dx + dy * dy, 1e-6)
        else:  # radial
            (cx, cy), r, stops = color[1], color[2], color[3]
            t = np.hypot(xs - cx, ys - cy) / max(r, 1e-6)
        t = np.clip(t, 0, 1)
        offs = np.array([s[0] for s in stops], np.float32)
        cols = np.array([s[1] for s in stops], np.float32)
        out = np.empty((h, w, 3), np.float32)
        for k in range(3):
            out[..., k] = np.interp(t, offs, cols[:, k])
        return out

    # ---- washes -----------------------------------------------------------
    def wash(self, pts, color, layers=30, alpha=0.07, var=0.15, base_depth=2,
             layer_depth=2, edge=0.9, edge_sigma=1.8, edge_dark=0.35, opacity=1.0,
             grain=0.18, bloom=0.18):
        base = self.deform(pts, base_depth, var)
        polys = [self.deform(base, layer_depth, var) for _ in range(layers)]
        ss = self.ss
        pad = int(edge_sigma * ss * 3) + 4
        allx = [p[0] for poly in polys for p in poly]
        ally = [p[1] for poly in polys for p in poly]
        x0 = max(0, int(min(allx) * ss) - pad)
        y0 = max(0, int(min(ally) * ss) - pad)
        x1 = min(self.W, int(max(allx) * ss) + pad)
        y1 = min(self.H, int(max(ally) * ss) + pad)
        w, h = x1 - x0, y1 - y0
        if w <= 2 or h <= 2:
            return

        dens = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
        dc = cairo.Context(dens)
        dc.translate(-x0, -y0)
        dc.scale(ss, ss)
        for poly in polys:
            dc.new_path()
            dc.move_to(poly[0][0], poly[0][1])
            for p in poly[1:]:
                dc.line_to(p[0], p[1])
            dc.close_path()
            dc.set_source_rgba(0, 0, 0, alpha)
            dc.fill()
        dens.flush()
        D = np.frombuffer(dens.get_data(), np.uint8).reshape(h, dens.get_stride())[:, :w]
        D = D.astype(np.float32) / 255.0

        Eg = np.clip(D - gaussian_filter(D, edge_sigma * ss), 0, None)
        Dmax = max(D.max(), 1e-6)
        A = D / Dmax * opacity
        A = A * (1 + bloom * self.low[y0:y1, x0:x1]) * (1 + grain * self.fine[y0:y1, x0:x1])
        A = np.clip(A + Eg * edge, 0, 1)

        rgb = self._color_field(color, x0, y0, w, h)
        en = np.clip(Eg * 4, 0, 1)[..., None]
        rgb = rgb * (1 - edge_dark * en)

        prem = np.empty((h, w, 4), np.float32)
        prem[..., :3] = rgb * A[..., None]
        prem[..., 3] = A
        self._composite(prem, x0, y0)

    def _composite(self, prem, x0, y0):
        h, w = prem.shape[:2]
        tmp = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        stride = tmp.get_stride()
        arr = np.zeros((h, stride // 4, 4), np.uint8)
        arr[:, :w] = (np.clip(prem[..., [2, 1, 0, 3]], 0, 1) * 255 + 0.5).astype(np.uint8)
        data = tmp.get_data()
        data[:] = arr.tobytes()
        tmp.mark_dirty()
        c = self.ctx
        c.save()
        c.identity_matrix()
        c.set_source_surface(tmp, x0, y0)
        c.paint()
        c.restore()

    # ---- line work ------------------------------------------------------
    def stroke_line(self, pts, rgb, alpha, width):
        c = self.ctx
        c.new_path()
        c.move_to(pts[0][0], pts[0][1])
        for p in pts[1:]:
            c.line_to(p[0], p[1])
        c.set_source_rgba(*rgb, alpha)
        c.set_line_width(width)
        c.stroke()

    def dot(self, x, y, r, rgb, alpha):
        c = self.ctx
        c.new_path()
        c.arc(x, y, r, 0, 2 * math.pi)
        c.set_source_rgba(*rgb, alpha)
        c.fill()

    # ---- export ---------------------------------------------------------
    def to_image(self, bleed=0.25):
        self.surf.flush()
        stride = self.surf.get_stride()
        buf = np.frombuffer(self.surf.get_data(), np.uint8).reshape(self.H, stride // 4, 4)[:, :self.W]
        prem = buf[..., [2, 1, 0, 3]].astype(np.float32) / 255.0
        if bleed:
            soft = np.stack([gaussian_filter(prem[..., k], 1.2 * self.ss) for k in range(4)], -1)
            prem = prem + soft * bleed * (1 - prem[..., 3:4])
        prem = np.clip(prem, 0, 1)
        img = Image.frombytes('RGBa', (self.W, self.H), (prem * 255 + 0.5).astype(np.uint8).tobytes())
        if self.ss != 1:
            img = img.resize((self.w, self.h), Image.LANCZOS)
        return img.convert('RGBA')


# ---------------------------------------------------------------------------
# Shape outlines (local coordinates, then positioned with xform)
# ---------------------------------------------------------------------------

def petal_shape(length, width, n=22, base_w=0.2, notch=0.0, curl=0.0, ruffle=0.0, rng=None):
    """Rounded petal with base at origin and tip at (0, length)."""
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        k = 0.5 - math.cos(th) / 2
        x = math.sin(th) * width / 2
        x *= base_w + (1 - base_w) * math.sin(min(1.0, k * 1.3) * math.pi / 2) ** 0.75
        y = k * length
        if notch:
            y -= notch * length * math.exp(-((th - math.pi) / 0.4) ** 2)
        if ruffle and rng is not None and k > 0.6:
            y += rng.uniform(-ruffle, ruffle) * length * (k - 0.6)
        x += curl * length * k * k
        pts.append((x, y, 0.2 + 1.0 * k ** 1.5))
    return pts


def place(shape, x, y, ang, sx=1.0, sy=1.0):
    """Rotate a local shape whose axis is +y so that it points along `ang`."""
    return xform(shape, x, y, ang - math.pi / 2, sx, sy)


def leaf_shape(length, width, n=24, asym=0.0, bend=0.0):
    """Lanceolate leaf: base at origin, pointed tip at (0, length)."""
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        k = 0.5 - math.cos(th) / 2
        side = 1 if th < math.pi else -1
        prof = math.sin(math.pi * min(1.0, k ** 0.8)) ** 0.85
        x = side * prof * width / 2 * (1 + asym * side)
        x += bend * length * k * k
        pts.append((x, k * length, 0.3 + 0.9 * math.sin(math.pi * k)))
    return pts


def curve_from(x0, y0, ang, length, bend, n=40, wobble=0.0, rng=None):
    pts = [(x0, y0)]
    x, y, a = x0, y0, ang
    step = length / n
    for i in range(n):
        a += bend / n + (rng.gauss(0, wobble) if (rng and wobble) else 0)
        x += math.cos(a) * step
        y += math.sin(a) * step
        pts.append((x, y))
    return pts


def tangent(pts, i):
    j = min(i + 1, len(pts) - 1)
    k = max(i - 1, 0)
    return math.atan2(pts[j][1] - pts[k][1], pts[j][0] - pts[k][0])


def ribbon(pts, w0, w1):
    """Polygon around a polyline whose width tapers from w0 to w1."""
    left, right = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        t = i / (n - 1)
        w = w0 + (w1 - w0) * t
        a = tangent(pts, i) + math.pi / 2
        left.append((p[0] + math.cos(a) * w / 2, p[1] + math.sin(a) * w / 2, 0.15))
        right.append((p[0] - math.cos(a) * w / 2, p[1] - math.sin(a) * w / 2, 0.15))
    return left + right[::-1]
