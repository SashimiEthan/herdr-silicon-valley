// How notifications look: an agent's news comes with its character's face.
// Anything can post one with notify({ title, body, level, icon, action });
// click to run its action (e.g. go to the agent) and dismiss it.

import { div, image } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { props, closeOverlay, run, theme, agents } from "herdr";
import { FONT, TEXT } from "./ui.js";
import { casting, who, head } from "./cast.js";

const DOT = { error: "blocked", warning: "working", success: "done", info: "accent" };

export default class Toast {
  render() {
    const t = theme();
    const p = props() ?? {};
    const login = /^([a-z0-9][a-z0-9_.-]{0,31}) needs login; run hc machine login \1$/.exec(p.body ?? "");
    const command = login ? `hc machine login ${login[1]}` : null;
    // The agent this is about: the one its click goes to.
    const targets = Object.values(p.action?.args ?? {}).filter((v) => typeof v === "string");
    const list = targets.length ? agents() : [];
    const agent = list.find((a) => targets.includes(a.address) || targets.includes(a.pane));
    const c = agent ? who(agent.address, casting(list)) : null;
    const body = login ? null : [c?.name, p.body].filter(Boolean).join(" · ");
    return h_flex()
      .id("toast")
      .size_full()
      .px(c ? 10 : 18)
      .gap(12)
      .items_center()
      .bg(t.popover)
      .font_family(FONT)
      .text_size(TEXT)
      .cursor_pointer()
      .hover((s) => s.bg(t.hover))
      .on_click(() => {
        if (p.action?.name) run(p.action.name, p.action.args ?? {});
        closeOverlay(p.overlay);
      })
      .child(c ? head(c, 32) : p.icon ? image(p.icon).w(18).h(18).flex_none() : div().size(8).flex_none().bg(t[DOT[p.level] ?? "accent"]))
      .child(
        v_flex()
          .flex_1()
          .gap(2)
          .line_height("14px")
          .overflow_hidden()
          .child(div().truncate().text_color(t.foreground).child(login ? `${login[1]} needs a login: run` : p.title ?? ""))
          .when(Boolean(body), (el) => el.child(div().truncate().text_color(t.muted).child(body)))
          .when(Boolean(login), (el) => el.child(h_flex().gap(8).items_center()
            .child(div().flex_1().min_w(0).truncate().tooltip(command).text_color(t.muted).child(command))
            .child(div().id("toast-login-copy").flex_none().px(6).py(3).bg(t.raised)
              .text_color(t.foreground).cursor_pointer().hover((s) => s.bg(t.hover))
              .on_click((_e, cx) => { cx.stop_propagation(); cx.write_to_clipboard(command); this.copied = true; cx.notify(); })
              .child(this.copied ? "Copied" : "Copy")))),
      );
  }
}
