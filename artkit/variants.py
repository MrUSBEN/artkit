"""Palette-swap variants and hue-shifted ramps (ideas borrowed from pxl's base+swap and shades()).
    with swap(purple2='carred'): img = gangster()      # temporarily point palette 'purple2' at another palette
    variant(fn, purple2='carred')                       # -> zero-arg function, for use in ALL = {...}
    make_pal('mint', (120, 220, 170))                   # registers PALS['mint'] = (base, shadow, highlight), hue-shifted
"""
import colorsys, contextlib
from artkit.core import PALS, K


def shades(rgb, n=3, shadow_hue=-18, light_hue=14, sat=1.0):
    """Hue-shifted ramp dark->light: shadows drift cooler/more saturated, lights warmer. Returns n colours."""
    h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in rgb]); out = []
    for i in range(n):
        t = (i / (n - 1) if n > 1 else .5) * 2 - 1                 # -1 (dark) .. +1 (light)
        hh = (h + (shadow_hue if t < 0 else light_hue) * abs(t) / 360) % 1
        ss = min(1, s * (1 + .18 * (-t if t < 0 else -t * .6)) * sat); vv = min(1, max(0, v * (1 + .38 * t if t < 0 else 1 + .22 * t)))
        out.append(tuple(int(round(c * 255)) for c in colorsys.hsv_to_rgb(hh, ss, vv)))
    return out


def make_pal(name, rgb):
    d, b, l = shades(rgb, 3); PALS[name] = (K(*b), K(*d), K(*l)); return PALS[name]


@contextlib.contextmanager
def swap(**m):
    """m: {palette_name: palette_name_or_triple}. Restored on exit."""
    old = {k: PALS[k] for k in m}
    try:
        for k, v in m.items(): PALS[k] = PALS[v] if isinstance(v, str) else v
        yield
    finally: PALS.update(old)


def variant(fn, **m):
    def f():
        with swap(**m): return fn()
    return f
