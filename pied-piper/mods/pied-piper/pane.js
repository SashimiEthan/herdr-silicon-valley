// A pane's header: the face of the character playing its agent, the tool's
// mark, the folder and the agent's status; buttons split, zoom and close this
// pane. Other terminals show their program's icon. Props from the app:
// { pane, terminal }. Click: focus the pane.

import { div, svg, image } from "gpui-kit";
import { h_flex } from "gpui-base";
import { panes, props, run, theme, home, layout } from "herdr";
import { FONT, TEXT, pix, mark, toolMark } from "./ui.js";
import { casting, who, head } from "./cast.js";

// Match the first visible tab frame, including the active child of a stack.
function paneFrame(node) {
  if (!node || node.hidden) return null;
  if (node.content?.tab && node.content.pane) return node.content.pane;
  let children = node.children ?? [];
  if (node.type === "stack") {
    const visible = children.filter((child) => !child.hidden);
    children = [visible.find((child) => child.id === node.active) ?? visible[0]];
  }
  for (const child of children) {
    const frame = paneFrame(child);
    if (frame) return frame;
  }
  return null;
}

function icon(p, size, color) {
  if (!p?.icon) return null;
  return p.tint ? svg(p.icon).size(size).flex_none().text_color(color) : image(p.icon).w(size).h(size).flex_none();
}

function folder(cwd) {
  if (!cwd) return "";
  const h = home();
  return cwd === h ? "~" : cwd.startsWith(h + "/") ? "~" + cwd.slice(h.length) : cwd;
}

export default class Pane {
  init() { this.hovered = false; }

  me() {
    return panes().find((p) => p.pane === props()?.pane);
  }

  button(t, id, name, command, args) {
    return div()
      .id(id)
      .p(4)
      .text_color(t.dim)
      .hover((s) => s.bg(t.hover).text_color(t.foreground))
      .on_click((_e, cx) => {
        cx.stop_propagation();
        run(command, args);
      })
      .child(pix(name));
  }

  render() {
    const t = theme();
    const p = this.me();
    if (!p) return div();
    const name = ((p.program?.agent || p.program?.shell) && p.program.name) || p.title || p.program?.name || "shell";
    // A shell left behind by an agent keeps the address, not the character.
    const c = p.status ? who(p.terminal, casting()) : null;
    const pic = c ? null : icon(p.program, 14, t.dim);
    // A character's agent: its tool's mark says what the name did.
    const badge = c && p.program?.agent ? toolMark(p.program, `pane-tool-${p.pane}`) : null;
    const st = p.status;
    const pane = p.pane;
    const bottom = paneFrame(layout())?.header?.position === "bottom";
    return h_flex()
      .id(`pane-head-${pane}`)
      .size_full()
      .pr(10)
      .gap(8)
      .items_center()
      .bg(t.chrome)
      .when(bottom, (el) => el.border_t(1))
      .when(!bottom, (el) => el.border_b(1))
      .border_color(t.border)
      .font_family(FONT)
      .text_size(TEXT)
      .on_hover((hovered, cx) => { this.hovered = hovered; cx.notify(); })
      .on_click(() => run("pane.focus", { pane }))
      .when(Boolean(c), (el) => el
        .child(div().id(`pane-cast-${pane}`).flex_none().tooltip(c.full).child(head(c, 32)))
        .child(div().flex_none().text_color(t.foreground).child(c.name)))
      .when(!c, (el) => el.pl(10).when(Boolean(pic), (el) => el.child(pic)))
      .when(Boolean(badge), (el) => el.child(div().flex_none().text_color(t.muted).child(badge)))
      .when(!badge, (el) => el.child(div().flex_none().truncate().max_w(260).text_color(c ? t.muted : t.foreground).child(name)))
      .child(div().flex_1().min_w(0).truncate().text_color(t.dim).child(folder(p.cwd)))
      .when(st === "blocked" || st === "working" || st === "done", (el) => el.child(mark(t, st)))
      .when(this.hovered, (el) => el
        .child(this.button(t, `ph-r-${pane}`, "split-right", "pane.split", { direction: "right", pane }))
        .child(this.button(t, `ph-d-${pane}`, "split-down", "pane.split", { direction: "down", pane }))
        .child(this.button(t, `ph-z-${pane}`, p.zoomed ? "unzoom" : "zoom", "pane.zoom", { pane }))
        .child(this.button(t, `ph-x-${pane}`, "close", "pane.close", { pane })));
  }
}
