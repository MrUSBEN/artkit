import argparse, json, os, subprocess, sys, time

HELP = """artkit - code-drawn game assets (pixel / flat vector / ink cartoon)
  python -m artkit list --file my_assets.py
  python -m artkit build --file my_assets.py --style all --out out/       (your asset file; defines ALL = {name: fn})
  python -m artkit build --file my_assets.py --only a,b --style flat --sheet --atlas
Options: --scale N (nearest-neighbour upscale of pixel output), --style pixel|flat|ink|all, --sheet (contact sheet), --atlas (packed sheet+json)"""


def main(argv=None):
    ap = argparse.ArgumentParser(prog='artkit', description=HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['build', 'list', 'tileset', 'lint'])
    ap.add_argument('--pack', default=''); ap.add_argument('--file', help='path to your own asset .py file (defines ALL)')
    ap.add_argument('--only', help='comma list of asset names'); ap.add_argument('--style', default='pixel')
    ap.add_argument('--out', default='artkit_out'); ap.add_argument('--scale', type=int, default=1)
    ap.add_argument('--anims', action='store_true', help='also export animation clips (gif + strip + json)'); ap.add_argument('--target', help='lint: folder to check'); ap.add_argument('--trim', action='store_true', help='crop transparent margins'); ap.add_argument('--sheet', action='store_true'); ap.add_argument('--atlas', action='store_true')
    a = ap.parse_args(argv)
    if a.cmd == 'lint':
        from artkit.lint import lint_dir; return lint_dir(a.target or a.out)
    if a.style == 'all':                                        # one process per style (style is fixed at import time)
        for st in ('pixel', 'flat', 'ink'):
            subprocess.run([sys.executable, '-m', 'artkit'] + _argv(a, st), check=True)
        return
    os.environ['ARTKIT_STYLE'] = a.style
    from artkit import packs
    names = [a.file] if a.file else [p for p in a.pack.split(',') if p]
    if not names: raise SystemExit('give your asset file: --file my_assets.py (it defines ALL = {name: fn})')
    A = packs.assets(names)
    if a.only:
        want = a.only.split(','); miss = [w for w in want if w not in A]
        if miss and not a.anims: raise SystemExit(f'unknown asset(s): {miss}. try: python -m artkit list')
        A = {k: A[k] for k in want if k in A}
    if a.cmd == 'list':
        for k, (p, _) in A.items(): print(f'{p:10s} {k}')
        return
    from PIL import Image
    from artkit import sheet
    if a.cmd == 'tileset':
        from artkit import tiled
        T = {}
        for n in names:
            m = packs.load_pack(n)
            for k, f in getattr(m, 'TILES', {}).items(): T[k] = f
        if not T: raise SystemExit('no TILES in that pack (define TILES = {name: fn} in your asset file)')
        out = os.path.join(a.out, a.style, 'tiles'); tl = [(k, f()) for k, f in T.items()]
        if a.scale > 1 and a.style == 'pixel': tl = [(k, im.resize((im.width * a.scale, im.height * a.scale), Image.NEAREST)) for k, im in tl]
        gid = tiled.export_tileset(tl, out)
        m = [packs.load_pack(n) for n in names if hasattr(packs.load_pack(n), 'MAP')]
        if m: tiled.export_map(m[0].MAP, m[0].MAP_LEGEND, gid, *tl[0][1].size, out)
        if a.sheet: sheet.contact_sheet(tl, os.path.join(out, '_tiles_sheet.png'), cols=8, max_px=96)
        print(f'{a.style}: {len(tl)} tiles + demo map -> {out}'); return
    out = os.path.join(a.out, a.style); os.makedirs(out, exist_ok=True); t = time.time(); ims = []
    for k, (p, f) in A.items():
        im = f()
        if a.trim and im.getbbox(): im = im.crop(im.getbbox())
        if a.scale > 1 and a.style == 'pixel': im = im.resize((im.width * a.scale, im.height * a.scale), Image.NEAREST)
        im.save(os.path.join(out, k + '.png')); ims.append((k, im))
    if a.sheet and ims: sheet.contact_sheet(ims, os.path.join(out, '_contact_sheet.png'), cols=min(8, len(ims)), max_px=150 if a.style != 'pixel' else 120)
    if a.atlas and ims: sheet.pack_atlas(ims, os.path.join(out, 'atlas.png'), os.path.join(out, 'atlas.json'))
    if a.anims:
        from artkit import anim
        n_an = 0
        for pn in names:
            for k, (fn, fps) in getattr(packs.load_pack(pn), 'ANIMS', {}).items():
                if a.only and k not in a.only.split(','): continue
                anim.save_clip(fn(), os.path.join(out, 'anims', k), fps=fps, scale=a.scale); n_an += 1
        print(f'{n_an} animation clips -> {out}/anims')
    print(f'{a.style}: {len(ims)} sprites -> {out} ({time.time() - t:.1f}s)')


def _argv(a, st):
    r = ['build', '--pack', a.pack, '--style', st, '--out', a.out, '--scale', str(a.scale)]
    if a.file: r += ['--file', a.file]
    if a.only: r += ['--only', a.only]
    if a.sheet: r.append('--sheet')
    if a.trim: r.append('--trim')
    if a.anims: r.append('--anims')
    if a.atlas: r.append('--atlas')
    return r
