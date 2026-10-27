"""Style selector. Set env ARTKIT_STYLE = pixel | flat | ink BEFORE importing (the CLI does this for you).
Every drawing function in an asset file uses only this API, so the same code renders in all three styles.
    c = C(w, h)            canvas in 'design units' (pixel style: 1 unit = 1 final pixel; vector styles: 1 unit = 6 px)
    c.ell/poly/rect/rrect/line/stroke/px/text, c.clip(fn) ... c.end(), c.shaded(shape, base, dark, light, hl=[...])
    c.finish() -> RGBA PIL image (outlined). PALS[name] -> (base, shadow, highlight) colours."""
import os
STYLE = os.environ.get('ARTKIT_STYLE', 'pixel')
if STYLE == 'pixel':
    from ._pixel import *          # noqa
    from ._pixel import SS, PAD, OUT
else:
    from ._vector import *         # noqa
    from ._vector import SS, PAD, OUT
