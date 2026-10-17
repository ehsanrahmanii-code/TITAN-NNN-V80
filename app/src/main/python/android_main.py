"""Start TITAN PRO V80 Flask server inside Chaquopy (Android)."""
from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path

_started = False
_lock = threading.Lock()


def _prepare_home() -> None:
    """Prefer shared storage NNN; fall back to app-private NNN."""
    candidates = []
    # Shared internal storage (user-visible folder NNN)
    candidates.extend(
        [
            Path("/storage/emulated/0/NNN"),
            Path("/sdcard/NNN"),
            Path("/storage/self/primary/NNN"),
        ]
    )
    # App-private fallback (always writable without All-files permission)
    for key in ("HOME", "ANDROID_PRIVATE", "TMPDIR"):
        v = (os.environ.get(key) or "").strip()
        if v:
            candidates.append(Path(v) / "NNN")
    candidates.append(Path("/data/data/org.titannnn.titan/files/NNN"))
    candidates.append(Path.home() / "NNN")

    for c in candidates:
        try:
            c.mkdir(parents=True, exist_ok=True)
            probe = c / ".titan_nnn_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            os.environ["TITAN_HOME"] = str(c)
            os.environ["TITAN_HOST"] = "127.0.0.1"
            os.environ["TITAN_PORT"] = "8080"
            os.environ["TITAN_OPEN_BROWSER"] = "0"
            return
        except Exception:
            continue


def start_server() -> None:
    global _started
    with _lock:
        if _started:
            return
        _started = True

    _prepare_home()

    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))

    # Import the flat unified build (module name = filename without .py)
    import TITAN_PRO_V80_NNN_UNIFIED as titan  # noqa: WPS433

    def run():
        # Prefer run_titan if present (starts live threads + Flask)
        try:
            if hasattr(titan, "run_titan") and callable(titan.run_titan):
                # Ensure host/port env already set
                os.environ.setdefault("TITAN_HOST", "127.0.0.1")
                os.environ.setdefault("TITAN_PORT", "8080")
                titan.run_titan(open_browser=False)
                return
        except Exception:
            pass
        # Fallback: direct Flask
        titan.app.run(
            host="127.0.0.1",
            port=8080,
            debug=False,
            use_reloader=False,
            threaded=True,
        )

    t = threading.Thread(target=run, name="titan-flask", daemon=True)
    t.start()
    time.sleep(1.5)
