# artkit

**Status: under development.** artkit is an experimental library for **agentic artwork**: an AI agent (such as Claude) uses it to turn a game idea into 2D art by writing small drawing programs, instead of generating images.

Everything is drawn with code from one drawing API, in three looks:

- **pixel** - crisp pixel art
- **flat** - clean flat vector
- **ink** - hand-inked cartoon

It can produce single sprites, contact sheets, sprite atlases, animation clips (GIF, strip, JSON) and tilesets for the Tiled map editor.

artkit is a **library only**. It ships no example art on purpose, so nothing biases the look of your game. The look comes from your idea and from the game's own `style.json`.

## Using it

1. Clone or copy this folder into your game project.
2. Make sure `pillow`, `numpy` and `scipy` are installed (any version).
3. Write an asset file in your game folder: functions that draw with the artkit API, plus `ALL = {name: fn}`. See `SKILL.md` for the drawing API and commands.
4. From inside this folder, build into your game's folder:

       python -m artkit build --file <path to your asset file> --style all --out <your assets folder> --sheet

Generated art and asset files belong in your game, not in this repo.

## What's inside

- `artkit/` - the library (two renderers behind one API, animation, tiles, palette variants, lint)
- `SKILL.md` - the short guide an AI agent reads before using it

## Notes

This is an early tool and it changes often. It is strong at props, UI, tiles, vehicles, stylised characters and simple animation. It is weak at realistic anatomy and long animations.
