---
name: artkit
description: Generate 2D game assets (props, characters, vehicles, UI, tiles) as PNGs, contact sheets and sprite atlases with the artkit Python tool, in pixel, flat-vector or ink-cartoon style. Use when the user asks for game art made with artkit or "the asset tool".
---
# artkit - how to use it (read this, don't re-invent the engine)

Setup: this folder is cloned or copied into the game project. It needs pillow, numpy and scipy (any version); install only the ones that are missing, and never upgrade or replace ones already installed.
Run from INSIDE this folder: `python -m artkit ...`, giving `--file` and `--out` as absolute paths (or paths relative to this folder) that point into the game's own folder.

## Workflow
1. Read `style.json` if the project has one (palette/outline/size decisions) and follow it.
2. Write the user's idea as drawing functions in an asset file that lives in the GAME's folder (never inside artkit). The library ships no example art, so design each asset fresh from the user's description and style.json.
3. Build: `python -m artkit build --file my_assets.py --style pixel --only a,b --out out --sheet`
   Styles: `pixel` (design unit = 1 px), `flat` (clean vector look, 6 px/unit), `ink` (wobbly hand-inked, slow ~1s/sprite), `all`.
   Flags: `--sheet` contact sheet, `--atlas` packed sheet + atlas.json, `--scale N` upscale pixel output.
4. Asset file shape: `from artkit.core import *`, each function does `c = C(w, h)`, draws, `return c.finish()`; end with `ALL = {name: fn}`.
   Build with `--style all --sheet`. Look at ONE contact sheet, fix, rebuild. Batch many assets per file; don't render one by one.

## More commands
- Animation clips: `python -m artkit build --file my_assets.py --anims --style pixel --scale 4 --only boss_walk` -> `anims/<name>.gif`, `_strip.png`, `.json` (frame size, fps). Clips are `ANIMS = {name: (fn -> frames, fps)}` in the asset file; frames are images or `(img, dx, dy)`. Helpers in `artkit/anim.py`: bob, squash, sway, flash. Parametric poses (a `step=-1|0|1` argument for walk frames) beat image transforms.
- Tiles + Tiled map editor: `python -m artkit tileset --file my_assets.py --style pixel --sheet` -> `tiles/tileset.png`, `tileset.tsj`, `demo_map.tmj`. Define `TILES = {name: fn}` (use `from artkit.tiled import tile` helper, 16 units square) plus optional `MAP`/`MAP_LEGEND` ASCII layout.
- Colour variants: `variant(fn, purple2='carblue')` (palette swap) in `ALL`, or `with swap(...)`. New colours: `make_pal('mint', (120,220,170))` (hue-shifted ramp). See `artkit/variants.py`.
- Lint: `python -m artkit lint --target out/pixel` flags stray pixels, wide palettes, soft edges, wasted margins. `--trim` on build crops margins.

## Drawing API (same for all styles; units are 'design units')
`c = C(w, h)`; `c.ell(cx,cy,rx,ry,col)`, `c.poly([(x,y)..],col)`, `c.rect(x0,y0,x1,y1,col)`, `c.rrect(x0,y0,x1,y1,r,col)`,
`c.line([(x,y)..], width, col)` (smooth through points), `c.stroke(pts, radii, col)` (tapered), `c.px(x,y,col)` (exact pixel in pixel style),
`c.clip(fn)` ... `c.end()`, `c.text(...)` (vector styles), `c.shaded(shape, base, dark, light, shift, hl=[(cx,cy,rx,ry)])`
where `shape(c, dx, dy, col)` draws the silhouette (dark crescent bottom-right + highlight blobs). Always `return c.finish()`.
Colours: `PALS['name'] -> (base, shadow, highlight)`; extend with `PALS.update(name=(K(r,g,b),K(..),K(..)))`.
No example assets are bundled, on purpose, so output is not biased toward any look.

## Tips
- Typical sizes (pixel): icon 16-28, prop 30-48, character 40x60, car 76x34. Scale the same code up for vector.
- Keep silhouettes simple; add detail with small rects/ellipses. Check mirrored/asymmetric parts by eye on the sheet.
- Realistic anatomy and many-frame animation are weak spots. Chibi/stylised characters and props are strong.
- Optional: vex (vector DSL, Spine/Tiled export) and pxl (pixel DSL, GIF/lint) from github.com/uilianks can be used alongside; they need npm access.
