// Each space's tabs in priority order, in Herdr's own tab order (tab.move), so
// Cmd+1–9 and tab cycling follow it, in every space, not only the shown one. A
// tab's priority is the best (lowest) number among the agents in it (shared
// "pied-piper.priority" agents, by pane); a space's own number doesn't order its
// tabs. Prioritized tabs come first, by number; the rest follow in the order
// they're in, and drag freely among themselves. Only the office's copy of
// spaces.js moves tabs (TabOrder); the tab bar's drag (tabs.js) asks dropIndex
// where a drop may land. No imports, so node can test it.

// An agent's number goes with the agent, as in pied-piper-menu's kept(): a pane whose
// agent exited and left a shell holds none.
const live = (p) => p.status != null || Boolean(p.program?.agent);

// Tab id -> its number, for tabs holding a prioritized agent. `panes`: panes().
export function tabRanks(panes, entries) {
  const held = new Map((entries ?? []).filter((e) => e && typeof e.n === "number" && e.n > 0).map((e) => [e.pane, e.n]));
  const ranks = new Map();
  for (const p of panes ?? []) {
    const n = held.get(p.pane);
    if (n === undefined || !p.tab || !live(p)) continue;
    if (!(ranks.get(p.tab) <= n)) ranks.set(p.tab, n);
  }
  return ranks;
}

// Tab ids in the order they belong in: by number, then (ties, and every tab
// without one, last) the order they're in now.
export function tabTarget(ids, ranks) {
  const rank = (id) => ranks.get(id) ?? Infinity;
  return ids.map((id, i) => ({ id, i })).sort((x, y) => (rank(x.id) === rank(y.id) ? x.i - y.i : rank(x.id) - rank(y.id))).map((x) => x.id);
}

// The tab.move calls that turn `order` into `target`: each index from 1, counting
// the moves before it. Only tabs moving forward are moved, one call each.
export function tabMoves(order, target) {
  const now = [...order];
  const moves = [];
  for (let i = 0; i < target.length; i++) {
    if (now[i] === target[i]) continue;
    const from = now.indexOf(target[i]);
    if (from < 0) continue;
    moves.push({ id: target[i], index: i + 1 });
    now.splice(i, 0, now.splice(from, 1)[0]);
  }
  return moves;
}

// Where the tab at `from` (from 0) lands when dropped on position `to`: where the
// ordering would put it after the drop. A prioritized tab dropped out of order
// stays where it was; one without a number dropped among the prioritized lands
// first after them.
export function dropIndex(ids, ranks, from, to) {
  const moved = [...ids];
  moved.splice(to, 0, moved.splice(from, 1)[0]);
  return tabTarget(moved, ranks).indexOf(ids[from]);
}

// A space's moves get SETTLE ms for their echo before its order is looked at
// again: an attempted write can lose a sync conflict, and another machine's echo
// takes a moment. Coming undone again (the same order wanted), the wait doubles,
// and after TRIES batches that space is left as it is until something changes:
// the numbers, its tabs, or its order being right for CALM.
const SETTLE = 1000;
const TRIES = 5;
const CALM = 60000;

export class TabOrder {
  constructor() {
    this.tried = new Map(); // space id -> { want: its target, tries: batches after it, at: the last one }
    this.out = false; // a space was out of order and not given up at the last look
    this.next = Infinity; // when to look again while one is
    this.moves = 0; // tab.move calls made, for tests
  }

  // Looking again is due: out of order, and the last batch has had its time.
  due(now) {
    return this.out && now >= this.next;
  }

  // Looks at every space and moves the tabs that are out of order, unless that
  // space's last batch is still settling. Spaces on a machine whose layout isn't
  // ready (asleep, loading) stay as they are. Returns the number of moves made.
  step({ spaces, panes, entries, machines, now, run }) {
    const ready = new Set((machines ?? []).filter((m) => m.layout === "ready").map((m) => m.name ?? null));
    const ranks = tabRanks(panes, entries);
    const ids = new Set();
    let made = 0;
    this.out = false;
    this.next = Infinity;
    for (const w of spaces ?? []) {
      ids.add(w.id);
      if (!ready.has(w.machine ?? null)) continue;
      const order = (w.tabs ?? []).map((c) => c.id);
      const target = tabTarget(order, ranks);
      const moves = tabMoves(order, target);
      const s = this.tried.get(w.id);
      if (!moves.length) {
        if (s && now - s.at >= CALM) this.tried.delete(w.id);
        continue;
      }
      const want = JSON.stringify(target);
      const again = s?.want === want;
      if (again && s.tries >= TRIES) continue;
      this.out = true;
      const wait = again ? SETTLE * 2 ** (s.tries - 1) : s ? SETTLE : 0;
      if (now - (s?.at ?? 0) < wait) {
        this.next = Math.min(this.next, s.at + wait);
        continue;
      }
      for (const m of moves) run("tab.move", m);
      const tries = again ? s.tries + 1 : 1;
      this.tried.set(w.id, { want, tries, at: now });
      this.next = Math.min(this.next, now + SETTLE * 2 ** (tries - 1));
      made += moves.length;
    }
    for (const id of this.tried.keys()) if (!ids.has(id)) this.tried.delete(id);
    this.moves += made;
    return made;
  }
}
