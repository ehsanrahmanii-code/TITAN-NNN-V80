"""Start TITAN PRO V80.2 Flask server inside Chaquopy (Android)."""
from __future__ import annotations

import os
import sys
import threading
import time
import traceback
from pathlib import Path

_started = False
_lock = threading.Lock()
_LOG = Path("/data/data/org.titannnn.titan/files/titan_boot.log")


def _log(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}\n"
    try:
        _LOG.parent.mkdir(parents=True, exist_ok=True)
        with _LOG.open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass
    try:
        print(line, end="", file=sys.stderr)
    except Exception:
        pass


def _prepare_home() -> Path:
    """Prefer user-visible Internal Storage/NNN; fall back to app-private."""
    candidates = [
        Path("/storage/emulated/0/NNN"),
        Path("/sdcard/NNN"),
        Path("/storage/self/primary/NNN"),
        Path("/data/data/org.titannnn.titan/files/NNN"),
    ]
    for key in ("HOME", "ANDROID_PRIVATE", "TMPDIR"):
        v = (os.environ.get(key) or "").strip()
        if v:
            candidates.append(Path(v) / "NNN")
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
            global _LOG
            _LOG = c / "titan_boot.log"
            _log(f"home={c}")
            return c
        except Exception as exc:
            _log(f"home_fail {c}: {exc}")
            continue
    c = Path("/data/data/org.titannnn.titan/cache/NNN")
    c.mkdir(parents=True, exist_ok=True)
    os.environ["TITAN_HOME"] = str(c)
    _log(f"home_fallback={c}")
    return c


def _run_titan_server() -> None:
    _log("import TITAN_PRO_V80_NNN_UNIFIED …")
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))

    try:
        import TITAN_PRO_V80_NNN_UNIFIED as titan  # noqa: WPS433
    except Exception as exc:
        _log(f"IMPORT FAIL: {type(exc).__name__}: {exc}\n{traceback.format_exc()}")
        return

    _log("import ok")
    os.environ.setdefault("TITAN_HOST", "127.0.0.1")
    os.environ.setdefault("TITAN_PORT", "8080")

    for name in ("_safe_startup_check", "load_settings", "reload_keys", "init_db"):
        fn = getattr(titan, name, None)
        if callable(fn):
            try:
                fn()
                _log(f"init ok: {name}")
            except Exception as e:
                _log(f"init skip {name}: {e}")

    try:
        if hasattr(titan, "start_live_engine"):
            titan.start_live_engine()
            _log("live_engine ok")
    except Exception as e:
        _log(f"live_engine skip: {e}")

    try:
        if hasattr(titan, "_background_market_refresh"):
            titan._background_market_refresh(True)
            _log("boot scan queued")
    except Exception as e:
        _log(f"boot scan: {e}")

    app = getattr(titan, "app", None)
    if app is None:
        _log("FATAL: titan.app missing")
        return

    try:
        _log("serving on 127.0.0.1:8080")
        app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False, threaded=True)
    except Exception as exc:
        _log(f"SERVE FAIL: {type(exc).__name__}: {exc}\n{traceback.format_exc()}")


def start_server() -> None:
    global _started
    with _lock:
        if _started:
            return
        _started = True

    try:
        _prepare_home()
    except Exception as exc:
        _log(f"prepare_home: {exc}\n{traceback.format_exc()}")

    threading.Thread(target=_run_titan_server, name="titan-flask", daemon=True).start()
    _log("start_server scheduled")
