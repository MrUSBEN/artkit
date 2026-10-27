"""Animation export. A clip is a list of frames; a frame is a PIL image or (image, dx, dy) for an offset.
All frames are placed on one fixed canvas (bottom-centre anchored) so nothing jitters.
Helpers build clips from a finished sprite (works in every style): bob, squash, sway, flash."""
import json, math, os
from PIL import Image


def _place(frames, pad=0):
    fr = [(f, 0, 0) if isinstance(f, Image.Image) else f for f in frames]
    W = max(f[0].width + abs(f[1]) * 2 for f in fr) + pad * 2; H = max(f[0].height + abs(f[2]) * 2 for f in fr) + pad * 2
    out = []
    for im, dx, dy in fr:
        c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c.alpha_composite(im, ((W - im.width) // 2 + dx, H - im.height - pad + dy)); out.append(c)
    return out


def save_clip(frames, out_base, fps=8, scale=1):
    """Writes <out_base>.gif, <out_base>_strip.png (frames side by side) and <out_base>.json. Returns frame list."""
    fr = _place(frames, pad=2)
    if scale > 1: fr = [f.resize((f.width * scale, f.height * scale), Image.NEAREST) for f in fr]
    W, H = fr[0].size; os.makedirs(os.path.dirname(out_base) or '.', exist_ok=True)
    strip = Image.new('RGBA', (W * len(fr), H), (0, 0, 0, 0))
    for i, f in enumerate(fr): strip.paste(f, (i * W, 0))
    strip.save(out_base + '_strip.png')
    pal = []                                              # GIF: composite on magenta key so edges stay clean, mark it transparent
    for f in fr:
        bg = Image.new('RGBA', f.size, (255, 0, 255, 255)); a = f.split()[3].point(lambda v: 255 if v > 127 else 0)
        bg.paste(f, mask=a); p = bg.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        mk = Image.new('P', f.size); m = a.point(lambda v: 255 if v == 0 else 0)
        p.paste(255, mask=m); pal.append(p)
    pal[0].save(out_base + '.gif', save_all=True, append_images=pal[1:], duration=int(1000 / fps), loop=0, transparency=255, disposal=2)
    json.dump(dict(image=os.path.basename(out_base) + '_strip.png', frame_w=W, frame_h=H, frames=len(fr), fps=fps), open(out_base + '.json', 'w'))
    return fr


def bob(im, n=6, amp=2):      return [(im, 0, -round(abs(math.sin(math.pi * i / n)) * amp)) for i in range(n)]
def sway(im, n=8, deg=6):     return [im.rotate(math.sin(2 * math.pi * i / n) * deg, resample=Image.NEAREST, expand=True) for i in range(n)]
def squash(im, n=6, amt=.12):
    out = []
    for i in range(n):
        k = math.sin(2 * math.pi * i / n) * amt; w, h = max(1, round(im.width * (1 - k))), max(1, round(im.height * (1 + k)))
        out.append(im.resize((w, h), Image.NEAREST))
    return out
def flash(*imgs, hold=1): return [i for i in imgs for _ in range(hold)]
