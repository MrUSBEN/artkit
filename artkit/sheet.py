"""Contact sheets (labelled grid for a quick visual check) and atlas packing (sprite sheet + JSON)."""
import json, os
from PIL import Image, ImageDraw, ImageFont


def _font(sz=12):
    for f in ('/usr/share/fonts/opentype/inter/Inter-Bold.otf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def contact_sheet(items, path, cols=8, cell=None, bg=(88, 130, 150), max_px=150):
    """items: [(name, PIL image)]. Each is scaled (nearest for small pixel art, smooth for big) to fit a cell."""
    ims = []
    for n, im in items:
        k = max_px / max(im.size)
        if k >= 1: k = max(1, int(k)); im = im.resize((im.width * k, im.height * k), Image.NEAREST)
        else: im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
        ims.append((n, im))
    cw = cell[0] if cell else max(i.width for _, i in ims) + 20
    ch = cell[1] if cell else max(i.height for _, i in ims) + 34
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * cw, rows * ch), bg); d = ImageDraw.Draw(S); F = _font(12)
    for i, (n, im) in enumerate(ims):
        x, y = (i % cols) * cw, (i // cols) * ch
        S.paste(im, (x + (cw - im.width) // 2, y + 6 + (ch - 34 - im.height) // 2), im)
        d.text((x + cw // 2, y + ch - 14), n, font=F, fill=(255, 255, 255), anchor='mm')
    S.save(path); return path


def pack_atlas(items, png_path, json_path, max_w=1024, pad=2):
    """Shelf-pack sprites into one PNG + JSON {name: {x,y,w,h}} (also writes a TexturePacker-style 'frames' key)."""
    items = sorted(items, key=lambda t: -t[1].height)
    x = y = rowh = 0; place = {}; W = 0
    for n, im in items:
        if x + im.width > max_w: x = 0; y += rowh + pad; rowh = 0
        place[n] = (x, y); x += im.width + pad; rowh = max(rowh, im.height); W = max(W, x)
    H = y + rowh
    A = Image.new('RGBA', (max(1, W), max(1, H)), (0, 0, 0, 0))
    for n, im in items: A.paste(im, place[n])
    A.save(png_path)
    fr = {n: dict(x=place[n][0], y=place[n][1], w=im.width, h=im.height) for n, im in items}
    json.dump(dict(image=os.path.basename(png_path), size=dict(w=A.width, h=A.height), sprites=fr,
                   frames={n: dict(frame=v, sourceSize=dict(w=v['w'], h=v['h'])) for n, v in fr.items()}), open(json_path, 'w'), indent=1)
    return A
