"""Draws the app icons: a glowing amber handset on the deep night-indigo background.

The glyph is the very same 24x24 handset path the page uses for the die texture and
the pips, so every phone on the site is the same shape. No image libraries are
available here, so the path is flattened and scanline-filled by hand, and the PNG is
assembled straight from zlib.

    python tools/make-icons.py
"""

import math
import re
import struct
import zlib
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "icons"

PHONE_PATH = (
    "M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 "
    "1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 "
    "0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 "
    "1.02l-2.2 2.2z"
)
VIEWBOX = 24.0

BG_CENTER = (0x2E, 0x1D, 0x40)
BG_EDGE = (0x0A, 0x06, 0x13)
GLOW = (0xF4, 0xB9, 0x42)
GLYPH_TOP = (0xFF, 0xEC, 0xCB)
GLYPH_BOTTOM = (0xE8, 0xA2, 0x2E)

SUBROWS = 4          # vertical supersampling; horizontal coverage is exact
CURVE_STEPS = 18     # segments per cubic


def flatten(d):
    """SVG path -> list of polygons (the handset needs M, c, l, V, h and z)."""
    tokens = re.findall(r"[MmLlHhVvCcZz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    polys, pts = [], []
    i, cmd = 0, None
    x = y = 0.0

    def num():
        nonlocal i
        v = float(tokens[i])
        i += 1
        return v

    while i < len(tokens):
        if re.match(r"[A-Za-z]", tokens[i]):
            cmd = tokens[i]
            i += 1
            if cmd in "Zz":
                if pts:
                    polys.append(pts)
                    pts = []
                continue
        rel = cmd.islower()
        if cmd in "Mm":
            if pts:
                polys.append(pts)
            x, y = (x + num(), y + num()) if rel else (num(), num())
            pts = [(x, y)]
            cmd = "l" if rel else "L"
        elif cmd in "Ll":
            x, y = (x + num(), y + num()) if rel else (num(), num())
            pts.append((x, y))
        elif cmd in "Hh":
            x = x + num() if rel else num()
            pts.append((x, y))
        elif cmd in "Vv":
            y = y + num() if rel else num()
            pts.append((x, y))
        elif cmd in "Cc":
            ox, oy = x, y
            x1, y1 = (ox + num(), oy + num()) if rel else (num(), num())
            x2, y2 = (ox + num(), oy + num()) if rel else (num(), num())
            x, y = (ox + num(), oy + num()) if rel else (num(), num())
            for s in range(1, CURVE_STEPS + 1):
                t = s / CURVE_STEPS
                u = 1 - t
                pts.append((
                    u * u * u * ox + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t * t * t * x,
                    u * u * u * oy + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t * t * t * y,
                ))
        else:
            raise ValueError("unsupported path command " + cmd)
    if pts:
        polys.append(pts)
    return polys


def coverage(size, scale):
    """Antialiased glyph mask. scale is the share of the icon the glyph spans."""
    span = size * scale
    off = (size - span) / 2.0
    edges = []
    for poly in flatten(PHONE_PATH):
        for k in range(len(poly)):
            ax, ay = poly[k]
            bx, by = poly[(k + 1) % len(poly)]
            ax, ay = off + ax / VIEWBOX * span, off + ay / VIEWBOX * span
            bx, by = off + bx / VIEWBOX * span, off + by / VIEWBOX * span
            if ay != by:
                edges.append((ax, ay, bx, by))

    cov = [[0.0] * size for _ in range(size)]
    weight = 1.0 / SUBROWS
    for j in range(size):
        row = cov[j]
        for s in range(SUBROWS):
            sy = j + (s + 0.5) / SUBROWS
            xs = sorted(
                ax + (sy - ay) * (bx - ax) / (by - ay)
                for ax, ay, bx, by in edges
                if (ay <= sy < by) or (by <= sy < ay)
            )
            for a, b in zip(xs[0::2], xs[1::2]):
                a, b = max(a, 0.0), min(b, float(size))
                if b <= a:
                    continue
                first, last = int(a), min(int(b), size - 1)
                if first == last:
                    row[first] += (b - a) * weight
                else:
                    row[first] += (first + 1 - a) * weight
                    for x in range(first + 1, last):
                        row[x] += weight
                    row[last] += (b - last) * weight
    return cov


def blur(src, size, radius, passes=3):
    """Cheap separable box blur, used to bloom the amber glow around the glyph."""
    buf = [row[:] for row in src]
    for _ in range(passes):
        for j in range(size):
            row, out = buf[j], [0.0] * size
            acc = 0.0
            for x in range(size + radius):
                if x < size:
                    acc += row[x]
                if x - 2 * radius - 1 >= 0:
                    acc -= row[x - 2 * radius - 1]
                if x >= radius:
                    out[x - radius] = acc / (2 * radius + 1)
            buf[j] = out
        for x in range(size):
            col = [buf[j][x] for j in range(size)]
            acc = 0.0
            for j in range(size + radius):
                if j < size:
                    acc += col[j]
                if j - 2 * radius - 1 >= 0:
                    acc -= col[j - 2 * radius - 1]
                if j >= radius:
                    buf[j - radius][x] = acc / (2 * radius + 1)
    return buf


def mix(a, b, t):
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def render(size, scale):
    cov = coverage(size, scale)
    glow = blur(cov, size, max(1, size // 16))
    peak = max(max(row) for row in glow) or 1.0
    rows = []
    for j in range(size):
        y = (j + 0.5) / size * 2 - 1
        row = bytearray()
        for i in range(size):
            x = (i + 0.5) / size * 2 - 1
            base = mix(BG_CENTER, BG_EDGE, (math.hypot(x, y) / 1.25) ** 1.4)
            bg = mix(base, GLOW, min(0.85, glow[j][i] / peak * 1.5))
            fill = mix(GLYPH_TOP, GLYPH_BOTTOM, (y / scale + 0.9) / 1.8)
            for c in mix(bg, fill, cov[j][i]):
                row.append(int(min(255.0, max(0.0, c)) + 0.5))
        rows.append(bytes(row))
    return rows


def write_png(path, rows):
    size = len(rows)
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)
    print(path.name, size, len(png), "bytes")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    write_png(OUT / "icon-512.png", render(512, 0.62))
    write_png(OUT / "icon-192.png", render(192, 0.62))
    write_png(OUT / "apple-touch-icon.png", render(180, 0.62))
    write_png(OUT / "favicon-32.png", render(32, 0.68))
    write_png(OUT / "icon-maskable-512.png", render(512, 0.45))


if __name__ == "__main__":
    main()
