"""Tiny pixel-art framework: draw shapes at SSx supersample with hard edges, majority-vote down to the sprite grid,
add exact-pixel details, then a 1px outline. Everything in design units = final sprite pixels."""
import math, numpy as np
from PIL import Image, ImageDraw
SS = 8
OUT = (58, 36, 44)
PAD = 1


def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cr_dense(pts, n=12):
    P = np.array(pts, float); P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]]); out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2]); return np.array(out)


class C:
    def __init__(s, w, h, outline=OUT):
        s.w, s.h, s.outline = w, h, outline
        s.W, s.H = (w + 2 * PAD) * SS, (h + 2 * PAD) * SS
        s.im = Image.new('RGBA', (s.W, s.H), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
        s.stack = []; s.post = []

    # -- coordinate helpers
    def P(s, x, y): return ((x + PAD) * SS, (y + PAD) * SS)
    def pts(s, p): return [s.P(x, y) for x, y in p]

    # -- primitives (colour may be None to skip)
    def ell(s, cx, cy, rx, ry, col): s.d.ellipse([*s.P(cx - rx, cy - ry), *s.P(cx + rx, cy + ry)], fill=tuple(col) + (255,))
    def poly(s, p, col): s.d.polygon(s.pts(p), fill=tuple(col) + (255,))
    def rect(s, x0, y0, x1, y1, col):
        a, b = s.P(x0, y0), s.P(x1, y1)
        if b[0] - 1 < a[0] or b[1] - 1 < a[1]: return
        s.d.rectangle([*a, b[0] - 1, b[1] - 1], fill=tuple(col) + (255,))
    def rrect(s, x0, y0, x1, y1, r, col):
        a, b = s.P(x0, y0), s.P(x1, y1)
        if b[0] - 1 < a[0] or b[1] - 1 < a[1]: return
        s.d.rounded_rectangle([a[0], a[1], b[0] - 1, b[1] - 1], radius=r * SS, fill=tuple(col) + (255,))
    def line(s, p, w, col):
        d = cr_dense(p) if len(p) > 2 else np.array([p[0], p[1]], float)
        for a, b in zip(d, d[1:]): s.d.line([*s.P(*a), *s.P(*b)], fill=tuple(col) + (255,), width=max(1, int(w * SS)))
        for q in (d[0], d[-1]): s.ell(q[0], q[1], w / 2, w / 2, col)
    def stroke(s, p, radii, col):
        d = cr_dense(p, 14); r = np.interp(np.linspace(0, 1, len(d)), np.linspace(0, 1, len(radii)), radii)
        for q, rr in zip(d, r): s.ell(q[0], q[1], rr, rr, col)
    def px(s, x, y, col): s.post.append((int(x), int(y), tuple(col)))

    # -- clipping: draw into a temp layer masked by a shape
    def clip(s, maskfn):
        old = (s.im, s.d)
        s.im = Image.new('RGBA', old[0].size, (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im); maskfn(s)
        mask = s.im.split()[3]
        s.stack.append((old, mask)); s.im = Image.new('RGBA', old[0].size, (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)

    def end(s):
        (base_im, base_d), mask = s.stack.pop()
        layer = s.im; a = np.minimum(np.array(layer.split()[3]), np.array(mask)); layer.putalpha(Image.fromarray(a))
        base_im.alpha_composite(layer); s.im, s.d = base_im, ImageDraw.Draw(base_im)

    def shaded(s, shape, base, dark, light=None, shift=(-0.14, -0.14), hl=()):
        """shape(c, dx, dy, col): draws the silhouette. Lower-right crescent is the dark colour."""
        shape(s, 0, 0, dark)
        s.clip(lambda c: shape(c, 0, 0, (0, 0, 0)))
        sx, sy = shift; shape(s, sx * s.w, sy * s.h, base)
        if light:
            for (cx, cy, rx, ry) in hl: s.ell(cx, cy, rx, ry, light)
        s.end()

    # -- finalise
    def finish(s, outline=True):
        a = np.array(s.im); h, w = s.H // SS, s.W // SS
        blk = a.reshape(h, SS, w, SS, 4).transpose(0, 2, 1, 3, 4).reshape(h, w, SS * SS, 4)
        out = np.zeros((h, w, 4), np.uint8)
        for y in range(h):
            for x in range(w):
                b = blk[y, x]; opaque = b[:, 3] > 128
                if opaque.sum() * 2 < len(b): continue
                cols, cnt = np.unique(b[opaque][:, :3], axis=0, return_counts=True)
                out[y, x, :3] = cols[cnt.argmax()]; out[y, x, 3] = 255
        for x, y, col in s.post:
            xx, yy = x + PAD, y + PAD
            if 0 <= xx < w and 0 <= yy < h and out[yy, xx, 3]: out[yy, xx, :3] = col
        if outline and s.outline is not None:
            op = out[..., 3] > 0; edge = np.zeros_like(op)
            edge[1:] |= op[:-1]; edge[:-1] |= op[1:]; edge[:, 1:] |= op[:, :-1]; edge[:, :-1] |= op[:, 1:]
            edge &= ~op
            out[edge, :3] = s.outline; out[edge, 3] = 255
        return Image.fromarray(out)


# ---- shared palette ------------------------------------------------------------------------------
K = lambda *a: tuple(a)
PALS = dict(
    orange=(K(246, 150, 40), K(206, 96, 28), K(255, 204, 100)), apple=(K(220, 56, 56), K(158, 34, 48), K(250, 128, 116)),
    green=(K(150, 198, 72), K(98, 152, 56), K(204, 234, 124)), banana=(K(252, 218, 66), K(218, 164, 40), K(255, 244, 150)),
    berry=(K(234, 62, 76), K(172, 36, 58), K(255, 130, 126)), cherry=(K(196, 32, 60), K(128, 20, 48), K(244, 100, 108)),
    lemon=(K(255, 234, 76), K(228, 186, 44), K(255, 250, 170)), blue=(K(86, 96, 204), K(52, 58, 142), K(156, 166, 244)),
    grape=(K(146, 74, 176), K(98, 46, 130), K(196, 138, 218)), leaf=(K(88, 164, 70), K(52, 114, 54), K(140, 204, 100)),
    ice=(K(196, 234, 252), K(132, 190, 230), K(244, 253, 255)), metal=(K(176, 184, 196), K(122, 130, 148), K(226, 232, 240)),
    dmetal=(K(112, 120, 136), K(70, 78, 94), K(158, 166, 182)), wood=(K(198, 130, 70), K(150, 90, 48), K(236, 180, 108)),
    dwood=(K(142, 84, 46), K(104, 60, 36), K(184, 118, 68)), cream=(K(248, 232, 198), K(222, 196, 152), K(255, 248, 228)),
    glass=(K(214, 236, 246), K(156, 194, 214), K(255, 255, 255)), bill=(K(94, 172, 82), K(58, 122, 62), K(152, 216, 122)),
    gold=(K(255, 204, 64), K(214, 150, 36), K(255, 240, 150)), brown=(K(110, 68, 40), K(78, 46, 30), K(150, 100, 64)),
    white=(K(250, 250, 252), K(206, 212, 224), K(255, 255, 255)), red=(K(220, 70, 60), K(160, 44, 48), K(250, 130, 110)),
    teal=(K(92, 140, 150), K(62, 100, 116), K(134, 184, 190)), kiwi=(K(142, 192, 62), K(96, 150, 48), K(196, 232, 112)),
    melon=(K(238, 74, 88), K(184, 44, 66), K(255, 138, 140)), pink=(K(244, 120, 160), K(196, 80, 124), K(255, 176, 200)),
    purple=(K(150, 80, 190), K(104, 52, 140), K(204, 150, 226)),
)
