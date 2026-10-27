"""Export tiles to a Tiled (mapeditor.org) tileset + a demo map, plus a plain tileset PNG for any engine."""
import json, os
from PIL import Image


def export_tileset(tiles, out_dir, name='tileset', cols=8, margin=0):
    """tiles: [(name, PIL image)] all the same size. Writes <name>.png, <name>.tsj (Tiled), <name>_index.json. Returns {tile_name: gid}."""
    tw, th = tiles[0][1].size
    for n, im in tiles:
        if im.size != (tw, th): raise SystemExit(f'tile {n} is {im.size}, expected {(tw, th)}')
    rows = (len(tiles) + cols - 1) // cols; os.makedirs(out_dir, exist_ok=True)
    sheet = Image.new('RGBA', (cols * tw, rows * th), (0, 0, 0, 0)); gid = {}
    for i, (n, im) in enumerate(tiles): sheet.paste(im, ((i % cols) * tw, (i // cols) * th)); gid[n] = i + 1
    sheet.save(os.path.join(out_dir, name + '.png'))
    ts = dict(type='tileset', version='1.10', tiledversion='1.10.2', name=name, image=name + '.png', imagewidth=sheet.width, imageheight=sheet.height,
              tilewidth=tw, tileheight=th, tilecount=len(tiles), columns=cols, margin=0, spacing=0,
              tiles=[dict(id=i, properties=[dict(name='name', type='string', value=n)]) for i, (n, _) in enumerate(tiles)])
    json.dump(ts, open(os.path.join(out_dir, name + '.tsj'), 'w'), indent=1)
    json.dump(gid, open(os.path.join(out_dir, name + '_index.json'), 'w'), indent=1)
    return gid


def export_map(rows, legend, gid, tw, th, out_dir, name='demo_map', tileset='tileset'):
    """rows: list of equal-length strings; legend: char -> tile name. Writes <name>.tmj and a rendered <name>.png preview."""
    h, w = len(rows), len(rows[0]); data = [gid.get(legend.get(ch), 0) for r in rows for ch in r]
    m = dict(type='map', version='1.10', tiledversion='1.10.2', orientation='orthogonal', renderorder='right-down', width=w, height=h, tilewidth=tw, tileheight=th,
             infinite=False, nextlayerid=2, nextobjectid=1, tilesets=[dict(firstgid=1, source=tileset + '.tsj')],
             layers=[dict(id=1, name='ground', type='tilelayer', width=w, height=h, x=0, y=0, opacity=1, visible=True, data=data)])
    json.dump(m, open(os.path.join(out_dir, name + '.tmj'), 'w'), indent=1)
    sheet = Image.open(os.path.join(out_dir, tileset + '.png')); cols = sheet.width // tw; img = Image.new('RGBA', (w * tw, h * th))
    for i, g in enumerate(data):
        if g: g -= 1; img.alpha_composite(sheet.crop(((g % cols) * tw, (g // cols) * th, (g % cols + 1) * tw, (g // cols + 1) * th)), ((i % w) * tw, (i // w) * th))
    img.save(os.path.join(out_dir, name + '.png')); return img


def tile(draw, units=16):
    """Render a square tile: draw(c) paints on a units x units canvas; returns the cropped RGBA image (no outline)."""
    from artkit.core import C, PAD
    c = C(units, units); draw(c); im = c.finish(outline=False)
    k = im.width / (units + 2 * PAD); return im.crop((round(PAD * k), round(PAD * k), round((PAD + units) * k), round((PAD + units) * k)))
