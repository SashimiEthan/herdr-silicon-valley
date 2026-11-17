// The status bar, a plain bar under the terminals: the shown space's machine
// and branch, a light per agent (lit in its status's color, an outline when
// idle), how many there are, and who needs you.

import { div } from "gpui-kit";
import { h_flex } from "gpui-base";
import { spaces, agents, theme, run, window, keys } from "herdr";
import { FONT, TEXT, pix } from "./ui.js";

export default class Status {
  // The palette key as actually bound, not a hardcoded one; without a
  // binding the hint stays useful ("commands") instead of lying.
  hint() {
    const mac = window()?.platform === "macos";
    const mod = { cmd: mac ? "⌘" : "Ctrl+", ctrl: mac ? "⌃" : "Ctrl+", shift: mac ? "⇧" : "Shift+", alt: mac ? "⌥" : "Alt+", option: mac ? "⌥" : "Alt+" };
    const b = keys().find((k) => k.section === "global" && k.action === "app.palette");
    const parts = b && b.keys.endsWith("--") ? [...b.keys.slice(0, -2).split("-"), "-"] : b?.keys.split("-");
    const key = parts && parts.map((p) => mod[p.toLowerCase()] ?? p.toUpperCase()).join("");
    return key ? `${key}  commands` : "commands";
  }

  render() {
    const t = theme();
    const space = spaces().find((s) => s.active);
    const list = agents();
    const needs = list.filter((a) => a.status === "blocked").length;
    const label = (icon, text) => h_flex().flex_none().gap(6).items_center().child(pix(icon)).child(text);
    // More agents than this and the lights stop: the count says the rest.
    const lights = list.slice(0, 24).map((a) => (a.status === "working" || a.status === "blocked" || a.status === "done"
      ? div().size(6).flex_none().bg(t[a.status])
      : div().size(6).flex_none().border(1).border_color(t.dim)));
    return h_flex().size_full().overflow_hidden().px(10).gap(16).items_center().bg(t.chrome).border_t(1).border_color(t.border)
      .font_family(FONT).text_size(TEXT).text_color(t.muted)
      .child(label(space?.machine ? "server" : "monitor", space?.machine ?? "This computer"))
      .when(Boolean(space?.branch), (el) => el.child(label("branch", space.branch)))
      .child(h_flex().flex_none().gap(7).items_center()
        .when(lights.length > 0, (el) => el.child(h_flex().flex_none().gap(3).children(lights)))
        .child(`${list.length} ${list.length === 1 ? "agent" : "agents"}`)
        .when(needs > 0, (el) => el.child(div().text_color(t.blocked).child(`· ${needs} ${needs === 1 ? "needs" : "need"} you`))))
      .child(div().flex_1())
      .child(div().flex_none().text_color(t.dim).child("Making the world a better place"))
      .child(div().id("palette").flex_none().text_color(t.dim).hover((s) => s.text_color(t.foreground)).on_click(() => run("app.palette")).child(this.hint()));
  }
}
