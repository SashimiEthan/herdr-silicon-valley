// The sidebar's lists of spaces, as two rooms of the hostel at night. A
// block shows one list, by props().list: "priority" is the office, spaces
// holding a priority (theirs or an agent's) by the best one; "inactive" is the
// bedroom, the rest A–Z, grouped by machine when more than one is known. A
// list is one wall, papered edge to edge (world/wall-*.png, with a few things
// hung at its top); its rows scroll over the wall and all that hangs on it, up
// to its top trim, while the wall stays put; only the trim and the room's name
// plate (and the bedroom's "+") stay in front of them. A space is
// one of the show's companies, with its sign; after its name, only what's
// unusual in the repo its first terminal is in now (branch, ahead/behind),
// never the repo's own name: a space named otherwise was renamed. Each
// space's agents are nested under it, ranked first then A–Z: the character
// playing each (cast.js), at their desk in the office and on their bunk in
// the bedroom, posed by the agent's status, beside the agent's name. Then
// their sub-agents, and the subagents Copilot, Claude Code and Codex run
// inside themselves. Click to switch, right-click for its menu and priority.
// Priorities are the ones pied-piper-menu sets: both read and write shared
// "pied-piper.priority". Double-clicking the boundary between the two rooms makes
// the bedroom as tall as its rows, once (`fitToRows`).

import { div, svg, image } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { spaces, machines, panes, agents, terminals, focused, run, openOverlay, exec, hc, theme, props, shared, setShared, setAgentOrder, watchFolder, window, home, layout, checking } from "herdr";
import { FONT, TEXT, ROOMS, art, pix, mark, toolMark, narrow, toggleSidebar } from "./ui.js";
import { casting, who, seat, bed, piedPiper, heard, tool, LOGGED } from "./cast.js";
import { TabOrder } from "./order.js";
// Where each picture's furniture stands at the left, in art pixels (art/generate.py writes them).
import DESK_LEGS from "./seats/legs.js";
import BUNK_LEGS from "./beds/legs.js";

// Subagents that run inside an agent's own process (Copilot, Claude Code, Codex)
// never reach Herdr as terminals: read them from that agent's own log. One script per
// machine; per terminal, its log (found by the process's pid) from the last offset on,
// as events: [id, "start", name, tooltip], [id, "run" | "idle" | "cancel"],
// [id, "fail", error], ["", "reset"]. With them, the agent's model for cast.js:
// s its session (its log), n the model now, k whether the session's first message
// is in, l the model then; ms is the reader's own state, handed back next time.
const READ_SUBAGENTS = String.raw`
import sys, json, os, glob, re, time, subprocess

def flag(argv, *names):
    # The value given to an option, as "--x v" or "--x=v".
    for i, a in enumerate(argv):
        for n in names:
            if a == n and i + 1 < len(argv):
                return argv[i + 1]
            if a.startswith(n + "="):
                return a[len(n) + 1:]
    return None

def config(argv, key):
    # A Codex "-c key=value" override.
    for i, a in enumerate(argv):
        v = a[2:] if a.startswith("-c") and len(a) > 2 else argv[i + 1] if a in ("-c", "--config") and i + 1 < len(argv) else None
        if v and v.split("=", 1)[0].strip() == key and "=" in v:
            return v.split("=", 1)[1].strip()
    return None

def lines(path, o):
    # Whole lines past offset o, each with the offset after it.
    with open(path, "rb") as f:
        f.seek(o)
        for line in f:
            if not line.endswith(b"\n"):
                break
            o += len(line)
            yield line, o

def iso(ms):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ms / 1000)) + ".%03dZ" % (ms % 1000)

def started(pid):
    # When the process started (ms): older lines are an earlier process's.
    r = subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], capture_output=True, text=True, timeout=5)
    return int(time.mktime(time.strptime(r.stdout.strip(), "%a %b %d %H:%M:%S %Y"))) * 1000

def first_line(text, n=200):
    for l in (text or "").splitlines():
        l = re.sub(r"[*#\x60>]+", "", l).strip()
        if l:
            return l if len(l) <= n else l[:n - 1] + "…"
    return ""

# Copilot: the session folder by the inuse.<pid>.lock it holds (several after /new:
# the newest is the session now). Its model: the session's start model and each
# change of it (the main agent's: a subagent's carry its agentId), locked at the
# first user message since the process started. Copilot writes none of that down
# before the first message: till then its own log, which names each model it
# switches to, says which.
def copilot_log(pid, st):
    # The last model Copilot's log for process pid names, read on from where st left it.
    logs = glob.glob(os.path.expanduser("~/.copilot/logs/process-*-%s.log" % pid))
    if not logs:
        return st
    cur = max(logs, key=os.path.getmtime)
    ino, m = os.stat(cur).st_ino, st.get("m")
    o = st.get("o", 0) if st.get("i") == ino and os.path.getsize(cur) >= st.get("o", 0) else 0
    parts = [(cur, o)]
    if st.get("i") and st["i"] != ino:
        # Rotated: the rest of what it read is in a numbered log now.
        old = [f for f in glob.glob(cur[:-4] + ".*.log") if os.stat(f).st_ino == st["i"]]
        parts = [(old[0], st.get("o", 0))] + parts if old else parts
    for path, o in parts:
        with open(path, "rb") as f:
            f.seek(o)
            data = f.read()
        data = data[:data.rfind(b"\n") + 1]
        for x in re.finditer(rb'"new_model": "([^"]+)"|managed default model: (\S+)', data):
            m = (x.group(1) or x.group(2)).decode()
    return {"i": ino, "o": o + len(data), "m": m}

def copilot(q):
    locks = glob.glob(os.path.expanduser("~/.copilot/session-state/*/inuse.%s.lock" % q["p"]))
    if not locks:
        return None
    here = os.path.dirname(max(locks, key=os.path.getmtime))
    d = here if os.path.exists(os.path.join(here, "events.jsonl")) else None
    o = q["o"] if d and d == q.get("d") else 0
    st = q.get("ms") or {}
    ms = st if o else {}
    n, k, l = ms.get("n"), ms.get("k", False), ms.get("l")
    since = iso(started(q["p"]))
    ev = []
    for line, o in lines(os.path.join(d, "events.jsonl"), o) if d else ():
        head = line[:40]
        if b'"session.start"' in head or b'"session.resume"' in head:
            if b'"session.resume"' in head:
                ev.append(["", "reset"])
            try:
                n = (json.loads(line).get("data") or {}).get("selectedModel") or n
            except ValueError:
                pass
            continue
        if b'"session.model_change"' in head:
            if b'"agentId"' not in line:
                try:
                    n = (json.loads(line).get("data") or {}).get("newModel") or n
                except ValueError:
                    pass
            continue
        if b'"user.message"' in head and b'"agentId"' not in line:
            # Its time is the line's last: the message itself may hold others.
            at = line.rfind(b'"timestamp":"')
            if not k and at >= 0 and line[at + 13:at + 37].decode("ascii", "replace") >= since:
                k, l = True, n
            continue
        if not (b'"subagent.' in head or b'"user.message"' in head or b'"assistant.message"' in head) or b'"agentId"' not in line:
            continue
        try:
            e = json.loads(line)
        except ValueError:
            continue
        a, t, x = e.get("agentId"), e.get("type"), e.get("data") or {}
        if not a:
            continue
        if t == "subagent.started":
            ev.append([a, "start", x.get("agentDisplayName") or x.get("agentName") or "Subagent", x.get("agentDescription") or ""])
        elif t == "subagent.completed":
            ev.append([a, "cancel" if x.get("cancelled") else "idle"])
        elif t == "subagent.failed":
            ev.append([a, "fail", str(x.get("error") or "")[:300]])
        elif t == "user.message":
            ev.append([a, "run"])
        elif t == "assistant.message":
            ev.append([a, "run" if x.get("toolRequests") else "idle"])
    log = st.get("p") or {}
    if not k:
        log = copilot_log(q["p"], log)
    return {"d": d, "o": o, "e": ev, "s": os.path.basename(here), "n": n if k else log.get("m") or n, "k": k, "l": l,
            "ms": {"n": n, "k": k, "l": l, "p": log}}

# Claude Code: <config>/sessions/<pid>.json names the session (a new one after /clear
# or /resume); its transcript is <config>/projects/<folder>/<session>.jsonl. A subagent
# is an Agent call; it ends with the call's result, or, run in the background, with
# a task notification; SendMessage can wake it again. Its id is the call's.
# Its model: locked at the first reply since the process started, by the model that
# wrote it. Before that, the one claude-model.sh saved for the session if its status
# line runs, else the last /model, else --model, else the settings' default.
MODELS = os.path.expanduser("~/.local/state/herdr-pied-piper/claude-models")

def claude_model(sid, root, argv, picked):
    try:
        with open(os.path.join(MODELS, sid)) as f:
            m = f.read().strip()
        if m:
            return m
    except OSError:
        pass
    if picked:
        return picked
    m = flag(argv, "--model")
    if m:
        return m
    try:
        with open(os.path.join(root, "settings.json")) as f:
            return json.load(f).get("model") or None
    except (OSError, ValueError, AttributeError):
        return None

def claude(q):
    roots = {os.path.expanduser("~/.claude")} | set(glob.glob(os.path.expanduser("~/.claude-*")))
    if os.environ.get("CLAUDE_CONFIG_DIR"):
        roots.add(os.environ["CLAUDE_CONFIG_DIR"])
    pids = [f for f in (os.path.join(r, "sessions", "%s.json" % q["p"]) for r in roots) if os.path.exists(f)]
    if not pids:
        return None
    pf = max(pids, key=os.path.getmtime)
    with open(pf) as f:
        s = json.load(f)
    sid, root = s.get("sessionId"), os.path.dirname(os.path.dirname(pf))
    if not sid:
        return None
    if q.get("pr"):
        # Saved models of sessions two weeks quiet.
        for f in glob.glob(os.path.join(MODELS, "*")):
            try:
                if time.time() - os.path.getmtime(f) > 14 * 86400:
                    os.remove(f)
            except OSError:
                pass
    d = q.get("d")
    if not (d and os.path.basename(d) == sid + ".jsonl" and os.path.exists(d)):
        found = glob.glob(os.path.join(root, "projects", "*", sid + ".jsonl"))
        d = max(found, key=os.path.getmtime) if found else None
    o = q["o"] if d and d == q.get("d") else 0
    ms = (q.get("ms") or {}) if o else {}
    picked, k, l = ms.get("p"), ms.get("k", False), ms.get("l")
    argv = q.get("v") or []

    def model():
        n = claude_model(sid, root, argv, picked)
        return {"s": sid, "n": n, "k": k, "l": l, "ms": {"p": picked, "k": k, "l": l}}

    if not d:
        return dict(d=None, o=0, e=[], **model())
    since = iso(s["startedAt"]) if s.get("startedAt") else ""
    live = set(q.get("w") or [])

    def call(agent):
        # The Agent call that started an agent, from the agent's sidecar.
        try:
            with open(os.path.join(d[:-6], "subagents", "agent-%s.meta.json" % agent)) as f:
                return json.load(f).get("toolUseId")
        except (OSError, ValueError):
            return None

    ev = []
    for line, o in lines(d, o):
        if not k and b'"isSidechain":false' in line[:300]:
            # The first reply: its model, unless Claude Code wrote it itself.
            if b'"role":"assistant"' in line[:400]:
                e = json.loads(line)
                m = (e.get("message") or {}).get("model")
                if e.get("type") == "assistant" and m and m != "<synthetic>" and e.get("timestamp", "") >= since:
                    k, l = True, m
            # A /model before it.
            elif b"<local-command-stdout>" in line[:600] and (b"Set model to " in line or b"Kept model as " in line):
                e = json.loads(line)
                c = (e.get("message") or {}).get("content")
                p = re.search(r"(?:Set model to|Kept model as) \x60?([^\x60<\n]+?)\x60?(?: and | for |<|$)", c if isinstance(c, str) else "")
                if p and e.get("timestamp", "") >= since:
                    picked = p.group(1).strip()
        if line.startswith(b'{"type":"queue-operation","operation":"enqueue"'):
            if b"<task-notification>" not in line[:300]:
                continue
            e = json.loads(line)
            n = e.get("content") or ""
            # After a SendMessage the notice carries that call's id: the agent's id leads back.
            u = (re.search(r"<tool-use-id>([^<]+)<", n) or [None, None])[1]
            if u not in live:
                u = call((re.search(r"<task-id>([^<]+)<", n) or [None, ""])[1])
            if u not in live or e.get("timestamp", "") < since:
                continue
            st = (re.search(r"<status>([^<]*)<", n) or [None, ""])[1]
            sm = (re.search(r"<summary>([^<]*)<", n) or [None, ""])[1]
            # Waiting on its own background work: it reports again when that ends.
            if st == "completed" and "waiting on its own background work" in sm:
                continue
            live.discard(u)
            if st == "failed":
                ev.append([u, "fail", sm.split("failed: ", 1)[-1][:300]])
            else:
                ev.append([u, "cancel" if st == "killed" else "idle"])
        elif b'"role":"assistant"' in line[:400] and (b'"name":"Agent"' in line or b'"name":"Task"' in line):
            e = json.loads(line)
            if e.get("timestamp", "") < since or e.get("isSidechain"):
                continue
            for b in (e.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in ("Agent", "Task"):
                    x = b.get("input") or {}
                    kind = x.get("subagent_type") or "general-purpose"
                    tip = first_line(x.get("prompt"))
                    ev.append([b["id"], "start", x.get("description") or x.get("name") or kind, kind + (": " + tip if tip else "")])
                    live.add(b["id"])
        elif b'"type":"user"' in line[:300] and (b'"resumedAgentId"' in line or any(('"tool_use_id":"%s"' % i).encode() in line for i in live)):
            e = json.loads(line)
            if e.get("timestamp", "") < since or e.get("isSidechain"):
                continue
            r = e.get("toolUseResult")
            if isinstance(r, dict) and r.get("resumedAgentId"):
                u = call(r["resumedAgentId"])
                if u:
                    ev.append([u, "run"])
                    live.add(u)
                continue
            for b in (e.get("message") or {}).get("content") or []:
                if not (isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") in live):
                    continue
                c = b.get("content")
                text = c if isinstance(c, str) else " ".join(i.get("text", "") for i in c or [] if isinstance(i, dict))
                if b.get("is_error"):
                    live.discard(b["tool_use_id"])
                    stopped = "interrupted" in text or "doesn't want to proceed" in text
                    ev.append([b["tool_use_id"], "cancel"] if stopped else [b["tool_use_id"], "fail", text.strip()[:300]])
                elif not isinstance(r, dict) or r.get("status") in (None, "completed"):
                    live.discard(b["tool_use_id"])
                    ev.append([b["tool_use_id"], "idle"])
                # Else it went on in the background: a notification ends it.
    return dict(d=d, o=o, e=ev, **model())

# Codex: the rollouts the process holds open (Herdr starts it with --no-daemon), its own
# being the one whose session is itself; a subagent has its own. Else, for a Codex
# run with its shared daemon, the thread named in the terminal's title, from its folder.
# Its model: locked at the first turn since the process started, by that turn's model.
# Before that (Codex writes nothing yet), the one at the end of the terminal's title
# when it shows one (Herdr starts it so, programs.json), else -m, else config.toml's.
def titled(argv, home):
    # Whether Codex puts its model in the terminal's title.
    v = config(argv, "tui.terminal_title")
    if v is None:
        try:
            with open(os.path.join(home, "config.toml")) as f:
                m = re.search(r'^\s*terminal_title\s*=\s*(\[[^\]]*\])', f.read(), re.M)
            v = m.group(1) if m else None
        except OSError:
            v = None
    return bool(v) and re.search(r'"model"', v) is not None

def codex_model(q, home):
    argv = q.get("v") or []
    title = re.sub(r"^[^\w]+", "", q.get("n") or "")
    if " | " in title and titled(argv, home):
        return title.rsplit(" | ", 1)[1].strip() or None
    m = flag(argv, "-m", "--model") or (config(argv, "model") or "").strip("\"'")
    if m:
        return m
    # config.toml: the profile's model, else the top one.
    profile = flag(argv, "-p", "--profile")
    try:
        with open(os.path.join(home, "config.toml")) as f:
            text = f.read()
    except OSError:
        return None
    table, top, mine = "", {}, None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("["):
            table = line.strip("[] ").replace('"', "")
            continue
        m = re.match(r'(model|profile)\s*=\s*"([^"]*)"', line)
        if not m:
            continue
        if table == "":
            top[m.group(1)] = m.group(2)
        elif m.group(1) == "model" and table == "profiles." + (profile or top.get("profile") or ""):
            mine = m.group(2)
    return mine or top.get("model")

def codex(q):
    home = os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex")
    since = started(q["p"])
    d = None
    r = subprocess.run(["lsof", "-a", "-p", str(q["p"]), "-Fn"], capture_output=True, text=True, timeout=5)
    mine = []
    for l in r.stdout.splitlines():
        if l.startswith("n") and "/rollout-" in l and l.endswith(".jsonl"):
            with open(l[1:], "rb") as f:
                head = f.read(600)
            m = re.search(rb'"session_id":"([^"]+)","id":"([^"]+)"', head)
            if m and m.group(1) == m.group(2):
                mine.append(l[1:])
    if mine:
        d = max(mine, key=os.path.getmtime)
    db = None
    try:
        import sqlite3
        dbs = sorted(glob.glob(os.path.join(home, "state_*.sqlite")))
        if dbs:
            db = sqlite3.connect("file:%s?mode=ro" % dbs[-1], uri=True, timeout=2)
    except Exception:
        db = None
    if not d and db and q.get("c"):
        # The title without the model Herdr has Codex add to it, then without its last part.
        title = re.sub(r"^[^\w]+", "", (q.get("n") or ""))
        if titled(q.get("v") or [], home):
            title = title.rsplit(" | ", 1)[0]
        name = title.rsplit(" | ", 1)[0].strip()
        rows = db.execute("select rollout_path, name from threads where cwd = ? and coalesce(thread_source, 'user') = 'user' and archived = 0 and updated_at_ms >= ? order by updated_at_ms desc", (q["c"], since)).fetchall()
        named = [p for p, n in rows if n and n == name]
        d = (named or [p for p, _ in rows] or [None])[0]
    if d and not os.path.exists(d):
        d = None
    o = q["o"] if d and d == q.get("d") else 0
    ms = (q.get("ms") or {}) if o else {}
    lk, lm = ms.get("k", False), ms.get("l")
    since, ev = iso(since), []
    for line, o in lines(d, o) if d else ():
        if not lk and b'"type":"turn_context"' in line[:120]:
            e = json.loads(line)
            if e.get("timestamp", "") >= since:
                lk, lm = True, (e.get("payload") or {}).get("model")
            continue
        if b'"SubAgentActivity"' not in line or not line.startswith(b'{"timestamp":"'):
            continue
        e = json.loads(line)
        x = ((e.get("payload") or {}).get("item")) or {}
        if x.get("type") != "SubAgentActivity" or e.get("timestamp", "") < since:
            continue
        a, k, path = x.get("agent_thread_id"), x.get("kind"), x.get("agent_path") or ""
        if not a:
            continue
        if k == "started":
            tip = path
            try:
                who = db.execute("select agent_nickname, agent_role from threads where id = ?", (a,)).fetchone() if db else None
                if who and who[0]:
                    tip = "%s%s · %s" % (who[0], " (%s)" % who[1] if who[1] else "", path)
            except Exception:
                pass
            ev.append([a, "start", path.rsplit("/", 1)[-1] or "Subagent", tip])
        elif k == "interacted":
            ev.append([a, "run"])
        elif k in ("completed", "interrupted"):
            # Interrupted, it waits for more work rather than ending.
            ev.append([a, "idle"])
    n = None if lk else codex_model(q, home)
    return {"d": d, "o": o, "e": ev, "s": d or "", "n": n or lm, "k": lk, "l": lm, "ms": {"k": lk, "l": lm}}

out = {}
for q in json.loads(sys.argv[1]):
    try:
        out[q["a"]] = {"copilot": copilot, "claude": claude, "codex": codex}[q.get("t", "copilot")](q)
    except Exception:
        pass
print(json.dumps(out))
`;

const clean = (s) => (s ?? "").replace(/^[^\p{L}\p{N}]+/u, "").trim();

function leadPanes(all) {
  const leads = new Map();
  for (const p of all) {
    if (!p.terminal) continue;
    const current = leads.get(p.tab);
    // First agent, else first focused terminal, else first terminal in the tab.
    if (!current || (!current.program?.agent && (p.program?.agent || (!current.focused && p.focused)))) leads.set(p.tab, p);
  }
  return leads;
}

// A terminal's title, without the model Herdr has Codex end its title with (programs.json).
const bare = (l) => (l?.program?.key === "codex" ? (l.title ?? "").replace(/ \| [^|]*$/, "") : l?.title);

function title(tab, l) {
  const prog = l?.program?.name;
  const live = clean(bare(l));
  // clean() would strip a path's leading ~ or /: test the title with only its status glyph gone.
  const path = /^[~/]|^[A-Za-z]:\\/.test((bare(l) ?? "").replace(/^[^\p{L}\p{N}~/]+/u, ""));
  const telling = live && live !== prog && !path && !live.includes("@") && live.toLowerCase() !== l?.program?.key;
  return (tab.name === prog || !tab.named) && telling ? live : tab.name;
}
// { spaces: [{ id, machine, n }], agents: [{ pane, machine, n }] }: one list of 1–5.
const PRIORITY = "pied-piper.priority";
// A section header's icon and gap.
const HEAD_ICON = 11;
const HEAD_GAP = 7;
// An office rank has 16px of wall on each side. Its ink starts 16 in from the
// sidebar's edge (the list's 8, RANK_LEFT, then the digit's own 1) and is 5
// wide, so the row's sign or desk starts at 37: OFFICE_INSET past the row's padding.
const RANK_LEFT = 7;
const OFFICE_INSET = 21;
// Rows stand apart, and a space's group (or a machine's) further from what's
// above it. Sub-agents stay tight under their agent, so its tree's lines reach it.
const ROW_GAP = 8;
const GROUP_GAP = 16;
// Bare wall under a list's last row, so the floor doesn't cover it.
const FLOOR_ROOM = 14;
// The band along a room's top with its name on a plate: a list's first row
// starts under it, and scrolled rows pass behind it.
const PLATE_BAND = 30;
// The trim along the top of each wall (art/decor.py's paper: the office's beam,
// the bedroom's white trim, each with its shadow and dark edge line), 4 art
// pixels deep: rows scroll up to its bottom edge and are clipped there, so it
// stays in front of them. The office's lamps hang 4px lower, like the signs, and
// rows pass in front of that part: a clip under them would cut rows off in bare wall.
const TRIM = { office: 8, bedroom: 8 };
// Herdr draws the boundary between the office and the bedroom and drags it
// itself, and tells a mod nothing about it. Its grip is 6px tall: the office's
// last 3px and the bedroom's first 3.
const GRIP = 3;
// Two presses there this close in time (ms; the system's own interval when it can
// be read) and space (px) are a double-click, even when the second one comes
// with a click_count of 1.
const DOUBLE_MS = 500;
const DOUBLE_SLOP = 4;
// Each list's heights in px, by props().list: the whole room, its scroll area,
// the scroll area's padding over its rows (`top`) and the rows in it. Module code
// is shared by the copies, so the bedroom reads the office's here; nothing is
// drawn from it.
const LIST_SIZE = {};
// How tall a list's room would be with no bare wall under its rows.
const fitted = (m) => m.room - m.list + m.top + m.rows + FLOOR_ROOM;
// Where the shown layout puts list `list`: its block and the column it's in.
function listBlock(node, list, parent = null) {
  const p = node?.content?.props;
  if (p?.role === "spaces" && p.list === list) return { node, parent };
  for (const child of node?.children ?? []) {
    const found = listBlock(child, list, node);
    if (found) return found;
  }
  return null;
}
const RANK = { blocked: 4, done: 3, working: 2, idle: 1 };
// A sub-agent without a pane isn't in agents(): its raw word, error counting as
// blocked. It's never done: it reports to its parent, and the parent's done is the news.
const kidStatus = (k, listed) => {
  const s = listed.get(k.address) ?? k.status;
  return s === "error" ? "blocked" : s === "done" ? "idle" : s;
};

function duration(ms) {
  const m = Math.floor(ms / 60000);
  if (m < 1) return "<1m";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  return h < 24 ? `${h}h` : `${Math.floor(h / 24)}d`;
}

// A program's icon from the app's table, for terminals no character plays: a one-color glyph or a picture.
function icon(p, size, color) {
  if (!p?.icon) return null;
  return p.tint ? svg(p.icon).size(size).flex_none().text_color(color) : image(p.icon).w(size).h(size).flex_none();
}

// Where a space is now: its first terminal's live folder, else where it was made.
// `ps`: panes(), read once by the caller (each read copies every pane).
function place(s, ps) {
  const tabs = new Set((s.tabs ?? []).map((c) => c.id));
  return ps.find((p) => tabs.has(p.tab) && p.cwd)?.cwd || s.folder;
}
const rowHeight = ({ tree }) => (tree ? 28 : 34);
const RAIL_CELL = 32;
const railCell = (el) => h_flex().flex_none().justify_center().child(el);
const where = (s, ps) => JSON.stringify([s.machine ?? null, place(s, ps)]);
const base = (path) => path.replace(/\/+$/, "").split("/").pop();
// Changes made outside Herdr (an editor's save, a commit in another app): looked
// for this often, in repos the list shows, while the window is in front.
const FALLBACK = 60000;

// A space's sign is its initial on its own color, the one kept for
// it (shared "space.colors"): one strong color per hue.
const MARK = { ansi6: "#22a99a", ansi3: "#e3814f", ansi4: "#5b8def", ansi5: "#8b7cf6", ansi2: "#3fae6a", ansi1: "#d9649a" };
const PALETTE = ["ansi6", "ansi3", "ansi4", "ansi5", "ansi2", "ansi1"];
// Pied Piper itself keeps the company's sign: the home folder's space, and the
// personal space (~/personal itself, not the folders in it), on this computer.
const trim = (path) => (path ?? "").replace(/\/+$/, "");
const isPiedPiper = (s) => {
  if (s.name === "~") return true;
  if (s.machine || !s.folder) return false;
  const f = trim(s.folder), h = trim(home());
  return f === h || f === `${h}/personal`;
};
// The first letter or digit of a space's name; of its repo or folder when the name has none (an emoji).
function initial(w, g) {
  for (const s of [w.name, g?.name, base(w.folder ?? "")]) {
    const m = (s ?? "").match(/[\p{L}\p{N}]/u);
    if (m) return m[0].toUpperCase();
  }
  return [...(w.name ?? "")][0] ?? "?";
}

// A space speaks up only when something in it needs you.
export function glyph(status) {
  return status === "blocked" || status === "done" ? "●" : "·";
}

export function tone(t, status) {
  return t[status] ?? t.unknown;
}

export default class Spaces {
  init(_props, cx) {
    this.git = {}; // where() -> { name, branch, ahead, behind, repo, linked }, null: not a repo
    this.checked = {}; // where() -> when it was last looked at
    this.unsure = new Set(); // where()s git couldn't answer for (a machine away)
    this.pending = new Set(); // where()s to look at next
    this.busy = {}; // pane -> an agent working or a program in front of its shell
    this.ready = {}; // machine -> its layout was readable at the last look
    this.at = {}; // space -> its where() at the last look
    this.watching = new Set(); // local repos' git folders
    // Spaces made while this runs wait (at most a moment) for their git, so a
    // worktree appears under its repo instead of jumping there.
    this.shown = new Set(spaces().map((s) => s.id));
    this.born = {};
    // The priority list also keeps the spaces' order and the agents' Cmd+] order.
    this.owner = props()?.list !== "inactive";
    // And each space's tabs in priority order (order.js).
    this.tabOrder = this.owner ? new TabOrder() : null;
    this.list = this.owner ? "priority" : "inactive";
    // This list's heights, for fitting the bedroom to its rows (LIST_SIZE).
    this.measured = LIST_SIZE[this.list] = {};
    // The bedroom's last press on the grip (gripPress), and the system's double-click interval.
    this.lastPress = null;
    this.doubleMs = DOUBLE_MS;
    // Which of the plate and the bedroom's "+" the pointer is on: rows scroll
    // under them, and the rows there don't light up or show a tooltip (`covered`).
    this.onPlate = new Set();
    this.covered = false;
    if (!this.owner && !checking() && window()?.platform === "macos") cx.spawn(async () => {
      try {
        const s = parseFloat((await exec("defaults", ["read", "-g", "com.apple.mouse.doubleClickThreshold"])).stdout);
        if (s >= 0.1 && s <= 5) this.doubleMs = s * 1000;
      } catch (_e) {}
    });
    this.inset = this.owner ? OFFICE_INSET : 0;
    this.roomName = this.owner ? "office" : "bedroom";
    this.room = ROOMS[this.roomName];
    this.machines = [];
    this.reconnecting = JSON.parse(localStorage.getItem("machines.reconnecting") ?? "{}");
    for (const state of Object.values(this.reconnecting)) state.busy = false;
    this.folded = new Set(JSON.parse(localStorage.getItem("machines.folded") ?? "[]"));
    this.refreshMachines(cx);
    cx.timer.every(15000, cx => this.refreshMachines(cx));
    // Refresh only when the refs could have changed (see `due`).
    cx.timer.every(250, (cx) => this.checkNew(cx));
    // Each agent's last state and when it changed (ms), kept across restarts.
    this.changed = JSON.parse(localStorage.getItem("changed") ?? "{}");
    this.foldedAgents = new Set();
    cx.timer.every(30000, (cx) => cx.notify());
    // Per Copilot, Claude Code or Codex terminal: its pid, log, offset and subagents by id.
    this.logs = new Map();
    this.openFinished = new Set();
    cx.timer.every(4000, (cx) => this.pollSubagents(cx));
    this.pollSubagents(cx);
  }

  // A terminal is read while it or a subagent works, once when its status
  // changes, and each minute; before its session's first message, every 10
  // seconds and when its title changes (Codex shows its model there).
  pollSubagents(cx) {
    if (this.polling) return;
    const now = Date.now();
    const live = terminals().filter((k) => k.state === "live" && LOGGED.has(tool(k)));
    // Gone, or running another of them now: start over.
    for (const [a, c] of this.logs) if (!live.some((k) => k.address === a && tool(k) === c.tool)) this.logs.delete(a);
    const titles = new Map(agents().map((a) => [a.address, a.title]));
    const due = live.filter((k) => {
      if (this.mine && !this.mine.has(k.address)) return false;
      const c = this.logs.get(k.address);
      return !c || k.status === "working" || c.running || c.status !== k.status || now - c.at > (c.k ? 60000 : 10000)
        || (!c.k && c.tool === "codex" && (titles.get(k.address) ?? c.title) !== c.sent);
    });
    if (!due.length) return;
    this.polling = true;
    cx.spawn(async (cx) => {
      let changed = false;
      const byMachine = new Map();
      for (const k of due) {
        const c = this.logs.get(k.address) ?? { tool: tool(k), subs: new Map(), offset: 0 };
        this.logs.set(k.address, c);
        c.status = k.status;
        c.at = now;
        try {
          if (!c.pid || now - c.pidAt > 60000) {
            const got = JSON.parse((await hc(["get", k.address, "--json"])).stdout || "{}");
            // Another process: its log is read afresh.
            if (c.pid && got.foreground?.pid !== c.pid) {
              Object.assign(c, { dir: null, offset: 0, ms: null, k: false, running: false });
              c.subs.clear();
            }
            c.pid = got.foreground?.pid;
            c.cwd = got.foreground?.cwd;
            c.argv = got.foreground?.argv;
            c.title = got.title;
            c.pidAt = now;
          }
        } catch (_e) {}
        if (!c.pid) continue;
        const m = k.address.includes("/") ? k.address.split("/")[0] : null;
        if (!byMachine.has(m)) byMachine.set(m, []);
        // Claude Code's reader needs the running ones' ids; Codex's, without its own log open, the folder and title.
        const working = [...c.subs.values()].filter((s) => s.status === "working").map((s) => s.id);
        c.sent = titles.get(k.address) ?? c.title;
        // Now and then, Claude Code's reader also drops the models claude-model.sh saved for old sessions.
        const prune = c.tool === "claude" && now - (this.pruned ?? 0) > 3600000;
        if (prune) this.pruned = now;
        byMachine.get(m).push({ a: k.address, t: c.tool, p: c.pid, d: c.dir, o: c.offset, w: working, c: c.cwd, n: c.sent, v: c.argv, ms: c.ms, pr: prune });
      }
      for (const [m, qs] of byMachine) {
        try {
          const r = await exec("python3", ["-c", READ_SUBAGENTS, JSON.stringify(qs)], { on: m, timeout: 20000 });
          const out = JSON.parse(r.stdout || "{}");
          for (const q of qs) if (q.a in out && this.applySubagents(q.a, out[q.a])) changed = true;
        } catch (_e) {}
      }
      this.polling = false;
      if (changed) cx.notify();
    });
  }

  // Folds new log events into the subagents; true if anything shown changed.
  applySubagents(addr, res) {
    const c = this.logs.get(addr);
    if (!c) return false;
    if (!res || res.d !== c.dir) {
      const had = c.subs.size > 0;
      c.subs.clear();
      c.dir = res?.d ?? null;
      c.offset = 0;
      c.running = false;
      if (!res) return had;
    }
    c.offset = res.o;
    for (const [id, kind, x, y] of res.e) {
      // A resume drops the old process's subagents without logging their end.
      if (kind === "reset") {
        c.subs.clear();
        continue;
      }
      if (kind === "start") {
        c.subs.set(id, { id, address: `${addr}#${id}`, via: addr, name: x, tip: y, status: "working" });
        continue;
      }
      const s = c.subs.get(id);
      if (!s) continue;
      // Cancelled: the parent stopped it, or its session ended.
      if (kind === "cancel") c.subs.delete(id);
      else if (kind === "fail") Object.assign(s, { status: "failed", err: x });
      else s.status = kind === "run" ? "working" : "idle";
    }
    c.running = [...c.subs.values()].some((s) => s.status === "working");
    // The model, for cast.js.
    c.ms = res.ms ?? null;
    c.k = Boolean(res.k);
    heard(addr, { s: `${c.tool}:${c.pid}|${res.s ?? ""}`, n: res.n ?? null, k: c.k, l: res.l ?? null });
    return res.e.length > 0;
  }

  // Stamps agents whose state changed. Done and idle count as one: looking at a
  // finished agent turns done into idle, and looking isn't the agent doing anything.
  track(list, now) {
    let dirty = false;
    for (const a of list) {
      const s = a.status === "done" ? "idle" : a.status;
      if (this.changed[a.address]?.s === s) continue;
      this.changed[a.address] = { s, at: now };
      dirty = true;
    }
    if (!dirty) return;
    // Gone and old: the list alone is empty right after a start.
    const listed = new Set(list.map((a) => a.address));
    for (const [k, c] of Object.entries(this.changed)) if (!listed.has(k) && now - c.at > 30 * 86400000) delete this.changed[k];
    localStorage.setItem("changed", JSON.stringify(this.changed));
  }

  // Live sub-agents of `addr`, depth first, each with the tree lines in front of it.
  // Then the subagents its own log names: running ones, and the finished ones under one row.
  tree(all, addr, lead = []) {
    const subs = [...(this.logs?.get(addr)?.subs.values() ?? [])];
    const finished = subs.filter((s) => s.status !== "working");
    const kids = [
      ...all.filter((k) => k.parent === addr && k.state === "live"),
      ...subs.filter((s) => s.status === "working"),
      ...(finished.length ? [{ address: `${addr}#finished`, status: "idle", finished, owner: addr }] : []),
    ];
    const open = this.openFinished?.has(addr);
    return kids.flatMap((k, i) => {
      const last = i === kids.length - 1;
      const below = [...lead, last ? "" : "│"];
      return [
        { t: k, lines: [...lead, last ? "└" : "├"], open },
        ...(k.finished
          ? k.finished.map((f, j) => ({ t: f, lines: [...below, j === k.finished.length - 1 ? "└" : "├"], hidden: !open }))
          : k.via ? [] : this.tree(all, k.address, below)),
      ];
    });
  }

  // `x`: where the tree's first line runs down. Each line stays inside its own
  // row, so a row's hover never shows the next one's: "│" and "├" run its whole
  // height, into the next row's line, "└" from its top to the elbow.
  subShell(t, id, lines, x) {
    const elbow = (el) => el.h(13).border_b(1).border_color(t.input);
    return h_flex()
      .id(id)
      .pl(x)
      .pr(8)
      .h(26)
      .flex_none()
      .gap(0)
      .items_center()
      .when(!this.covered, (el) => el.hover((s) => s.bg(this.room.hover)))
      .children(lines.map(l => div().w(9).mr(4).flex_none()
        .when(Boolean(l), el => el.border_l(1).border_color(t.input))
        .when(l === "└", el => elbow(el.self_start()))
        .when(l !== "└", el => el.self_stretch())
        .when(l === "├", el => el.child(elbow(div().w_full())))));
  }

  subRow(t, s, shown, x) {
    const k = s.t;
    const st = kidStatus(k, this.listed);
    // Something an agent started on its own: a Son of Anton.
    const pic = icon(k.program, 14, t.foreground) ?? art("world/anton.png", 18, 14);
    const on = k.address === shown;
    return this.subShell(t, `sub-${k.address}`, s.lines, x)
      .when(on, (el) => el.bg(this.room.selected))
      .on_click(() => (k.via ? run("pane.focus", { terminal: k.via }) : this.listed.has(k.address) ? run("pane.focus", { terminal: k.address }) : run("terminal.peek", { terminal: k.address })))
      .when(Boolean(k.via) && !this.covered, (el) => el.tooltip(st === "failed" ? `Failed${k.err ? `: ${k.err}` : ""}` : k.tip || k.name))
      .when(Boolean(pic), el => el.child(div().mr(8).child(pic)))
      .child(div().flex_1().truncate().text_color(on ? t.foreground : t.muted).child(k.name || k.template || k.program?.name || k.address))
      .child(this.status(t, { status: st }));
  }

  // Opens on click; folded, its ring is red if one of them failed.
  finishedRow(t, s, x) {
    const list = s.t.finished;
    return this.subShell(t, `sub-${s.t.address}`, s.lines, x)
      .on_click((_e, cx) => {
        s.open ? this.openFinished.delete(s.t.owner) : this.openFinished.add(s.t.owner);
        cx.notify();
      })
      .child(h_flex().flex_1().min_w(0).gap(4).items_center().text_color(t.dim)
        .child(div().truncate().child(`${list.length} finished`))
        .child(pix(`chevron-${s.open ? "down" : "right"}`)))
      .when(!s.open, (el) => el.child(this.status(t, { status: list.some((f) => f.status === "failed") ? "failed" : "idle" })));
  }

  status(t, a) {
    return mark(t, a.status, true);
  }

  // This render's agents, each space's ranked first, then A–Z. A kept sub-agent (one
  // with a pane) is in agents() too: it shows in its parent's tree, not on its own.
  readAgents() {
    const list = agents();
    this.roles = casting(list);
    this.listed = new Map(list.map((a) => [a.address, a.status]));
    const all = terminals();
    const now = Date.now();
    this.track(list, now);
    const nested = new Set(list.flatMap((a) => this.tree(all, a.address).map((s) => s.t.address)));
    const top = list.filter((a) => !nested.has(a.address));
    const tabCounts = new Map();
    for (const a of top) tabCounts.set(a.tab, (tabCounts.get(a.tab) ?? 0) + 1);
    // A row names the agent by a tab someone named or its own title, never an
    // automatic tab number unless two rows in a space would otherwise read the same.
    // Read the pane snapshot once: every host read copies the whole list into JS.
    const leads = leadPanes(panes());
    const tabs = new Map(spaces().flatMap(s => s.tabs).map(tab => [tab.id, tab]));
    const labels = new Map(top.map(a => {
      const tab = tabs.get(a.tab);
      const many = tabCounts.get(a.tab) > 1;
      return [a.address, tab ? title(many ? { ...tab, named: false } : tab, many ? a : leads.get(a.tab)) : (bare(a) || a.program?.name || "")];
    }));
    const auto = (a) => /^\d+$/.test(labels.get(a.address));
    const seen = {};
    for (const a of top) if (auto(a)) seen[a.space] = (seen[a.space] ?? 0) + 1;
    const name = (a) => (auto(a) && seen[a.space] < 2 ? a.program?.name || labels.get(a.address) : labels.get(a.address));
    const bySpace = new Map();
    for (const a of top) {
      if (!bySpace.has(a.space)) bySpace.set(a.space, []);
      bySpace.get(a.space).push(a);
    }
    const ranked = new Map((shared(PRIORITY)?.agents ?? []).map((e) => [e.pane, e.n]));
    const rank = (a) => ranked.get(a.pane) ?? Infinity;
    for (const l of bySpace.values()) l.sort((x, y) => rank(x) - rank(y) || name(x).localeCompare(name(y), undefined, { sensitivity: "base" }) || x.seq - y.seq);
    const f = focused();
    this.ag = { list, bySpace, all, now, name, ranked, shown: f?.agent, cur: f?.pane };
  }

  // A space's agents under its row, each followed by its sub-agents unless folded.
  // An agent with a character is a taller row: the character at their desk (in
  // the bedroom, on their bunk), posed by the agent's status, then the agent's
  // name over the character's and the mark of the tool it runs in.
  agentRows(w, tree, t) {
    const { bySpace, all, now, name, ranked, shown, cur } = this.ag;
    return (bySpace.get(w.id) ?? []).flatMap((a) => {
      const n = ranked.get(a.pane) ?? 0;
      const subs = this.tree(all, a.address);
      const open = !this.foldedAgents.has(a.address);
      const c = who(a.address, this.roles);
      const pic = c ? (this.owner ? seat(c, a.status) : bed(c, a.status)) : icon(a.program, 16, t.foreground);
      const badge = c ? toolMark(a.program, `tool-${a.address}`) : null;
      const box = c ? 124 : tree ? 13 : 18;
      const when = this.changed[a.address]?.at ?? 0;
      const on = a.pane === cur;
      const idle = a.status === "idle" && !on;
      const fold = (_e, cx) => {
        cx.stop_propagation();
        open ? this.foldedAgents.add(a.address) : this.foldedAgents.delete(a.address);
        cx.notify();
      };
      const sts = subs.filter((s) => !s.t.finished).map((s) => kidStatus(s.t, this.listed));
      const top = sts.reduce((m, s) => ((RANK[s] ?? 0) > (RANK[m] ?? 0) ? s : m), null);
      // A desk or a bunk starts a pixel into its picture: its edge under the sign's.
      const left = (tree ? 30 : 8) + this.inset - (c ? 2 : 0);
      const row = h_flex()
        .id(`ag-${a.address}`)
        .relative()
        .px(8)
        .pl(left)
        .h(c ? 82 : 28)
        .flex_none()
        .mt(ROW_GAP)
        .items_center()
        .gap(c ? 10 : 9)
        .when(on, (el) => el.bg(this.room.selected))
        .when(!on && !this.covered, (el) => el.hover((s) => s.bg(this.room.hover)))
        .on_click(() => run("pane.focus", { pane: a.pane }))
        .on_mouse_down("right", () => openOverlay({ mod: "pied-piper-menu", kind: "popup", width: 170, height: 260, props: { tab: "agent", target: { pane: a.pane, space: a.space, machine: w.machine ?? null } } }))
        .child(h_flex().id(`agent-fold-${a.address}`).w(box).flex_none().justify_center().when(Boolean(c) && !this.covered, el => el.tooltip(c.full)).when(subs.length > 0, el => el.on_click(fold)).when(Boolean(pic), el => el.child(pic)))
        .when(Boolean(n), (el) => el.child(this.rankMark(t, n)))
        .child(v_flex().flex_1().min_w(0).gap(3).line_height("14px")
          .child(div().truncate().text_color(idle ? t.muted : t.foreground).child(name(a)))
          // The gap is one letter wide, so the dot sits midway between the name and the mark.
          .when(Boolean(c), el => el.child(h_flex().gap(7).items_center().text_color(t.dim)
            .child(div().truncate().child(badge ? `${c.name} ·` : `${c.name} · ${a.program?.name ?? "agent"}`))
            .when(Boolean(badge), el => el.child(badge)))))
        .when(subs.length > 0, el => el.child(div()
          .id(`fold-${a.address}`)
          .h(18)
          .px(3)
          .gap(3)
          .flex()
          .items_center()
          .text_color(open ? t.dim : (t[top] ?? t.dim))
          .cursor_pointer()
          .hover((s) => s.bg(this.room.hover).text_color(t.foreground))
          .on_click(fold)
          .child(pix(`chevron-${open ? "down" : "right"}`))
          .when(!open, (el) => el.child(String(subs.filter((s) => !s.t.finished).length)))))
        .when(Boolean(when), el => el.child(div().flex_none().text_color(t.dim).child(duration(now - when))))
        .child(this.status(t, a));
      if (!open) return [row];
      // The tree's line runs on down from the desk's left leg (the bunk's left
      // post), an art pixel being 2 of ours; without one, a step in from where the name starts.
      const lineX = left + (c ? 2 * ((this.owner ? DESK_LEGS : BUNK_LEGS)[c.key] ?? 1) : box + 15);
      return [row, ...subs.filter((s) => !s.hidden).map((s) => (s.t.finished ? this.finishedRow(t, s, lineX) : this.subRow(t, s, shown, lineX)))];
    });
  }

  checkNew(cx) {
    const now = Date.now();
    const sp = spaces();
    for (const s of sp) if (!this.shown.has(s.id)) this.born[s.id] ??= now;
    const due = this.due(now, sp, panes());
    if (due.size) this.refreshGit(due, cx);
    if (sp.some((s) => !this.shown.has(s.id)) || this.orderingDue(now) || this.tabOrder?.due(now)) cx.notify();
  }

  // Places whose git could have changed: new ones (a new space, a cd), where a
  // command or an agent's turn just ended (a checkout, a commit, edits), those on
  // a machine that is back, and repos in view whose fallback is due.
  due(now, sp, ps) {
    // Moved there: what it knew of that place may be old.
    const at = {};
    for (const s of sp) at[s.id] = where(s, ps);
    const keys = new Set(Object.values(at).filter((k) => JSON.parse(k)[1]));
    const due = new Set([...keys].filter((k) => !(k in this.git)));
    for (const [id, k] of Object.entries(at)) if (this.at[id] && this.at[id] !== k && keys.has(k)) due.add(k);
    this.at = at;
    const spaceOf = {};
    for (const s of sp) for (const t of s.tabs ?? []) spaceOf[t.id] = s;
    const busy = {};
    for (const p of ps) {
      if (!p.terminal || !spaceOf[p.tab]) continue;
      busy[p.pane] = p.status === "working" || !(p.program?.shell || p.program?.agent);
      if (this.busy[p.pane] && !busy[p.pane]) this.sameRepo(at[spaceOf[p.tab].id], keys).forEach((k) => due.add(k));
    }
    this.busy = busy;
    for (const m of machines()) {
      const ready = m.layout === "ready";
      if (ready && this.ready[m.name] === false) for (const k of keys) if (JSON.parse(k)[0] === m.name) due.add(k);
      this.ready[m.name] = ready;
    }
    if (window().active) {
      const mine = new Set(Object.entries(at).filter(([id]) => !this.inView || this.inView.has(id)).map(([, k]) => k));
      for (const k of keys) {
        if (!mine.has(k)) continue;
        const asks = this.git[k] || this.unsure.has(k);
        if (asks && !this.folded.has(JSON.parse(k)[0]) && now - (this.checked[k] ?? 0) > FALLBACK) due.add(k);
      }
    }
    return due;
  }

  // `key` and the other places in its repo (a commit there moves their ahead/behind).
  sameRepo(key, keys) {
    const repo = this.git[key]?.repo;
    return [key, ...(repo ? [...keys].filter((k) => this.git[k]?.repo === repo) : [])];
  }

  refreshMachines(cx) {
    cx.spawn(async cx => {
      try { const r = await hc(["machine", "ls", "--json"]); if (r.code === 0) this.machines = (JSON.parse(r.stdout).machines ?? []).filter((m) => !m.temporary); } catch {}
      cx.notify();
    });
  }

  rebuilt(machine) {
    return machine?.state === "unreachable" && /^a different core answers there \("[^"]+"\)$/.test(machine.why ?? "");
  }

  reconnect(machine, cx) {
    const name = machine.name;
    if (this.reconnecting[name]?.busy) return;
    const state = this.reconnecting[name] ??= { machine, removed: false };
    state.busy = true;
    state.error = null;
    localStorage.setItem("machines.reconnecting", JSON.stringify(this.reconnecting));
    cx.notify();
    cx.spawn(async cx => {
      try {
        const ask = async args => {
          const r = await hc([...args, "--json"]);
          if (r.code !== 0) {
            let error;
            try { error = JSON.parse(r.stdout || r.stderr).error?.message; } catch {}
            throw new Error(error || r.stderr || r.stdout || "Couldn't connect.");
          }
        };
        if (!state.removed) {
          await ask(["machine", "rm", name]);
          state.removed = true;
          localStorage.setItem("machines.reconnecting", JSON.stringify(this.reconnecting));
        }
        const args = ["machine", "add"];
        if (machine.via) args.push("--via", machine.target);
        else args.push(machine.target);
        args.push("--name", name);
        if (machine.session) args.push("--session", machine.session);
        if (machine.temporary) args.push("--temp");
        await ask(args);
        this.folded.delete(name);
        localStorage.setItem("machines.folded", JSON.stringify([...this.folded]));
        delete this.reconnecting[name];
      } catch (e) {
        state.error = String(e.message ?? e);
        state.busy = false;
      }
      localStorage.setItem("machines.reconnecting", JSON.stringify(this.reconnecting));
      this.refreshMachines(cx);
      cx.notify();
    });
  }

  // One look at a time, each place once however often it was asked for meanwhile.
  refreshGit(keys, cx) {
    for (const k of keys) this.pending.add(k);
    if (this.refreshing) return;
    this.refreshing = true;
    cx.spawn(async (cx) => {
      while (this.pending.size) {
        const keys = [...this.pending];
        this.pending.clear();
        await Promise.all(keys.map((key) => this.check(key, cx)));
      }
      const used = new Set(Object.values(this.git).filter(Boolean).map((g) => JSON.parse(g.repo)).filter(([on]) => !on).map(([, repo]) => repo));
      for (const repo of this.watching) if (!used.has(repo)) this.watching.delete(repo);
      this.refreshing = false;
      cx.notify();
    });
  }

  // One place's git: branch, ahead/behind, its repo.
  async check(key, cx) {
    const [on, cwd] = JSON.parse(key);
    this.checked[key] = Date.now();
    this.unsure.delete(key);
    try {
      // Ref-only reads avoid scanning the worktree or waking its index watch.
      // Two reads: a folder name may itself contain a newline.
      const [r, common] = await Promise.all([
        exec("git", ["rev-parse", "--path-format=absolute", "--show-toplevel"], { cwd, on }),
        exec("git", ["rev-parse", "--path-format=absolute", "--git-common-dir"], { cwd, on }),
      ]);
      if (r.code !== 0 || common.code !== 0) {
        // Only git's own "no" is remembered as no repo; anything else is asked again.
        if (!/not a git repository/i.test(r.code !== 0 ? r.stderr : common.stderr)) this.unsure.add(key);
        this.git[key] = null;
        return;
      }
      // The repo's own .git folder names it; a worktree's top differs from it.
      const top = r.stdout.replace(/\n$/, ""), repo = common.stdout.replace(/\n$/, "");
      const [branch, counts] = await Promise.all([
        exec("git", ["symbolic-ref", "-q", "HEAD"], { cwd, on }),
        exec("git", ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"], { cwd, on }),
      ]);
      const name = repo.endsWith("/.git") ? base(repo.slice(0, -5)) : base(repo).replace(/\.git$/, "");
      const [ahead, behind] = counts.code === 0 ? counts.stdout.trim().split(/\s+/).map(Number) : [0, 0];
      const info = { name, branch: branch.code === 0 ? branch.stdout.trim().replace(/^refs\/heads\//, "") : "(detached)", ahead, behind, repo: JSON.stringify([on, repo]), linked: repo !== `${top}/.git` };
      this.git[key] = info;
      if (!on) this.watch(repo, cx);
    } catch {
      // Couldn't ask (the machine is away): keep what it showed, look again later.
      this.git[key] ??= null;
      this.unsure.add(key);
    }
  }

  watch(repo, cx) {
    if (this.watching.has(repo)) return;
    this.watching.add(repo);
    cx.spawn(async (cx) => {
      try {
        while (this.watching.has(repo)) {
          await watchFolder(repo);
          const mine = JSON.stringify([null, repo]);
          if (this.watching.has(repo)) this.refreshGit(Object.keys(this.git).filter((k) => this.git[k]?.repo === mine), cx);
        }
      } catch { this.watching.delete(repo); }
    });
  }

  menu(w) {
    // A popup is as tall as its items; height is only the most.
    openOverlay({ mod: "pied-piper-menu", kind: "popup", width: 200, height: 360, props: { tab: "space", target: { id: w.id } } });
  }

  orderingDue(now) {
    return this.ordering && now - this.ordering.at >= 1000
      && this.ordering.machines.every(name => machines().some(m => m.name === name && m.layout === "ready"));
  }

  // Spaces in order: those holding a priority first (any machine), by the best of
  // theirs and their agents', then each machine's A–Z. A worktree space goes under
  // its main checkout's unless it holds one itself.
  ordered() {
    const sp = spaces(), ps = panes();
    const ready = (w) => this.shown.has(w.id) || where(w, ps) in this.git || Date.now() - (this.born[w.id] ??= Date.now()) > 1500;
    for (const w of sp) if (!this.shown.has(w.id) && ready(w)) this.shown.add(w.id);
    const own = new Map((shared(PRIORITY)?.spaces ?? []).map((e) => [e.id, e.n]));
    const rank = new Map(sp.flatMap((w) => {
      const ns = [own.get(w.id), ...(this.ag.bySpace.get(w.id) ?? []).map((a) => this.ag.ranked.get(a.pane))].filter(Boolean);
      return ns.length ? [[w.id, Math.min(...ns)]] : [];
    }));
    const list = sp.map((w, i) => ({ w, i, g: this.git[where(w, ps)] ?? null }));
    const mains = new Set(list.filter((r) => r.g && !r.g.linked).map((r) => r.g.repo));
    const nested = (r) => r.g?.linked && mains.has(r.g.repo) && !rank.has(r.w.id);
    const az = (x, y) => x.w.name.localeCompare(y.w.name, undefined, { sensitivity: "base" }) || x.i - y.i;
    const heads = list.filter((r) => !nested(r));
    const ranked = heads.filter((r) => rank.has(r.w.id)).sort((x, y) => rank.get(x.w.id) - rank.get(y.w.id));
    const remote = [...new Set(heads.map((r) => r.w.machine).filter(Boolean))].sort();
    const rest = [null, ...remote].flatMap((m) => heads.filter((r) => !rank.has(r.w.id) && (r.w.machine ?? null) === m).sort(az));
    const out = [];
    const placed = new Set(); // repos whose worktrees are listed (under the first of its spaces)
    for (const r of [...ranked, ...rest]) {
      const pri = rank.has(r.w.id);
      out.push({ ...r, tree: null, pri, n: own.get(r.w.id) ?? 0 });
      if (!r.g || r.g.linked || placed.has(r.g.repo)) continue;
      placed.add(r.g.repo);
      const kids = list.filter((k) => nested(k) && k.g.repo === r.g.repo).sort(az);
      kids.forEach((k, n) => out.push({ ...k, tree: n === kids.length - 1 ? "└─" : "├─", pri, n: 0 }));
    }
    // Simulate the batch so later indexes include earlier moves. An attempted
    // write can lose a sync conflict: allow the echo to settle before retrying.
    const order = sp.map(w => w.id);
    const target = out.map(r => r.w.id);
    const key = JSON.stringify([order, target, machines()]);
    if (order.every((id, i) => id === target[i])) {
      this.ordering = null;
    } else if (this.owner && (this.ordering?.key !== key || this.orderingDue(Date.now()))) {
      const moved = new Set();
      this.ordering = { key, at: Date.now(), machines: [] };
      for (let i = 0; i < out.length; i++) {
        const from = order.indexOf(out[i].w.id);
        if (from === i) continue;
        run("space.move", { id: out[i].w.id, index: i + 1 });
        moved.add(out[i].w.machine ?? null);
        order.splice(i, 0, order.splice(from, 1)[0]);
      }
      this.ordering.machines = [...moved];
    }
    this.tabOrder?.step({ spaces: sp, panes: ps, entries: shared(PRIORITY)?.agents, machines: machines(), now: Date.now(), run });
    return out.filter(r => this.shown.has(r.w.id));
  }

  // This block's rows; the inactive ones under a header per machine once one isn't this computer.
  grouped(t, collapsed) {
    const rows = this.ordered();
    if (this.owner) setAgentOrder(rows.flatMap((r) => this.ag.bySpace.get(r.w.id) ?? []).map((a) => a.address));
    const draw = (r, k) => (collapsed ? [this.compact(r, t)] : [this.row(r, t, k === 0 ? 0 : r.tree ? ROW_GAP : GROUP_GAP), ...this.agentRows(r.w, r.tree, t)]);
    const top = rows.filter((r) => r.pri);
    const rest = rows.filter((r) => !r.pri);
    this.inView = new Set((this.owner ? top : rest).map((r) => r.w.id));
    this.mine = new Set(this.ag.list.filter((a) => this.inView.has(a.space)).map((a) => a.address));
    if (this.owner) return top.length ? top.flatMap(draw) : collapsed ? [] : [div().pl(8 + OFFICE_INSET).pr(8).py(6).text_color(t.dim).child("Right-click a space or agent to prioritize it.")];
    const remote = [...new Set([...rows.map(r => r.w.machine).filter(Boolean), ...this.machines.map(m => m.name), ...Object.keys(this.reconnecting)])].sort();
    const loading = m => {
      const layout = machines().find(k => k.name === m)?.layout;
      return layout === "loading" || (!layout && this.machines.some(k => k.name === m && k.state === "connected"))
        || spaces().some(s => (s.machine ?? null) === m && !this.shown.has(s.id));
    };
    const loadingRow = m => h_flex().id(`machine-loading-${m ?? "local"}`).h(28).flex_none().px(collapsed ? 0 : 8).when(!collapsed, el => el.pl(8)).items_center().when(collapsed, el => el.justify_center()).text_color(t.dim).child(collapsed ? "…" : "Loading…");
    if (!remote.length) return loading(null) && !rows.length ? [loadingRow(null)] : rest.flatMap(draw);
    const machineNames = [null, ...remote];
    return machineNames.flatMap((m, n) => {
      const all = rows.filter((r) => (r.w.machine ?? null) === m);
      const mine = all.filter((r) => !r.pri);
      const repair = this.reconnecting[m];
      const machine = this.machines.find(k => k.name === m) ?? repair?.machine;
      const connected = !m || machine?.state === "connected";
      const rebuilt = this.rebuilt(machine) || !!repair;
      const login = machine?.state === "needs_login" ? `hc machine login ${m}` : null;
      const folded = this.folded.has(m);
      const icon = pix(m ? "server" : "monitor", HEAD_ICON);
      const badge = div().absolute().right(-3).bottom(-2).size(6).border_1().border_color(this.room.wall).bg(connected ? t.ansi2 : t.dim);
      const head = h_flex().id(`machine-${m ?? "local"}`).h(26).flex_none().px(collapsed ? 0 : 8).gap(HEAD_GAP).items_center().text_color(t.dim)
        .when(!collapsed && n > 0, el => el.mt(GROUP_GAP))
        .when(collapsed, el => el.mt(4).w(RAIL_CELL).justify_center().tooltip(login ? `${m} needs a login: run ${login}. Click for Copy.` : m ? `${m} · ${connected ? "connected" : (machine?.state ?? "asleep").replace(/_/g, " ")}` : "This computer"))
        .when(!this.covered, el => el.cursor_pointer().hover(s => s.bg(this.room.hover)))
        .on_click((_e, cx) => {
          if (collapsed && login) { run("app.settings", { section: "machines" }); return; }
          folded ? this.folded.delete(m) : this.folded.add(m);
          localStorage.setItem("machines.folded", JSON.stringify([...this.folded]));
          cx.notify();
        })
        .when(!collapsed, el => el.child(icon))
        .when(collapsed, el => el.child(div().relative().flex_none().child(icon).when(Boolean(m), el => el.child(badge))))
        .when(!collapsed, el => el.child(div().flex_1().truncate().child(m ?? "This computer"))
          .when(!connected && !rebuilt && !login, el => el.child(div().flex_none().child((machine?.state ?? "asleep").replace(/_/g, " "))))
          .when(rebuilt, el => el.child(h_flex().flex_none().gap(3).items_center()
            .child(div().max_w(140).truncate().child(repair?.error || "rebuilt ·"))
            .child(div().id(`machine-connect-${m}`).text_color(repair?.error ? t.blocked : t.muted)
              .hover(s => s.text_color(t.foreground))
              .tooltip(repair?.error || "This machine was rebuilt or replaced. Click to connect to the new one.")
              .on_click((_e, cx) => { cx.stop_propagation(); this.reconnect(machine, cx); })
              .child(repair?.busy ? "Connecting…" : "Connect"))))
          .when(connected, el => el.child(div().id(`machine-add-${m ?? "local"}`).flex_none().px(4).hover(s => s.bg(this.room.hover).text_color(t.foreground))
            .on_click((_e, cx) => { cx.stop_propagation(); run("space.new", { machine: m ?? "" }); }).child("+")))
          .child(div().size(6).flex_none().bg(connected ? t.ansi2 : t.dim))
          .child(pix(`chevron-${folded ? "right" : "down"}`)));
      const empty = h_flex().id(`machine-new-${m ?? "local"}`).h(28).flex_none().px(collapsed ? 0 : 8).when(!collapsed, el => el.pl(8)).gap(7).items_center()
        .text_color(t.dim).when(!this.covered, el => el.hover(s => s.bg(this.room.hover).text_color(t.foreground)))
        .on_click(() => run("space.new", { machine: m ?? "" }))
        .when(collapsed, el => el.w(RAIL_CELL).justify_center().tooltip(`New space on ${m ?? "this computer"}`)
          .child(h_flex().size(18).border_1().border_color(t.dim).items_center().justify_center()
            .child(pix("plus"))))
        .when(!collapsed, el => el.child(pix("plus")).child("New space there"));
      if (!collapsed && rebuilt) return [head];
      const cell = collapsed ? railCell : (el) => el;
      const guidance = !collapsed && login ? [v_flex().px(8).pb(6).gap(3).flex_none()
        .child(div().text_color(t.blocked).child("needs a login: run"))
        .child(h_flex().gap(5).items_center()
          .child(div().flex_1().min_w(0).truncate().when(!this.covered, el => el.tooltip(login)).text_color(t.muted).child(login))
          .child(div().id(`machine-login-copy-${m}`).flex_none().px(5).py(2)
            .text_color(t.foreground).bg(this.room.selected).cursor_pointer().hover(s => s.bg(this.room.hover))
            .on_click((_e, cx) => { cx.stop_propagation(); cx.write_to_clipboard(login); this.copiedLogin = login; cx.notify(); })
            .child(this.copiedLogin === login ? "Copied" : "Copy")))] : [];
      return [cell(head), ...guidance, ...(folded ? [] : mine.length ? mine.flatMap(draw) : all.length ? [] : [loading(m) ? loadingRow(m) : cell(empty)])];
    });
  }

  rankMark(t, n) {
    return h_flex().absolute().left(RANK_LEFT).top(0).bottom(0).items_center().text_color(t.muted).child(String(n));
  }

  // Only what's unusual, after the name: "spike \u21912 \u21931". Never the repo's name:
  // a space named something else was renamed, and the name it was given is the one
  // to read. The branch goes when the name already says it (a worktree is named
  // after its branch), and master/main go: nearly every space is on one.
  gitTail(g, name, t) {
    const raw = g.branch ?? "detached";
    const branch = raw.toLowerCase() === name.toLowerCase() || raw === "master" || raw === "main" ? "" : raw;
    // Right after the name, on the bare wall: what hangs at the wall's top is to the right.
    return h_flex()
      .flex_1()
      .min_w(0)
      .gap(5)
      .items_center()
      .text_color(t.dim)
      .when(Boolean(branch), (el) => el.child(div().min_w(0).truncate().child(branch)))
      .when(g.ahead > 0, (el) => el.child(div().flex_none().text_color(t.ansi2).child(`\u2191${g.ahead}`)))
      .when(g.behind > 0, (el) => el.child(div().flex_none().text_color(t.ansi1).child(`\u2193${g.behind}`)));
  }

  // `gap`: the space above it.
  row({ w, g, tree, n }, t, gap) {
    // Said once: the focused agent's row is highlighted instead of its space's.
    const on = w.active && !(this.ag.bySpace.get(w.id) ?? []).some((a) => a.pane === this.ag.cur);
    const color = this.colors[w.id] ?? "ansi6";
    const fill = color.startsWith("#") ? color : (MARK[color] ?? t[color]);
    // 22px is the font's pixels at the art's size.
    const sign = isPiedPiper(w) ? piedPiper()
      : h_flex().size(24).flex_none().bg(fill).items_center().justify_center().text_size(22).line_height("24px").text_color("#ffffff").child(initial(w, g));
    return v_flex()
      .relative()
      .id(`space-${w.id}`)
      .px(8)
      .pl(8 + this.inset)
      .h(rowHeight({ tree }))
      .flex_none()
      .justify_center()
      .mt(gap)
      .when(on, (el) => el.bg(this.room.selected))
      .when(!on && !this.covered, (el) => el.hover((s) => s.bg(this.room.hover)))
      .on_click(() => run("space.select", { id: w.id }))
      .on_mouse_down("right", () => this.menu(w))
      .when(Boolean(n), (el) => el.child(this.rankMark(t, n)))
      .child(
        h_flex()
          .gap(9)
          .items_center()
          .when(Boolean(tree), el => el.pl(22).child(pix("branch").text_color(t.dim)))
          .when(!tree, el => el.child(sign))
          .child(div().flex_shrink(0).max_w(150).truncate().text_color(t.foreground).child(w.name))
          .child(g ? this.gitTail(g, w.name, t) : div().flex_1()),
      );
  }

  compact({ w, i }, t) {
    return railCell(h_flex()
      .id(`space-${w.id}`)
      .relative()
      .w(RAIL_CELL)
      .h(26)
      .justify_center()
      .items_center()
      .when(w.active, (el) => el.bg(this.room.selected))
      .when(!w.active, (el) => el.hover((s) => s.bg(this.room.hover)))
      .on_click(() => run("space.select", { id: w.id }))
      .child(div().text_color(w.active ? t.foreground : t.muted).child(String(i + 1)))
      .child(div().absolute().right(5).text_color(tone(t, w.status)).child(glyph(w.status))));
  }

  // A press on the bedroom, or anywhere else (`on_mouse_down_out`, which comes
  // before Herdr's boundary hears it). A double-click or double tap on the
  // boundary's grip above the bedroom fits the bedroom to its rows, once. A
  // single press is left to Herdr, whose drag it starts.
  gripPress(e, cx) {
    if (e.button !== "left") return;
    const p = e.local_position;
    if (!p || !e.bounds || p.y < -GRIP || p.y >= GRIP || p.x < 0 || p.x >= e.bounds.width) {
      this.lastPress = null;
      return;
    }
    const now = Date.now(), last = this.lastPress, room = this.measured.room;
    // macOS counts the presses (click_count), and so does this: a second press soon
    // after the first, where it was, with the boundary not dragged in between.
    const soon = last && now - last.at <= this.doubleMs && Math.hypot(e.position.x - last.x, e.position.y - last.y) <= DOUBLE_SLOP;
    let what;
    if (soon && last.fitted) what = "again"; // a third press of the same gesture
    else if (e.click_count >= 2 || (soon && Math.abs(room - last.room) < DOUBLE_SLOP)) what = this.fitToRows();
    else what = "single";
    this.lastPress = { at: now, x: e.position.x, y: e.position.y, room, fitted: what !== "single" };
    // Herdr's boundary would take a double's presses for a drag, and the pointer's
    // next move would put the boundary back under it.
    if (what !== "single") cx.stop_propagation();
  }

  // Once, as if the boundary were dragged there: the bedroom as tall as its rows,
  // but the office, the priority list, never shorter than its own rows (or its
  // min); a bedroom that still doesn't fit scrolls. Afterwards it stays put like any drag.
  fitToRows() {
    const here = listBlock(layout(), this.list);
    const kids = (here?.parent?.children ?? []).filter((n) => !n.hidden);
    const above = kids[kids.indexOf(here?.node) - 1];
    const me = this.measured;
    const office = LIST_SIZE[above?.content?.props?.list];
    const known = (m) => m?.room > 0 && m.list > 0 && m.rows != null;
    if (!above) return "no room above";
    if (!known(me) || !known(office)) return "not measured";
    // Both share the column by weight, as in the layout file; anything else is left alone.
    const weight = (n) => (n.size?.px != null ? NaN : n.size?.weight ?? 1);
    const sum = weight(above) + weight(here.node);
    if (Number.isNaN(sum)) return "sized in px";
    const total = me.room + office.room;
    const left = total - Math.max(above.min ?? 0, fitted(office));
    const want = Math.max(Math.min(fitted(me), left), here.node.min ?? 0);
    if (!(want < total) || Math.abs(want - me.room) < 1) return "fits already";
    // The two weights a drag to there would leave (a drag keeps their sum), so the
    // rooms share the column as before when the window's height changes.
    run("layout.resize", { id: above.id, weight: (sum * (total - want)) / total });
    run("layout.resize", { id: here.node.id, weight: (sum * want) / total });
    return `fit ${Math.round(me.room)} -> ${Math.round(want)}`;
  }

  render() {
    // The theme, with its two quieter text colors swapped for ones that read on this room's wall.
    const t = Object.assign(Object.create(theme()), { muted: this.room.muted, dim: this.room.dim, input: this.room.dim });
    const collapsed = narrow();
    // Folded, there's no plate for the pointer to be on.
    if (collapsed) this.onPlate.clear();
    this.covered = this.onPlate.size > 0;
    this.readAgents();
    // Every space but Pied Piper's has a color: the least used one.
    const sp = spaces();
    const ids = new Set(sp.map((p) => p.id));
    const old = shared("space.colors") ?? {};
    const kept = Object.fromEntries(Object.entries(old).filter(([id]) => ids.has(id)));
    // An empty list right after a start is not every space having closed.
    let changed = sp.length > 0 && Object.keys(kept).length !== Object.keys(old).length;
    for (const p of sp) {
      if (kept[p.id] || isPiedPiper(p)) continue;
      const uses = (c) => Object.values(kept).filter((v) => v === c).length;
      kept[p.id] = PALETTE.reduce((best, c) => (uses(c) < uses(best) ? c : best));
      changed = true;
    }
    if (changed) setShared("space.colors", kept);
    this.colors = sp.length ? kept : old;
    const name = this.roomName;
    const add = div().id("space-new").size(18).flex_none().flex().items_center().justify_center().bg(this.room.plate).text_color(t.muted)
      .hover(s => s.text_color(t.foreground)).on_click(() => run("space.new")).child(pix("plus"));
    // The plate and the "+" are in front of the rows scrolled under them: a press
    // on one stops there, after the "+" has had its click, and while the pointer
    // is on one no row lights up (`covered`). Nothing else in the band holds the
    // pointer, so rows behind its bare wall work as anywhere else.
    const inFront = (key, el) => el.id(`plate-${key}`)
      .on_hover((on, cx) => { on ? this.onPlate.add(key) : this.onPlate.delete(key); cx.notify(); })
      .on_mouse_down("left", (_e, cx) => cx.stop_propagation())
      .on_mouse_down("right", (_e, cx) => cx.stop_propagation());
    // The room's name, on a plate on its wall. Unfolded, the plate stays put at
    // the room's top, over the list, which runs up behind it.
    const head = collapsed
      ? h_flex().h(31).flex_none().items_center().justify_center().text_color(t.dim)
        .when(this.owner, el => el.child(div().id("priority").tooltip("Office").child(pix("flag", HEAD_ICON))))
        .when(!this.owner, el => el.child(add))
      : h_flex().absolute().top(0).left(0).right(0).h(PLATE_BAND).px(8).gap(6).items_center()
        .child(inFront("name", h_flex().px(6).h(18).items_center().bg(this.room.plate).text_color(t.muted).child(name.toUpperCase())))
        .when(!this.owner, el => el.child(inFront("add", div().flex_none().child(add))));
    // The list starts at the bottom edge of the wall's trim. In the bedroom that is
    // well under the boundary's grip (its 1px border and GRIP - 1 more): rows never
    // reach the grip, so a press or a double-click there is only ever the
    // boundary's (gripPress).
    const clear = collapsed ? 0 : Math.max(TRIM[name], this.owner ? 0 : GRIP - 1);
    // Unscrolled, the first row starts under the plate's band, as it always has.
    const top = collapsed ? 0 : PLATE_BAND - clear;
    this.measured.top = top;
    return v_flex().id("room").relative().size_full().min_h(0).overflow_hidden().bg(this.room.wall).font_family(FONT).text_size(TEXT)
      .on_size_change((size) => { this.measured.room = size.height; })
      .when(!this.owner, el => el.border_t(1).border_color(t.border)
        .on_mouse_down("left", (e, cx) => this.gripPress(e, cx))
        .on_mouse_down_out((e, cx) => this.gripPress(e, cx)))
      // The wall is taller than a list gets, and stays put while the rows scroll
      // over it and everything hung on it, under its trim; its baseboard and the
      // floor lie along the list's bottom.
      .when(!collapsed, el => el.child(art(`world/wall-${name}.png`, 480, 960).absolute().left(0).top(0))
        .child(art(`world/floor-${name}.png`, 480, 16).absolute().left(0).bottom(0)))
      .when(collapsed, el => el.child(head))
      .when(clear > 0, el => el.child(div().h(clear).flex_none()))
      .child(v_flex().id("list").flex_1().min_h(0).px(collapsed ? 0 : 8).pt(top).pb(FLOOR_ROOM).overflow_y_scrollbar().mode("always")
        .on_size_change((size) => { this.measured.list = size.height; })
        .child(v_flex().id("rows").flex_none().on_size_change((size) => { this.measured.rows = size.height; })
          .children(this.grouped(t, collapsed))))
      // Drawn after the list, so in front of its rows.
      .when(!collapsed, el => el.child(head))
      .when(collapsed && !this.owner, (el) => el.child(h_flex().h(28).flex_none().items_center().justify_center()
        .child(div().id("collapse").text_color(t.dim).hover((s) => s.text_color(t.foreground)).on_click(toggleSidebar).child("»"))));
  }
}
