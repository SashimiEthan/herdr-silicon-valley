// The sidebar's top: the title over the valley at night (world/brand.png),
// with search and fold in its corner. As the footer role, the sidebar's
// bottom: a plain bar the height of the status bar, with settings and add
// machine.

import { div } from "gpui-kit";
import { h_flex } from "gpui-base";
import { theme, run, props, window, updates } from "herdr";
import { FONT, TEXT, NIGHT, art, pix, narrow, toggleSidebar } from "./ui.js";

// The title art's width on screen.
const WIDE = 480;

export default class Chrome {
  init() { this.width = WIDE; }

  button(t, id, icon, action) {
    return div().id(id).size(26).flex_none().flex().items_center().justify_center().bg(NIGHT.plate).text_color(t.muted)
      .hover((s) => s.bg(t.hover).text_color(t.foreground))
      .on_mouse_down("left", (_e, cx) => cx.stop_propagation()).on_click(action).child(pix(icon));
  }

  footer(t, collapsed) {
    const item = (id, icon, label, dim, action) => h_flex().id(id).relative().h(20).px(6).gap(6).flex_none().items_center()
      .when(collapsed, (el) => el.w(20).px(0).justify_center().tooltip(label))
      .text_color(dim ? t.dim : t.muted).hover((s) => s.bg(t.hover).text_color(t.foreground)).cursor_pointer()
      .on_click(action).child(pix(icon))
      .when(!collapsed, (el) => el.child(label));
    const ready = div().size(6).bg(t.accent);
    return h_flex().id("pp-footer").size_full().overflow_hidden().px(collapsed ? 0 : 6).gap(collapsed ? 2 : 4).items_center()
      .when(collapsed, (el) => el.justify_center())
      .bg(t.chrome).border_t(1).border_color(t.border).font_family(FONT).text_size(TEXT)
      .child(item("settings", "settings", "Settings", false, () => run("app.settings"))
        .when(Boolean(updates().app.ready), (el) => el.child(collapsed ? ready.absolute().top(1).right(1) : ready)))
      .child(item("machine", "plus", "Add machine", true, () => run("mod.open", { name: "machine-add" })));
  }

  render() {
    const t = theme();
    const collapsed = narrow();
    if (props()?.role === "footer") return this.footer(t, collapsed);
    const w = window();
    // The picture is as wide as the sidebar gets; a narrower one shows its middle, the rail its left end.
    return div().id("pp-brand").relative().size_full().overflow_hidden().bg(NIGHT.sky).font_family(FONT).text_size(TEXT)
      .on_size_change((size, cx) => { if (size.width !== this.width) { this.width = size.width; cx.notify(); } })
      .child(art("world/brand.png", WIDE, 112).absolute().top(0).left(collapsed ? 0 : Math.round((this.width - WIDE) / 2)))
      .child(h_flex().absolute().top(8).right(8).gap(4)
        .when(!collapsed, (el) => el.child(this.button(t, "search", "search", () => run("mod.open", { name: "picker" }))))
        // On the macOS rail the traffic lights fill the row; the spaces list's » unfolds it.
        .when(!(collapsed && w?.platform === "macos"), (el) => el.child(this.button(t, "sidebar-toggle", "sidebar", toggleSidebar))));
  }
}
