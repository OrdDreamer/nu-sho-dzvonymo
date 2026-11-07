"""Bakes locales/*.json into index.html.

Browsers refuse fetch() over file://, so a page that loaded its texts over the
network showed nothing but the error screen when index.html was opened straight from
disk. The texts now ride along inside the page instead. locales/*.json stay the single
place to edit; run this after touching them.

    python tools/inline-locales.py           # rewrite the block
    python tools/inline-locales.py --check   # exit 1 if it is out of date
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
LOCALES = ROOT / "locales"
LANGS = ("uk", "ru", "en")
START = "<!-- locales:start"
END = "<!-- locales:end -->"


def block():
    lines = [START + " - generated from locales/*.json by tools/inline-locales.py -->"]
    for lang in LANGS:
        data = json.loads((LOCALES / (lang + ".json")).read_text(encoding="utf-8"))
        # </script> inside the payload would close the tag early; the escape is still valid JSON
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        lines.append(
            '<script type="application/json" id="locale-%s">%s</script>' % (lang, payload)
        )
    lines.append(END)
    return "\n".join(lines)


def main():
    page = PAGE.read_text(encoding="utf-8")
    head, _, rest = page.partition(START)
    _, _, tail = rest.partition(END)
    if not rest or not tail:
        sys.exit("markers %s ... %s not found in index.html" % (START, END))

    updated = head + block() + tail
    if "--check" in sys.argv:
        if updated != page:
            sys.exit("index.html is out of date - run python tools/inline-locales.py")
        print("inlined locales are up to date")
        return
    if updated == page:
        print("inlined locales already up to date")
        return
    PAGE.write_text(updated, encoding="utf-8", newline="\n")
    print("inlined %s into index.html (%d bytes)" % (", ".join(LANGS), len(updated)))


if __name__ == "__main__":
    main()
