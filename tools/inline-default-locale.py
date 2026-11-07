"""Bakes locales/uk.json into index.html as the offline fallback copy.

The page normally fetches its texts, which browsers refuse to do over file://, so a
copy of the default locale rides along inside the page. locales/uk.json stays the
single place to edit; run this after touching it.

    python tools/inline-default-locale.py        # rewrite the block
    python tools/inline-default-locale.py --check  # exit 1 if it is out of date
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
LOCALE = ROOT / "locales" / "uk.json"
START = "<!-- locale-uk:start"
END = "<!-- locale-uk:end -->"


def block(data):
    # </script> inside the payload would close the tag early; the escape is still valid JSON
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (
        START + " - generated from locales/uk.json by tools/inline-default-locale.py -->\n"
        '<script type="application/json" id="locale-uk">' + payload + "</script>\n"
        + END
    )


def main():
    page = PAGE.read_text(encoding="utf-8")
    head, _, rest = page.partition(START)
    _, _, tail = rest.partition(END)
    if not rest or not tail:
        sys.exit("markers %s ... %s not found in index.html" % (START, END))

    updated = head + block(json.loads(LOCALE.read_text(encoding="utf-8"))) + tail
    if "--check" in sys.argv:
        if updated != page:
            sys.exit("index.html is out of date - run python tools/inline-default-locale.py")
        print("inlined locale is up to date")
        return
    if updated == page:
        print("inlined locale already up to date")
        return
    PAGE.write_text(updated, encoding="utf-8", newline="\n")
    print("inlined locales/uk.json into index.html (%d bytes)" % len(updated))


if __name__ == "__main__":
    main()
