// Context menus (Herdr's items, plus priorities for spaces and agents). Opened as
// a popup with props { tab: "pane" | "tab" | "space" | "agent" | "global", target };
// an agent's target is { pane, space, machine }. Tab "priority" is the flyout a
// space's Priority item opens: { target: what it numbers, parent: the menu's overlay }.
// ↑/↓ move, Enter runs, Esc closes. An item is [label, command, args, { on, off }];
// a command "worktree" opens the worktree dialog instead.

import { View, div, svg } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { run, props, closeOverlay, openOverlay, theme, keys, terminals, spaces, panes, agents, machines, exec, shared, setShared } from "herdr";

// Where a space is now: its first terminal's live folder, else where it was made.
function place(s) {
  const tabs = new Set((s.tabs ?? []).map((c) => c.id));
  return panes().find((p) => tabs.has(p.tab) && p.cwd)?.cwd || s.folder;
}

// A space's checkout: "main" (a repo's own), "linked" (a worktree), or null.
async function checkout(folder, on) {
  const top = await exec("git", ["rev-parse", "--show-toplevel"], { cwd: folder, on });
  const common = await exec("git", ["rev-parse", "--path-format=absolute", "--git-common-dir"], { cwd: folder, on });
  if (top.code !== 0 || common.code !== 0) return null;
  return common.stdout.trim() === `${top.stdout.trim()}/.git` ? "main" : "linked";
}

// { spaces: [{ id, machine, n }], agents: [{ pane, machine, n }] }: one list of
// numbers 1–5 for spaces and agents together, each held once.
const PRIORITY = "pied-piper.priority";
const LEVELS = 5;
// The open priority flyout's overlay id.
const SUB = "pied-piper-menu.sub";

// What a number is set on.
function subject(tab, tg) {
  if (tab === "space") return { kind: "spaces", key: "id", id: tg.id, machine: spaces().find((s) => s.id === tg.id)?.machine ?? null };
  return { kind: "agents", key: "pane", id: tg.pane, machine: tg.machine ?? null };
}

// Gone only if its machine is loaded: one asleep keeps its numbers. An agent's
// number goes with the agent, not its pane: once the agent exits and leaves a
// shell there, no list shows the pane, so it must not hold a number either.
function kept() {
  const ready = new Set(machines().filter((m) => m.layout === "ready").map((m) => m.name));
  const asleep = (e) => e.machine != null && !ready.has(e.machine);
  const ids = new Set(spaces().map((s) => s.id));
  const live = new Set(panes().filter((p) => p.status != null || p.program?.agent).map((p) => p.pane));
  const all = shared(PRIORITY) ?? {};
  return {
    spaces: (all.spaces ?? []).filter((e) => asleep(e) || ids.has(e.id)),
    agents: (all.agents ?? []).filter((e) => asleep(e) || live.has(e.pane)),
  };
}

// Every number can be picked, one held elsewhere too (prioritize bumps it);
// s's own is checked.
function numberItems(s) {
  const own = kept()[s.kind].find((e) => e[s.key] === s.id)?.n ?? 0;
  return [
    ...Array.from({ length: LEVELS }, (_, i) => [String(i + 1), "priority", { ...s, op: "set", n: i + 1 }, { on: own === i + 1 }]),
    ...(own ? [["Remove priority", "priority", { ...s, op: "remove" }]] : []),
  ];
}

// Setting n takes s off its own number, then gives it n. Whatever holds n, and
// the run of held numbers beyond it, moves one place to the first free number,
// so only the run in the way moves. A new number, or a move up (to a smaller n),
// pushes the run down: n to n+1, the one there to n+2, and so on; one pushed past
// LEVELS loses its priority. A move down (to a larger n) pulls the run up toward
// the number s left: n to n-1, and so on, into that number at the latest, so no
// one is lost. Spaces and agents bump each other, and so do ones on a sleeping
// machine. Picking its own number changes nothing; removing moves no one up.
function prioritize(s) {
  const k = kept();
  const own = k[s.kind].find((e) => e[s.key] === s.id)?.n;
  if (s.op === "set" && own === s.n) return;
  const next = { ...k, [s.kind]: k[s.kind].filter((e) => e[s.key] !== s.id) };
  if (s.op === "set") {
    const held = new Set([...next.spaces, ...next.agents].map((e) => e.n));
    const step = own && own < s.n ? -1 : 1;
    let end = s.n;
    while (held.has(end)) end += step;
    const inRun = (n) => (step > 0 ? n >= s.n && n < end : n <= s.n && n > end);
    const bump = (e) => (!inRun(e.n) ? [e] : e.n + step <= LEVELS ? [{ ...e, n: e.n + step }] : []);
    next.spaces = next.spaces.flatMap(bump);
    next.agents = next.agents.flatMap(bump);
    next[s.kind].push({ [s.key]: s.id, machine: s.machine, n: s.n });
  }
  setShared(PRIORITY, next);
}

function items(p, git) {
  p = p ?? {};
  const tg = p.target ?? {};
  switch (p.tab) {
    case "pane": {
      // A kept sub-agent can go back under its parent, still running.
      const all = terminals();
      const term = all.find((t) => t.address === tg.terminal);
      const parent = term?.parent && all.find((t) => t.address === term.parent);
      // Once they go to the program, Shift+right-click still opens this menu.
      const toProgram = term?.labels?.["herdr.right-click"] === "program";
      // A terminal shown outside a tab (a layout terminal block, a window) has
      // no pane to split, zoom or close: its pane is the block's id.
      const inTab = panes().some((pane) => pane.pane === tg.pane);
      return [
        ...(inTab
          ? [
              ["Split right", "pane.split", { direction: "right", pane: tg.pane }],
              ["Split down", "pane.split", { direction: "down", pane: tg.pane }],
              ["Zoom", "pane.zoom", { pane: tg.pane }],
            ]
          : []),
        ...(term
          ? [
              toProgram
                ? ["Use Herdr right-click menu", "terminal.right_click", { terminal: term.address, to: "menu" }]
                : ["Send right-clicks to pane", "terminal.right_click", { terminal: term.address, to: "program" }],
            ]
          : []),
        ...(parent ? [[`Send back to ${parent.name || parent.address}`, "terminal.park", { terminal: term.address }]] : []),
        ...(inTab ? [["Close pane", "pane.close", { pane: tg.pane }]] : []),
      ];
    }
    case "tab":
      return [
        ["Rename", "tab.rename", { id: tg.id }],
        ["New tab", "tab.new", { space: tg.space }],
        ["Close", "tab.close", { id: tg.id }],
      ];
    case "agent":
      return numberItems(subject("agent", tg));
    case "priority":
      return numberItems(tg);
    case "space":
      return [
        ["Priority", "priority-menu", subject("space", tg)],
        ["Rename", "space.rename", { id: tg.id }],
        ...(git ? [["New worktree", "worktree", { space: tg.id, action: "new" }], ["Open worktree", "worktree", { space: tg.id, action: "open" }]] : []),
        ...(git === "linked" ? [["Remove worktree", "worktree", { space: tg.id, action: "remove" }]] : []),
        ["Close", "space.close", { id: tg.id }],
      ];
    default:
      return [
        ["New space", "space.new", {}],
        ["Keybinds", "app.help", {}],
        ["Theme: graphite", "app.theme", { name: "graphite" }],
        ["Theme: ink", "app.theme", { name: "ink" }],
        ["Theme: moss", "app.theme", { name: "moss" }],
        ["Theme: atom one dark", "app.theme", { name: "atom-one-dark" }],
      ];
  }
}

function menuIcon([, command, args, state]) {
  if (command === "priority-menu") return "mods/pied-piper-menu/flag.svg";
  if (command === "priority") return args.op === "remove" ? "mods/pied-piper-menu/flag-off.svg" : state?.on ? "mods/workspace-chrome/check.svg" : null;
  const name = command.endsWith(".close") ? "x" : command.endsWith(".rename") ? "square-pen" : command.endsWith(".new") ? "plus" : command === "worktree" ? "git-branch" : command === "app.help" ? "terminal" : command === "app.theme" ? "settings" : command === "pane.split" ? "panel-right" : command === "pane.zoom" ? "square" : "terminal";
  return `mods/workspace-chrome/${name}.svg`;
}

// The key bound to a command, for the hint on the right.
function shortcut(name, args) {
  // `pane.split:right` binds pane.split with { direction: "right" }.
  const value = args && Object.values(args)[0];
  const k = keys().find((b) => b.section === "global" && (b.action === name || b.action === `${name}:${value}`));
  return k ? k.keys : "";
}

export default class Menu extends View {
  init(_props, cx) {
    this.git = null;
    this.handle = cx.focus_handle();
    this.handle.focus();
    const p = props();
    if (p?.tab === "priority") setShared(SUB, p.overlay);
    const list = items(p, null);
    const on = list.findIndex((it) => it[3]?.on);
    this.at = on >= 0 ? on : Math.max(0, list.findIndex((it) => !it[3]?.off));
    const space = p?.tab === "space" && spaces().find((s) => s.id === p.target?.id);
    const folder = space && place(space);
    if (folder)
      cx.spawn(async (cx) => {
        this.git = await checkout(folder, space.machine).catch(() => null);
        cx.notify();
      });
  }

  async close() {
    if (shared(SUB) === props()?.overlay) setShared(SUB, null);
  }

  // Beside the Priority row, its first number level with it.
  openSub(it) {
    if (this.sub && shared(SUB) === this.sub) return;
    const b = this.subBounds;
    const at = b ? { x: b.x + b.width + 8, y: b.y - 6 } : "pointer";
    this.sub = openOverlay({ mod: "pied-piper-menu", kind: "popup", width: 170, height: 240, at, props: { tab: "priority", target: it[2], parent: props().overlay } });
  }

  closeSub() {
    if (this.sub) closeOverlay(this.sub);
    this.sub = null;
  }

  choose(i, cx) {
    const it = items(props(), this.git)[i];
    if (!it || it[3]?.off) return;
    if (it[1] === "priority-menu") return this.openSub(it);
    this.closeSub();
    closeOverlay(props()?.overlay);
    if (props()?.parent) closeOverlay(props().parent);
    if (it[1] === "priority") prioritize(it[2]);
    else if (it[1] === "worktree") openOverlay({ mod: "worktree", kind: "dialog", ...(it[2].action === "open" ? { width: 560, height: 480 } : { width: 440, height: 260 }), props: it[2] });
    else run(it[1], it[2]);
  }

  step(list, dir) {
    for (let k = 1; k <= list.length; k++) {
      const j = (this.at + dir * k + list.length * k) % list.length;
      if (!list[j][3]?.off) return (this.at = j);
    }
  }

  render(cx) {
    const t = theme();
    const p = props();
    const list = items(p, this.git);
    const pri = (c) => c === "priority" || c === "priority-menu";
    return v_flex()
      .id("menu")
      .track_focus(this.handle)
      .w_full()
      .min_h(0)
      .p(5)
      .bg(t.popover)
      .text_size(12.8)
      .on_key_down((e, cx) => {
        if (e.key === "down") this.step(list, 1);
        else if (e.key === "up") this.step(list, -1);
        else if (e.key === "enter") this.choose(this.at, cx);
        else if (e.key === "right" && list[this.at]?.[1] === "priority-menu") this.openSub(list[this.at]);
        else if (e.key === "escape" || (e.key === "left" && p?.tab === "priority")) closeOverlay(p.overlay);
        else return;
        cx.notify();
      })
      .when(p?.tab === "agent", (el) => el.child(h_flex().h(24).pl(31).items_center().text_size(11).text_color(t.dim).child("Priority")))
      .children(
        list.map((it, i) => {
          const st = it[3] ?? {};
          const icon = menuIcon(it);
          return v_flex()
            .when(i > 0 && ((pri(list[i - 1][1]) && !pri(it[1])) || (it[1] === "priority" && it[2].op === "remove") || it[1].endsWith(".close") || it[1] === "app.help" || (it[1] === "app.theme" && list[i - 1][1] !== "app.theme")), el => el.child(div().mx(7).my(4).h(1).bg(t.border)))
            .child(h_flex()
            .id(`mi-${i}`)
            .h(31)
            .px(8)
            .gap(9)
            .rounded(7)
            .items_center()
            .justify_between()
            .text_color(st.off ? t.dim : t.foreground)
            .when(i === this.at, (el) => el.bg(t.selected))
            .when(!st.off, (el) => el.hover((s) => s.bg(t.hover)).on_click((_e, cx) => this.choose(i, cx)))
            .when(it[1] === "priority-menu", (el) => el
              .on_mouse_down("left", (e) => { this.subBounds = e.bounds ?? this.subBounds; })
              .on_mouse_move((e, cx) => {
                this.subBounds = e.bounds;
                this.at = i;
                this.openSub(it);
                cx.notify();
              }))
            .when(it[1] !== "priority-menu" && p?.tab !== "priority", (el) => el.on_hover((h) => h && this.closeSub()))
            .child(icon ? svg(icon).size(14).flex_none().text_color(t.muted) : div().size(14).flex_none())
            .child(div().flex_1().child(it[0]))
            .child(it[1] === "priority-menu" ? svg("mods/workspace-chrome/chevron-right.svg").size(12).flex_none().text_color(t.dim) : div().text_size(11).text_color(t.dim).child(shortcut(it[1], it[2]))));
        }),
      );
  }
}
