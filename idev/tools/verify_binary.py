#!/usr/bin/env python3
"""Check that a built librustdesk.dll embeds the Soporte iDev configuration.

Usage: python idev/tools/verify_binary.py path/to/librustdesk.dll
Exits non-zero if the private server or key are missing, or if the default
public rendezvous server is still embedded as a fallback.
"""

import sys

MUST_CONTAIN = [
    b"rustdesk.idevpy.com",
    b"O6qGUkD2hlCk26erLMuMmBk3+PReg03kaXMebv+46G0=",
    # APP_NAME "Soporte-iDev" (12 bytes) is copied with to_owned(), which the
    # optimizer emits as 8 + 4 byte immediates, so only "Soporte-" is contiguous.
    b"Soporte-",
    b"Soporte iDev",
]
MUST_NOT_CONTAIN = [
    b"rs-ny.rustdesk.com",
    b"OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=",
]


def main(path):
    with open(path, "rb") as f:
        data = f.read()
    ok = True
    for s in MUST_CONTAIN:
        found = s in data
        ok &= found
        print(("OK      " if found else "MISSING ") + s.decode())
    for s in MUST_NOT_CONTAIN:
        found = s in data
        ok &= not found
        print(("FOUND!  " if found else "absent  ") + s.decode())
    print("RESULT: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
