// What every Pied Piper role draws with: the pixel font, the icons, the art, the
// status marks and the sidebar's rail.

import { div, svg, image } from "gpui-kit";
import { layout, run, shared, setShared, window } from "herdr";

export const HOME = "mods/pied-piper";
// Departure Mono's pixels land on whole screen pixels at 11px, so everything is 11px.
export const FONT = "Departure Mono";
export const TEXT = 11;

// A picture from this mod, `w` x `h` on screen. The art is drawn small and saved
// 4x; shown at 2x, every art pixel is a whole number of screen pixels.
export const art = (path, w, h) => image(`${HOME}/${path}`).w(w).h(h).flex_none();

// The night the art is painted in, for what sits on it: the sky, and a plate
// for text.
export const NIGHT = { sky: "#070b16", plate: "#0a0e17e6" };

// The tabs are billboards over the valley. One is dark until it is lit, and
// the lit one is the tab or panel that is shown: its face, the light pooled
// under its lamps (`top`) and falling off (`low`), its frame, its lamps, the
// posts it stands on, and what is written on it.
export const BOARD = {
  dark: { face: "#141d30", top: "#1b2640", rim: "#2c3854", hover: "#1c2844", lamp: "#3a4358" },
  lit: { face: "#e6dfc4", top: "#f6f0d8", low: "#cfc7a8", rim: "#8d8a78", lamp: "#fff6c8", glow: "#ffd27a", ink: "#141b2b", faint: "#7d775f" },
  post: "#2a3348", arm: "#59606a",
};

// The buttons past the tabs are freeway signs hung from a gantry: green, a pale
// line just inside the edge. One whose panel is open is the yellow of an EXIT
// ONLY panel.
export const SIGN = {
  face: "#0f4d35", hover: "#156648", line: "#b9d6c4", text: "#e8f3ea",
  on: "#e3c04a", ink: "#141b2b",
  beam: "#59606a", web: "#232b38", leg: "#3d4656",
};

// The sidebar's two rooms at night (art/decor.py draws each wall): the wall's
// color, for where its picture isn't; the two quieter text colors that read on
// it (the theme's are for navy); a row under the pointer and the row that is
// shown, as light over the wall; a plate for the room's name.
export const ROOMS = {
  office: { wall: "#27150c", muted: "#d2b6a4", dim: "#a98672", hover: "#ffffff12", selected: "#ffffff22", plate: "#120a06e6" },
  bedroom: { wall: "#0e1622", muted: "#9eabbd", dim: "#6d7b90", hover: "#ffffff0a", selected: "#ffffff17", plate: "#070b12e6" },
};

// An icon from icons/, tinted with the text color. 11px shows it pixel for pixel.
export const pix = (name, size = 11) => svg(`${HOME}/icons/${name}.svg`).size(size).flex_none();

// The tool an agent runs in, as its mark in place of its name. Claude Code's,
// Copilot's and Codex's are drawn at the icons' pixel size (TOOLS in
// art/icons.py; [width, height] here); another tool's is the app's own icon.
// Tinted with the text around it, not the tool's own color: Claude's coral is
// nearly the theme's "needs you" red. The tabs are the exception: they pass
// `own`, and Claude Code's mark there is its own coral (OWN), on a dark
// billboard and the lit one alike. Copilot's and Codex's logos
// are one color anyway, so they stay tinted. With an `id`, hovering names the
// tool. Null when the tool has no icon: write its name.
// (Not `tool`: spaces.js has a function by that name, and it wins over an import here without an error.)
const TOOLS = { claude: [16, 11], copilot: [13, 11], codex: [14, 13] };
// Claude Code's coral: Anthropic's brand orange, the color of the mascot this
// mark draws (Anthropic's brand guidelines, Simple Icons' Claude Code entry and
// the Claude Code docs' logo all give #d97757).
export const OWN = { claude: "#d97757" };
export function toolMark(p, id, own = false) {
  const key = p?.key === "claude-code" ? "claude" : p?.key;
  const size = TOOLS[key];
  const pic = size ? svg(`${HOME}/icons/tool-${key}.svg`).w(size[0]).h(size[1]).flex_none().when(own && Boolean(OWN[key]), (el) => el.text_color(OWN[key]))
    : !p?.icon ? null
    : p.tint ? svg(p.icon).size(11).flex_none() : image(p.icon).w(11).h(11).flex_none();
  return pic && id ? div().id(id).flex_none().tooltip(p.name).child(pic) : pic;
}

export function find(node, id) {
  if (node?.id === id) return node;
  for (const child of node?.children ?? []) {
    const found = find(child, id);
    if (found) return found;
  }
  return null;
}

// The sidebar's rail goes by its width, not a flag: dragging its edge narrows it too.
export const narrow = () => (find(layout(), "sidebar")?.size?.px ?? Infinity) < 160;

// To the rail (on macOS wide enough for the traffic lights), or back to the width it had.
export function toggleSidebar() {
  const width = find(layout(), "sidebar")?.size?.px;
  if (!narrow()) setShared("sidebar.width", width);
  // Mods edited before the rail went by width still read the flag.
  setShared("sidebar.collapsed", !narrow());
  run("layout.resize", { id: "sidebar", px: narrow() ? (shared("sidebar.width") ?? 268) : window()?.platform === "macos" ? 76 : 44 });
}

// An agent's status as pixels: blocked says so, working is a square with a halo,
// done a square, idle an outline (red when a Copilot subagent failed).
// `solid` is for a mark on a colored wall, where red letters would not read.
export function mark(t, status, solid = false) {
  if (status === "blocked") return div().flex_none().px(5).h(16).flex().items_center().bg(solid ? "#c8322c" : t.blocked + "26").text_color(solid ? "#ffffff" : t.blocked).child("NEEDS YOU");
  if (status === "idle" || status === "failed") return div().size(8).mx(3).flex_none().border(2).border_color(status === "failed" ? t.blocked : (t.idle ?? t.dim));
  const color = t[status] ?? t.dim;
  const dot = div().size(8).flex_none().bg(status === "working" || status === "done" ? color : t.dim + "00");
  if (status !== "working") return dot.mx(3);
  // Slow and faint on purpose: faster or stronger pulses give some people headaches.
  return div().relative().mx(3).flex_none().child(div().absolute().left(-3).top(-3).size(14).bg(color).loop("opacity", { from: 0, to: 0.3, period: 7000 })).child(dot);
}
