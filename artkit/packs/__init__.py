"""Asset loader. An asset file is a .py module exposing ALL = {asset_name: zero-arg function returning an RGBA PIL image}.
Optional: ANIMS = {name: (fn -> frames, fps)}, TILES, MAP, MAP_LEGEND. Pass its path with --file (or --pack <path>)."""
import importlib.util, os, sys


def load_pack(name):
    if os.path.exists(name):
        spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(name))[0], name)
        m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m; spec.loader.exec_module(m); return m
    raise SystemExit(f'asset file not found: {name!r}. Pass the path to a .py file that defines ALL = {{name: fn}}')


def assets(names):
    out = {}
    for n in names:
        m = load_pack(n)
        for k, f in m.ALL.items(): out[k] = (n, f)
    return out
