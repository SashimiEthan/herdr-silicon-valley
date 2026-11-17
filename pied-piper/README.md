# Silicon Valley (pied-piper)

Herdr as HBO's Silicon Valley, in pixel art, at night. The red title over a skyline of the valley's companies, with your tabs as billboards; the sidebar is the Hacker Hostel, where every agent is played by a character from the show, at a desk in the Office or on a bunk in the Bedroom, posed by what the agent is doing. Dark only.

## What's here

| Path | What it is |
|---|---|
| `layouts/pied-piper.json` | The window. `layouts/pied-piper.png` is its picture in Settings |
| `themes/pied-piper.json` | Its colors: night navy, Pied Piper green, working blue, done green. Named like the layout, so Settings offers it only with this layout |
| `mods/pied-piper/` | Everything the layout draws, one mod in roles (`main.js`), with its pictures, its font (Departure Mono, OFL, in `fonts/`) and two notification sounds (`sounds/`) |
| `mods/pied-piper-menu/` | The right-click menu for spaces and agents (a clone of Herdr's `menu`), with a 1–5 Priority list. A priority is what puts a space in the Office; the rest sleep in the Bedroom |

## Adding it

Follow "Layouts and mods other people made" in `~/.config/herdr-app/AGENTS.md`, and also:

1. **The theme.** Copy `themes/pied-piper.json` into the home's `themes/` too. The layout asks for it by name (`"theme": "pied-piper"`); without it the window shows in the person's own theme, and the pictures were drawn for these colors. If you rename it to avoid a clash, change the layout's `"theme"` to match.
2. **The menu.** If you rename `pied-piper-menu`, also change the two `mod: "pied-piper-menu"` in `mods/pied-piper/spaces.js`, and the menu's own name and `mods/pied-piper-menu/` paths in its `main.js`.
3. **The sounds (optional; ask the person first).** Herdr takes its notification sounds from `settings.json`, never from a layout, so they don't come with it. To use the show's (the opening bars of its title music, replayed on a synth) set:

   ```json
   "sounds": { "enabled": true, "done": "mods/pied-piper/sounds/finished.wav", "blocked": "mods/pied-piper/sounds/needs-you.wav" }
   ```

   They then play in every layout, not only this one. They are WAV files; tested on macOS.

Priorities are kept in Herdr's shared state as `"pied-piper.priority"`: they start empty, and other layouts' priority lists don't share them.
