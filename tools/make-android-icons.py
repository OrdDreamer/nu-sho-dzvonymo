"""Draws the Android launcher icons with the same renderer as make-icons.py."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("make_icons", Path(__file__).with_name("make-icons.py"))
mi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mi)

RES = Path(__file__).resolve().parent.parent / "android/app/src/main/res"
DENSITY = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}

for name, k in DENSITY.items():
    d = RES / f"mipmap-{name}"
    legacy = round(48 * k)
    for f in ("ic_launcher.png", "ic_launcher_round.png"):
        mi.write_png(d / f, mi.render(legacy, 0.62))
    # adaptive layer is 108dp; only the middle ~66dp stays visible after masking
    mi.write_png(d / "ic_launcher_foreground.png", mi.render(round(108 * k), 0.38))
