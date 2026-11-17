// Pied Piper: Herdr as Silicon Valley, after the show's opening titles but at
// night, in pixel art. Across the top, the title and then the valley's
// companies, one after another, with the tabs as billboards over them; the
// one that is shown is lit. The sidebar is the hostel: an office and a
// bedroom, each with its own wall, where every agent is played by a character
// from the show (cast.js), at their own desk or on their own bunk, facing you.
// One mod in roles; the layout gives each copy props { role }:
//   brand   the sidebar's top: the title, search, fold
//   footer  the sidebar's bottom: settings, add machine
//   spaces  a sidebar list of spaces and their agents (props.list:
//           "priority" is the office, "inactive" the bedroom)
//   tabs    the tab bar
//   pane    a pane's header
//   status  the status bar
//   toast   notifications (the app opens it without a role)
// art/generate.py draws every picture.

import { View, div } from "gpui-kit";
import { props } from "herdr";
import Chrome from "./chrome.js";
import Spaces from "./spaces.js";
import Tabs from "./tabs.js";
import Pane from "./pane.js";
import Status from "./status.js";
import Toast from "./toast.js";

const ROLES = { brand: Chrome, footer: Chrome, spaces: Spaces, tabs: Tabs, pane: Pane, status: Status, toast: Toast };

export default class PiedPiper extends View {
  init(p, cx) {
    const pr = props() ?? p ?? {};
    // The layout's toast mod gets the notification itself as props.
    const R = ROLES[pr.role ?? ("overlay" in pr || "title" in pr ? "toast" : "")];
    this.role = R ? new R() : null;
    this.role?.init?.(pr, cx);
  }

  render(cx) {
    if (!this.role) return div().child(`pied-piper: no role "${props()?.role}"`);
    return this.role.render(cx);
  }
}
