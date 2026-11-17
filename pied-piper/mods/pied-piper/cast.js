// The cast, and who plays which agent. Each agent is cast by the model it runs,
// in tiers: the top models (Fable, Opus, GPT Astra) are Richard, Gilfoyle and
// Dinesh; Sol is Jian-Yang and Carla; any other model Erlich and Big Head. An
// agent takes the first free character of its own tier, then of each tier
// below it (a top model: Sol's, then the other models'), then of the overflow,
// the rest in CAST order, Jared to Ron; with all of those full, its own tier's
// least played. An agent whose model isn't known (not read yet, or a program
// nobody reads) goes straight to the overflow. spaces.js reads the models from
// each agent's own log (heard()).
//
// A character is chosen only when a session starts, or when its model changes
// to another group before the session's first message. Nothing else moves it:
// an agent that spilled into a lower tier or the overflow stays there when a
// character above frees up. At the first message it is fixed for the rest of
// the session, whatever happens after. A new session in the terminal (a new
// or resumed one, /clear, another agent started there) is cast again: it keeps
// its character if its way down the tiers could give it that one now, else
// takes another.
//
// Each character is drawn seated at their own desk, facing you, in four poses
// (seats/<key>-<pose>.png), in their own bed in the same four (beds/), and as
// a face (cast/<key>-head.png); art/generate.py draws them all.

import { agents, shared, setShared } from "herdr";
import { art } from "./ui.js";

export const CAST = [
  { key: "richard", name: "Richard", full: "Richard Hendricks" },
  { key: "gilfoyle", name: "Gilfoyle", full: "Bertram Gilfoyle" },
  { key: "dinesh", name: "Dinesh", full: "Dinesh Chugtai" },
  { key: "jared", name: "Jared", full: "Jared Dunn" },
  { key: "erlich", name: "Erlich", full: "Erlich Bachman" },
  { key: "bighead", name: "Big Head", full: "Nelson “Big Head” Bighetti" },
  { key: "monica", name: "Monica", full: "Monica Hall" },
  { key: "jianyang", name: "Jian-Yang", full: "Jian-Yang" },
  { key: "gavin", name: "Gavin", full: "Gavin Belson" },
  { key: "russ", name: "Russ", full: "Russ Hanneman" },
  { key: "laurie", name: "Laurie", full: "Laurie Bream" },
  { key: "peter", name: "Peter Gregory", full: "Peter Gregory" },
  { key: "jack", name: "Jack Barker", full: "“Action” Jack Barker" },
  { key: "fiona", name: "Fiona", full: "Fiona" },
  { key: "denpok", name: "Denpok", full: "Denpok" },
  { key: "carla", name: "Carla", full: "Carla Walton" },
  { key: "ron", name: "Ron", full: "Ron LaFlamme" },
];

const BY_KEY = new Map(CAST.map((c) => [c.key, c]));

// The tiers: who plays which models, each in CAST order. "none", the overflow:
// everyone in no tier, and the group of a model not known.
const NAMED = {
  top: ["richard", "gilfoyle", "dinesh"],
  sol: ["jianyang", "carla"],
  other: ["erlich", "bighead"],
};
const GROUPS = { ...NAMED, none: CAST.map((c) => c.key).filter((k) => !Object.values(NAMED).flat().includes(k)) };
const GROUP_OF = Object.fromEntries(Object.entries(GROUPS).flatMap(([g, keys]) => keys.map((k) => [k, g])));
// Where an agent of each group looks for a character, in order: its own tier,
// the tiers below it, then the overflow. A model not known: the overflow only.
const CASCADE = {
  top: ["top", "sol", "other", "none"],
  sol: ["sol", "other", "none"],
  other: ["other", "none"],
  none: ["none"],
};

// A model's group, by the words in its name in any case: "claude-opus-5-5",
// "Opus 5.5", "GPT-6-Astra", "gpt-6.1-sol".
export function group(model) {
  if (!model) return "none";
  const words = String(model).toLowerCase().match(/[a-z]+/g) ?? [];
  if (words.some((w) => w === "fable" || w === "opus" || w === "astra")) return "top";
  return words.includes("sol") ? "sol" : "other";
}

// The agents spaces.js reads the logs of, by Herdr's program key (Claude Code
// also reports itself as "claude-code").
export const LOGGED = new Set(["copilot", "claude", "codex"]);
export const tool = (k) => {
  const key = k.program?.key ?? k.agent ?? k.app;
  return key === "claude-code" ? "claude" : key;
};

// { [terminal address]: role }, a role being
//   c     the character's key
//   at    when it was last seen, ms
//   x     what spaces.js last read of the agent (heard())
//   s     the session c was cast for, as x.s
//   g     the group of the model c was cast for (the model's, not c's tier)
//   lock  true once that session's first message was seen
//   was   the sessions before it, so a log read again can't bring one back
const KEY = "pied-piper.cast";
const DAY = 86400000;

// What spaces.js read of the agent at `address`:
//   s  its session, "<program>:<pid>|<log>"; the log part is empty until there is one
//   n  the model it runs now, null if not known
//   k  true once the session's first message was seen
//   l  the model at that message
export function heard(address, x) {
  const roles = shared(KEY) ?? {};
  const r = roles[address];
  const was = r?.x;
  // A model read before in this session stays known when a read finds none.
  if (x.n == null && was?.s === x.s) x = { ...x, n: was.n };
  if (was && was.s === x.s && was.n === x.n && was.k === x.k && was.l === x.l) return;
  setShared(KEY, { ...roles, [address]: { ...r, at: r?.at ?? Date.now(), x } });
}

// What's known of agent `a`: its program's read, or for a program nobody
// reads, one session with no model. Null: not read yet.
function facts(a, r) {
  const t = tool(a);
  if (!LOGGED.has(t)) return { s: `${t}:|`, n: null, k: false, l: null };
  return r.x?.s?.startsWith(`${t}:`) ? r.x : null;
}

// How session `s` stands to the one role `r` was cast for: "same"; also "same"
// when the process just got its log (Codex writes one at the first message);
// "wait" when it has none now, or one it had before; else "new".
function relate(r, s) {
  if (r.s === undefined) return "new";
  if (r.s === s) return "same";
  if ((r.was ?? []).includes(s)) return "wait";
  const [p, log] = split(r.s), [np, nlog] = split(s);
  if (p === np && !log) return "same";
  if (p === np && !nlog) return "wait";
  return "new";
}
const split = (s) => {
  const i = s.indexOf("|");
  return i < 0 ? [s, ""] : [s.slice(0, i), s.slice(i + 1)];
};

// A character for group `want`, given how many agents hold each (`held`): the
// first free one down its cascade, else its own group's least played.
function pick(want, held) {
  const free = (k) => !held.get(k);
  const n = (k) => held.get(k) ?? 0;
  for (const g of CASCADE[want]) {
    const k = GROUPS[g].find(free);
    if (k) return k;
  }
  return GROUPS[want].reduce((best, k) => (n(k) < n(best) ? k : best));
}

// The roles after looking at `list` (agents()) with `before` stored, at `now`.
// Pure; casting() stores what changed.
export function assign(list, before, now) {
  const roles = { ...before };
  const held = new Map();
  const hold = (k) => held.set(k, (held.get(k) ?? 0) + 1);
  const open = []; // agents to cast, in list order: { address, want, role }
  for (const a of list) {
    const r = before[a.address] ?? {};
    const has = BY_KEY.has(r.c);
    const x = facts(a, r);
    const rel = x ? relate(r, x.s) : "wait";
    if (has && rel === "wait") {
      hold(r.c);
      continue;
    }
    const want = x ? group(x.k ? x.l : x.n) : "none";
    const role = x ? { ...r, s: x.s, g: want, lock: Boolean(x.k) } : { ...r, g: want, lock: false };
    if (x && rel === "new" && r.s !== undefined) role.was = [...(r.was ?? []), r.s].slice(-4);
    // Fixed once its session's first message is in; before that, kept while
    // its model stays in the group it was cast for, from whichever tier.
    if (has && rel === "same" && (r.lock || r.g === want)) {
      roles[a.address] = r.lock ? { ...r, s: x.s } : role;
      hold(r.c);
      continue;
    }
    open.push({ address: a.address, want, role });
  }
  // Those being cast keep their character if their cascade could give it to
  // them now: it is free and on their way down, and every tier above it on
  // that way is full. Not only a tier's first free one: that order is for
  // newcomers and never moves anyone. Again until no one more keeps theirs:
  // one keeping a character can fill a tier another has to look past.
  const full = (g) => GROUPS[g].every((k) => held.get(k));
  for (let kept = true; kept; ) {
    kept = false;
    for (const o of open) {
      const c = o.role.c, way = CASCADE[o.want], i = way.indexOf(GROUP_OF[c]);
      if (!o.pick && BY_KEY.has(c) && i >= 0 && !held.get(c) && way.slice(0, i).every(full)) {
        hold((o.pick = c));
        kept = true;
      }
    }
  }
  for (const o of open) if (!o.pick) hold((o.pick = pick(o.want, held)));
  for (const o of open) roles[o.address] = { ...o.role, c: o.pick, at: now };
  // Seen today; gone and old ones dropped (the list alone is empty right after a start).
  const live = new Set(list.map((a) => a.address));
  for (const [address, role] of Object.entries(roles)) {
    if (live.has(address)) {
      if (!(now - role.at <= DAY)) roles[address] = { ...role, at: now };
    } else if (!(now - role.at <= 14 * DAY)) delete roles[address];
  }
  const dirty = Object.keys(roles).length !== Object.keys(before).length
    || Object.keys(roles).some((k) => JSON.stringify(roles[k]) !== JSON.stringify(before[k]));
  return { roles, dirty };
}

// Every agent's role, casting the agents that need one.
export function casting(list = agents()) {
  const { roles, dirty } = assign(list, shared(KEY) ?? {}, Date.now());
  if (dirty) setShared(KEY, roles);
  return roles;
}

// The character playing the agent at `address`, or null.
export const who = (address, roles) => BY_KEY.get(roles?.[address]?.c) ?? null;

// What a character does about its agent's status: works with the laptop open,
// raises a hand when blocked, cheers when done. Idle sits with it shut.
const POSE = { working: "work", blocked: "blocked", done: "done" };

// The character at their desk, 124x80. To animate one later, save its frames
// as an animated image under the same name: image() plays those by itself.
export const seat = (c, status) => art(`seats/${c.key}-${POSE[status] ?? "idle"}.png`, 124, 80);

// In the bedroom they are on their bunk instead (beds/<key>-<pose>.png, the
// same size): cross-legged with the laptop on their lap, shut when idle as
// at a desk.
export const bed = (c, status) => art(`beds/${c.key}-${POSE[status] ?? "idle"}.png`, 124, 80);

// The face, for a tab, a pane header or a toast. 32 shows its pixels whole,
// and so does 16.
export const head = (c, size = 32) => art(`cast/${c.key}-head.png`, size, size);

// Pied Piper's own sign, 24px: the home folder's space and the personal one
// (~/personal) hang it. Every other space's sign is its initial (spaces.js).
export const piedPiper = (size = 24) => art("world/co-piedpiper.png", size, size);
