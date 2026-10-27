"""Quick quality checks on exported PNGs (idea from pxl lint). `python -m artkit lint <dir>`"""
import glob, os
import numpy as np
from PIL import Image


def lint_image(path, max_colors=48):
    a = np.array(Image.open(path).convert('RGBA')); msgs = []; op = a[..., 3] > 0
    if not op.any(): return ['empty image']
    semi = ((a[..., 3] > 0) & (a[..., 3] < 255)).sum()
    cols = len({tuple(p) for p in a[op][:, :3]})
    if cols > max_colors: msgs.append(f'{cols} colours (>{max_colors}): palette may be too wide')
    nb = np.zeros_like(op)
    nb[1:] |= op[:-1]; nb[:-1] |= op[1:]; nb[:, 1:] |= op[:, :-1]; nb[:, :-1] |= op[:, 1:]
    iso = (op & ~nb).sum()
    if iso: msgs.append(f'{iso} isolated pixel(s)')
    ys, xs = np.where(op); h, w = op.shape
    if (ys.min() > 3 or xs.min() > 3 or h - 1 - ys.max() > 3 or w - 1 - xs.max() > 3) and max(h, w) < 128: msgs.append('wasted transparent margin >3px')
    if semi and cols <= 48 and max(h, w) < 128 and semi > op.sum() * .02: msgs.append(f'{semi} semi-transparent pixels (soft edges in a pixel sprite?)')
    return msgs


def lint_dir(d):
    bad = 0
    for p in sorted(glob.glob(os.path.join(d, '**', '*.png'), recursive=True)):
        if os.path.basename(p).startswith('_') or 'atlas' in p or '_strip' in p: continue
        m = lint_image(p)
        if m: bad += 1; print(f'{os.path.relpath(p, d)}: ' + '; '.join(m))
    print('lint: clean' if not bad else f'lint: {bad} file(s) with notes')
