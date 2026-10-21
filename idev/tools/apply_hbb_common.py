#!/usr/bin/env python3
"""Apply the Soporte iDev changes to the hbb_common submodule.

Equivalent to idev/patches/hbb_common.patch, but independent of line endings
(Windows checkouts may use CRLF) and idempotent. Fails if upstream changed the
expected lines, so a RustDesk update can never silently skip the change.

Run from the repository root:  python idev/tools/apply_hbb_common.py
"""

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_RS = os.path.join(ROOT, "libs", "hbb_common", "src", "config.rs")

REPLACEMENTS = [
    (
        'pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());',
        'pub static ref APP_NAME: RwLock<String> = RwLock::new("Soporte-iDev".to_owned());',
    ),
    (
        'pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];',
        'pub const RENDEZVOUS_SERVERS: &[&str] = &["rustdesk.idevpy.com"];',
    ),
    (
        'pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";',
        'pub const RS_PUB_KEY: &str = "O6qGUkD2hlCk26erLMuMmBk3+PReg03kaXMebv+46G0=";',
    ),
]


def main():
    with open(CONFIG_RS, encoding="utf-8", newline="") as f:
        src = f.read()
    for old, new in REPLACEMENTS:
        if src.count(new) == 1:
            print("already applied:", new)
            continue
        if src.count(old) != 1:
            print("ERROR: expected line not found exactly once:", old, file=sys.stderr)
            return 1
        src = src.replace(old, new)
        print("applied:", new)
    with open(CONFIG_RS, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    return 0


if __name__ == "__main__":
    sys.exit(main())
