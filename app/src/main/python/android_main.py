"""Start TITAN PRO V80 Flask server inside Chaquopy (Android).

Binds 127.0.0.1:8080 as early as possible so WebView does not see CONNECTION_REFUSED.
All failures are written to a log file under the app files dir.
"""
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
_STATUS = {"phase": "init", "error": "", "detail": ""}


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
    """App-private NNN first (always writable), then shared storage."""
    candidates = []
    # App-private first — no All-files permission required
    candidates.append(Path("/data/data/org.titannnn.titan/files/NNN"))
    for key in ("HOME", "ANDROID_PRIVATE", "TMPDIR"):
        v = (os.environ.get(key) or "").strip()
        if v:
            candidates.append(Path(v) / "NNN")
    candidates.extend(
        [
            Path("/storage/emulated/0/NNN"),
            Path("/sdcard/NNN"),
            Path("/storage/self/primary/NNN"),
            Path.home() / "NNN",
        ]
    )
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
            os.environ["TITAN_LOG_LEVEL"] = "INFO"
            global _LOG
            _LOG = c / "titan_boot.log"
            _log(f"home={c}")
            return c
        except Exception as exc:
            _log(f"home_fail {c}: {exc}")
            continue
    # Last resort: temp dir
    c = Path("/data/data/org.titannnn.titan/cache/NNN")
    c.mkdir(parents=True, exist_ok=True)
    os.environ["TITAN_HOME"] = str(c)
    _log(f"home_fallback={c}")
    return c


def _boot_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
body{{font-family:sans-serif;background:#0b0f1a;color:#e8ecff;margin:0;padding:24px;line-height:1.7}}
.card{{background:#141a2e;border-radius:16px;padding:20px;max-width:560px;margin:40px auto}}
h1{{font-size:18px;margin:0 0 12px}}
pre{{white-space:pre-wrap;word-break:break-word;background:#0b0f1a;padding:12px;border-radius:10px;font-size:12px;color:#9ab}}
.ok{{color:#5dffa8}}.err{{color:#ff7b8a}}
</style></head><body><div class="card"><h1>{title}</h1>
<div>{body}</div>
<p style="opacity:.6;font-size:12px;margin-top:16px">Titan NNN · boot</p>
</div>
<script>setTimeout(function(){{location.reload()}},4000)</script>
</body></html>"""


def _start_placeholder_server() -> None:
    """Bind 8080 immediately so WebView is not refused while TITAN imports."""
    try:
        from flask import Flask, Response
    except Exception as exc:
        _log(f"flask_import_fail: {exc}")
        return

    boot = Flask("titan_boot")

    @boot.get("/")
    def index():
        phase = _STATUS.get("phase") or "init"
        err = _STATUS.get("error") or ""
        detail = _STATUS.get("detail") or ""
        if phase == "ready":
            return Response(
                _boot_page("آماده", '<p class="ok">سرور آماده است — در حال انتقال…</p>'),
                mimetype="text/html; charset=utf-8",
            )
        if phase == "error":
            return Response(
                _boot_page(
                    "خطای استارت سرور",
                    f'<p class="err">{err}</p><pre>{detail}</pre>'
                    f"<p>فایل لاگ: {_LOG}</p>",
                ),
                mimetype="text/html; charset=utf-8",
            )
        return Response(
            _boot_page(
                "در حال راه‌اندازی TITAN…",
                f"<p>مرحله: <b>{phase}</b></p>"
                "<p>اولین بار ممکن است ۳۰–۹۰ ثانیه طول بکشد (بارگذاری numpy/pandas).</p>",
            ),
            mimetype="text/html; charset=utf-8",
        )

    @boot.get("/health")
    def health():
        return {"ok": _STATUS.get("phase") == "ready", "phase": _STATUS.get("phase"), "error": _STATUS.get("error")}

    def run():
        try:
            _log("placeholder bind 127.0.0.1:8080")
            boot.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False, threaded=True)
        except OSError as exc:
            _log(f"placeholder_bind_fail: {exc}")
            # Port may already be taken by TITAN — fine
        except Exception as exc:
            _log(f"placeholder_fail: {exc}\n{traceback.format_exc()}")

    threading.Thread(target=run, name="titan-boot-http", daemon=True).start()
    time.sleep(0.4)


def _run_titan_server() -> None:
    _STATUS["phase"] = "import"
    _log("import TITAN_PRO_V80_NNN_UNIFIED …")
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))

    try:
        import TITAN_PRO_V80_NNN_UNIFIED as titan  # noqa: WPS433
    except Exception as exc:
        _STATUS["phase"] = "error"
        _STATUS["error"] = f"import failed: {type(exc).__name__}: {exc}"
        _STATUS["detail"] = traceback.format_exc()[-4000:]
        _log(_STATUS["error"] + "\n" + _STATUS["detail"])
        return

    _STATUS["phase"] = "bind"
    _log("import ok — starting Flask app")
    os.environ.setdefault("TITAN_HOST", "127.0.0.1")
    os.environ.setdefault("TITAN_PORT", "8080")

    # Prefer direct app.run (more reliable on Android than full run_titan + waitress)
    try:
        # Light init if available
        for name in ("_safe_startup_check", "load_settings", "reload_keys", "init_db"):
            fn = getattr(titan, name, None)
            if callable(fn):
                try:
                    fn()
                except Exception as e:
                    _log(f"init {name}: {e}")
        try:
            if hasattr(titan, "start_live_engine"):
                titan.start_live_engine()
        except Exception as e:
            _log(f"live_engine: {e}")

        app = getattr(titan, "app", None)
        if app is None:
            raise RuntimeError("titan.app is missing")

        _STATUS["phase"] = "ready"
        _log("serving titan.app on 127.0.0.1:8080")
        # This blocks the worker thread (intended)
        app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False, threaded=True)
    except OSError as exc:
        # Port in use by placeholder — stop placeholder isn't easy; retry shortly
        _log(f"port busy, retry: {exc}")
        time.sleep(1.5)
        try:
            titan.app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False, threaded=True)
            _STATUS["phase"] = "ready"
        except Exception as e2:
            _STATUS["phase"] = "error"
            _STATUS["error"] = f"bind failed: {e2}"
            _STATUS["detail"] = traceback.format_exc()[-4000:]
            _log(_STATUS["error"])
    except Exception as exc:
        _STATUS["phase"] = "error"
        _STATUS["error"] = f"server failed: {type(exc).__name__}: {exc}"
        _STATUS["detail"] = traceback.format_exc()[-4000:]
        _log(_STATUS["error"] + "\n" + _STATUS["detail"])


def start_server() -> None:
    global _started
    with _lock:
        if _started:
            return
        _started = True

    try:
        _prepare_home()
    except Exception as exc:
        _log(f"prepare_home: {exc}")

    _STATUS["phase"] = "boot_http"
    _start_placeholder_server()

    # Heavy TITAN import + serve on a dedicated thread
    threading.Thread(target=_run_titan_server, name="titan-flask", daemon=True).start()
    _log("start_server scheduled")
