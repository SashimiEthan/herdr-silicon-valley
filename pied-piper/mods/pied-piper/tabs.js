// The tab bar, over the valley's companies (world/band-*.png, which carry on
// the title's picture from the sidebar): the shown space's tabs are billboards
// standing behind the skyline, each with the face of the character playing its
// agent, and while the tab has no name someone typed, the character's name and
// the agent's tool as its mark, Claude Code's in its own coral on a dark board
// and the lit one (other tabs show their program's icon; a tab
// named after an agent that is no longer in it, dimmed, by what runs there
// now). They are dark, and the shown one is lit. Past them, a freeway gantry
// with green signs: new tab, new Copilot tab and the Files and Changes panels,
// yellow while their panel is open.

import { div, svg, image } from "gpui-kit";
import { h_flex, v_flex, ScrollHandle } from "gpui-base";
import { spaces, panes, run, openOverlay, theme, window, shared, layout, settings, knownAgents, notify } from "herdr";
import { FONT, TEXT, NIGHT, BOARD, SIGN, art, pix, toolMark, find } from "./ui.js";
import { casting, who, head } from "./cast.js";
import { tabRanks, dropIndex } from "./order.js";

// The band top to bottom, in px: the sky above the lamps, a billboard's lamps
// (the gantry's beam is as tall) and face, then its posts down to the street. band-front.png starts under the
// faces (art/world.py FRONT_Y, x2), so it covers the posts and never a click.
const SKY = 12, LAMPS = 4, FACE = 22, STREET = 102, FRONT = 46;
const POSTS = STREET - SKY - LAMPS - FACE;
// A status on a lit face, where the theme's own colors would wash out.
const INKED = { working: "#2f6fd0", blocked: "#d93a34", done: "#2e8b3d" };

export default class Tabs {
  init(_props, cx) {
    this.pressed = null;
    this.scroll = ScrollHandle.new();
    // Scrolling over the billboards only moves them sideways: it never changes
    // tab. The shown one is brought into view when it changes, and when a
    // billboard up to it changes width (a name, a status dot), until the
    // billboards are scrolled by hand: then they stay where they were put until
    // the shown tab changes.
    this.scrolled = false;
    this.panels = JSON.parse(localStorage.getItem("panels") ?? "{}");
    // The names agents give the tabs they start ("Copilot", "Claude Code"). A tab
    // named one of them with no agent in it lost its agent: Herdr brings a tab
    // back from a restart with a shell in it and never re-runs what was there.
    // That tab is shown as the shell it is now.
    this.agentNames = new Set();
    cx?.spawn(async (cx) => {
      const list = await knownAgents().catch(() => null);
      this.agentNames = new Set((list ?? []).map((a) => a.name));
      cx.notify();
    });
  }

  // Launch argv comes from programs.json via knownAgents(); hovering starts the lookup so the click is instant.
  lookupCopilot(machine) {
    this.copilot = { machine, agents: knownAgents({ on: machine }).catch(() => null) };
  }

  startCopilot(space, cx) {
    const machine = space?.machine ?? null;
    if (this.copilot?.machine !== machine) this.lookupCopilot(machine);
    const { agents } = this.copilot;
    this.copilot = null;
    cx.spawn(async () => {
      const copilot = (await agents)?.find((a) => a.key === "copilot");
      if (copilot?.installed) run("tab.new", { name: copilot.name, space: space?.id, argv: copilot.run });
      else notify({ title: copilot ? `Copilot isn't installed on ${machine ?? "this computer"}` : "Couldn't check for Copilot", level: "error" });
    });
  }

  // The side panel is remembered per space: switching shows that space's choice
  // (closed if it never had one), and opening or closing it records it.
  syncPanel(space, panel, body, enabled) {
    if (!space || !panel) return;
    const now = panel.hidden ? null : body?.active ?? null;
    if (space.id !== this.space) {
      const first = this.space === undefined;
      this.space = space.id; this.pending = null;
      if (!(first && !(space.id in this.panels))) {
        const stored = this.panels[space.id] ?? null, want = enabled.includes(stored) ? stored : null;
        if (want !== now) {
          this.pending = { want, until: Date.now() + 1000 };
          if (want) { run("layout.select", { stack: "panel-body", child: want }); run("layout.show", { id: "panel" }); }
          else run("layout.hide", { id: "panel" });
          return;
        }
      }
    }
    // Until the restore lands (or something else won), the old state isn't a choice.
    if (this.pending) {
      if (this.pending.want !== now && Date.now() < this.pending.until) return;
      this.pending = null;
    }
    if (this.panels[space.id] === now) return;
    this.panels[space.id] = now;
    localStorage.setItem("panels", JSON.stringify(this.panels));
  }

  render() {
    const t = theme();
    const space = spaces().find((p) => p.active);
    const shown = space?.tabs ?? [];
    const active = shown.findIndex((tab) => tab.active);
    const selected = shown[active]?.id;
    if (selected !== this.selected || active !== this.selectedIndex) {
      this.selected = selected;
      this.selectedIndex = active;
      this.scrolled = false;
      if (active >= 0) this.scroll.scroll_to_item(active);
    }
    const follow = (cx) => { if (active >= 0 && !this.scrolled) { this.scroll.scroll_to_item(active); cx.notify(); } };
    // A scroll is only noted (the scroll area moves itself), on each billboard
    // and on the strip between them: the strip may keep the event to itself.
    const scrolled = () => { this.scrolled = true; };
    // Read once: every host read copies the whole list into JS.
    const all = panes();
    const roles = casting();
    // Tabs holding a prioritized agent keep their order (order.js): a drag can't break it.
    const ranks = tabRanks(all, shared("pied-piper.priority")?.agents);
    const stop = (_e, cx) => cx.stop_propagation();
    const D = BOARD.dark, L = BOARD.lit;
    // A billboard's face: dark, or lit from its lamps, brightest under them.
    const face = (id, lit) => h_flex().id(id).relative().h(FACE).flex_none().items_center()
      .bg(lit ? L.face : D.face).border(1).border_color(lit ? L.rim : D.rim).text_color(lit ? L.ink : t.muted)
      .when(!lit, (el) => el.hover((s) => s.bg(D.hover).text_color(t.foreground)))
      .child(div().absolute().left(0).right(0).top(0).h(4).bg(lit ? L.top : D.top))
      .when(lit, (el) => el.child(div().absolute().left(0).right(0).bottom(0).h(4).bg(L.low)));
    // The face on its posts, under its lamps.
    const stand = (board, lit) => {
      const lamp = () => v_flex().flex_none().items_center().child(div().w(4).h(2).bg(lit ? L.lamp : D.lamp)).child(div().w(1).h(LAMPS - 2).bg(BOARD.arm));
      const post = () => div().w(2).h_full().flex_none().bg(BOARD.post);
      return v_flex().flex_none().on_scroll_wheel(scrolled)
        .child(h_flex().h(LAMPS).px(10).justify_between().child(lamp()).child(lamp()).child(lamp()))
        // A lit face spills a little light around itself, in two steps.
        .child(div().relative().when(lit, (el) => el.child(div().absolute().inset(-4).bg(L.glow + "12")).child(div().absolute().inset(-2).bg(L.glow + "24"))).child(board))
        .child(h_flex().h(POSTS).px(10).justify_between().child(post()).child(post()));
    };
    // A freeway sign: green, or yellow while what it leads to is open.
    const sign = (id, on) => h_flex().id(id).relative().h(FACE).flex_none().items_center().rounded(3)
      .bg(on ? SIGN.on : SIGN.face).text_color(on ? SIGN.ink : SIGN.text)
      .when(!on, (el) => el.hover((s) => s.bg(SIGN.hover)))
      .child(div().absolute().inset(1).rounded(2).border(1).border_color(on ? SIGN.ink : SIGN.line));
    // The gantry the signs hang from: a beam over the road, a leg at each end
    // down to the street. Its signs line up with the billboards' faces.
    const gantry = (signs) => v_flex().relative().flex_none().mx(6)
      .child(div().absolute().left(-6).top(0).w(3).h(STREET - SKY).bg(SIGN.leg))
      .child(div().absolute().right(-6).top(0).w(3).h(STREET - SKY).bg(SIGN.leg))
      .child(div().absolute().left(-6).right(-6).top(0).h(LAMPS - 1).bg(SIGN.web).border_t(1).border_b(1).border_color(SIGN.beam))
      .child(h_flex().mt(LAMPS).gap(4).children(signs));
    const button = (id, label, action, more = (el) => el) => more(sign(id, false).w(FACE).justify_center()
      .on_mouse_down("left", stop).on_click(action).child(label));
    const item = (c, i) => {
      const mine = all.filter((p) => p.tab === c.id);
      const program = (mine.find((p) => p.program?.agent) ?? mine[0])?.program;
      // The tab's first agent stars in it.
      const lead = mine.find((p) => p.status && who(p.terminal, roles));
      const star = lead ? who(lead.terminal, roles) : null;
      const gone = c.named && this.agentNames.has(c.name) && !mine.some((p) => p.status != null || p.program?.agent);
      // A name nobody typed (Herdr's own, an agent's, what runs there) gives way to
      // the star's, with the tool's mark after it. One someone typed stays as typed.
      const billed = Boolean(star) && (!c.named || /^tb\d+$/.test(c.name) || this.agentNames.has(c.name) || c.name === program?.name);
      const name = billed ? star.name : gone || /^tb\d+$/.test(c.name) ? program?.name ?? "Terminal" : c.name;
      const lit = c.active;
      // In its own color, unlike a row's or a pane header's: Claude Code's is its coral.
      const badge = billed ? toolMark(lead.program, null, true) : null;
      return stand(face(`tab-${c.id}`, lit).pr(7).gap(6)
        // A rename or status dot on this or an earlier tab can push the active one out.
        .when(i <= active, (el) => el.on_size_change((_size, cx) => follow(cx)))
        .on_mouse_down("left", (e, cx) => { cx.stop_propagation(); this.pressed = i; if (e.click_count === 2) run("tab.rename", { id: c.id }); })
        .on_mouse_up("left", () => {
          const from = this.pressed; this.pressed = null;
          if (from === null || from === i) { run("tab.select", { id: c.id }); return; }
          // Dropped out of order, a prioritized tab stays put and another lands first after them.
          const to = dropIndex(shown.map((x) => x.id), ranks, from, i);
          if (to !== from) run("tab.move", { id: shown[from].id, index: to + 1 });
        })
        .on_mouse_down("right", (_e, cx) => { cx.stop_propagation(); openOverlay({ mod: "menu", kind: "popup", width: 200, props: { tab: "tab", target: { id: c.id, space: space.id } } }); })
        .when(gone, (el) => el.text_color(lit ? L.faint : t.dim).tooltip(`${c.name} isn't running here any more: this tab has a shell now`))
        // The face at 16: one art pixel to a point.
        .when(Boolean(star), (el) => el.pl(2).child(head(star, 16)))
        .when(!star, (el) => el.pl(7).when(Boolean(program?.icon), (el) => el.child(program.tint ? svg(program.icon).size(12).flex_none().text_color(lit ? L.ink : t.muted) : image(program.icon).w(12).h(12).flex_none())))
        .when(billed, (el) => el.tooltip(`${star.full} · ${lead.program?.name ?? "agent"}`))
        // As a row reads: "Richard · mark".
        .child(div().max_w(150).truncate().child(badge ? `${name} ·` : c.zoomed ? `${name} Z` : name))
        .when(Boolean(badge), (el) => el.child(badge).when(Boolean(c.zoomed), (el) => el.child("Z")))
        .when(c.status === "working" || c.status === "blocked" || c.status === "done", (el) => el.child(div().size(5).flex_none().bg(lit ? INKED[c.status] : t[c.status])))
        .when(lit, (el) => el.child(div().id(`close-${c.id}`).flex_none().text_color(L.faint).hover((s) => s.text_color(L.ink)).on_mouse_down("left", stop).on_click((_e, cx) => { cx.stop_propagation(); run("tab.close", { id: c.id }); }).child(pix("close")))), lit);
    };
    const root = layout(), sidebar = find(root, "sidebar"), w = window();
    // Old saved rails and a dragged-narrow sidebar can be smaller than the window buttons.
    const lightsPadding = w?.platform === "macos" && w.titlebar === "none" && !w.fullscreen && root?.traffic_lights
      ? Math.max(10, (root.traffic_lights[0] + 64) / settings().zoom - (sidebar?.hidden ? 0 : sidebar?.size?.px ?? 0))
      : 10;
    const panel = find(root, "panel"), body = find(root, "panel-body");
    const enabled = shared("workspace.panels") ?? ["files", "changes"];
    this.syncPanel(space, panel, body, enabled);
    const panelButton = (id, label, icon) => {
      const on = panel && !panel.hidden && body?.active === id;
      return sign(`panel-${id}`, on).px(8).gap(6).on_mouse_down("left", stop)
        .on_click(() => {
          if (on) run("layout.hide", { id: "panel" });
          else { run("layout.select", { stack: "panel-body", child: id }); run("layout.show", { id: "panel" }); }
        }).child(pix(icon)).child(label);
    };
    const row = () => h_flex().gap(6).items_start();
    return h_flex().relative().size_full().min_w(0).overflow_hidden().pr(10).pl(lightsPadding).pt(SKY).gap(6).items_start().bg(NIGHT.sky).font_family(FONT).text_size(TEXT)
      .child(art("world/band-back.png", 2800, 112).absolute().left(0).top(0))
      .on_mouse_up("left", () => { this.pressed = null; })
      // The scroll area cuts at its edges: its padding is room for a lit face's glow.
      .child(row().id("tab-scroll").flex_1().min_w(0).px(4).overflow_x_scroll().track_scroll(this.scroll)
        .on_scroll_wheel(scrolled)
        .on_size_change((_size, cx) => follow(cx))
        .children(shown.map(item)))
      .child(gantry([
        button("tab-new", pix("plus"), () => openOverlay({ mod: "new-menu", kind: "popup", width: 250, height: 512 })),
        button("tab-copilot", svg("icons/copilot.svg").size(12), (_e, cx) => this.startCopilot(space, cx), (el) => el
          .on_hover((hovered) => { if (hovered) this.lookupCopilot(space?.machine ?? null); })
          .tooltip("New Copilot tab").accessibility_label("New Copilot tab")),
        ...(enabled.includes("files") ? [panelButton("files", "Files", "file")] : []),
        ...(enabled.includes("changes") ? [panelButton("changes", "Changes", "changes")] : []),
        ...(w?.buttons ? [
          button("minimize", w.platform === "windows" ? svg("mods/tabs/win-min.svg").size(16) : "−", () => run("window.minimize")),
          button("maximize", w.platform === "windows" ? svg(`mods/tabs/${w.maximized ? "win-restore" : "win-max"}.svg`).size(16) : "□", () => run("window.maximize")),
          button("close-window", w.platform === "windows" ? svg("mods/tabs/win-close.svg").size(16) : pix("close"), () => run("window.close")),
        ] : []),
      ]))
      // The skyline, in front of the posts.
      .child(art("world/band-front.png", 2800, 112 - FRONT).absolute().left(0).top(FRONT));
  }
}
