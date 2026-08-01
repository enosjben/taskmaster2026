#!/usr/bin/env python3
"""Party server: the board on the TV, the scoring remote on your phone.

Run this on the laptop driving the TV. It holds the night's scores and pushes
every change to whoever is watching, so submitting a round on the phone lands
on the TV at once.

    python3 server.py

Then open the board at the printed address on the laptop, and the remote at
/remote on your phone. Both devices need to be on the same wifi; nothing goes
near the internet.
"""

import json
import queue
import socket
import threading
import pathlib
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).parent
BOARD = ROOT / "index.html"
REMOTE = ROOT / "remote.html"
SAVE = ROOT / "party-state.json"

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

# Mirrors TASKS in the pages: (name, buttons up to, open-ended). The relay is
# the finale, worth more, and open-ended in case it runs away with itself.
OPEN_LIMIT = 999
TASKS = [
    ("Longest Line", 5, False),
    ("Coolest Phone Photo", 5, False),
    ("Recreate Phone Photo", 5, False),
    ("Treasure Hunt", 5, False),
    ("Hit Song", 5, False),
    ("Museum Piece", 5, False),
    ("Painting", 5, False),
    ("Commercial", 5, False),
    ("Relay", 15, True),
]
TEAMS = ["Red Team", "Yellow Team", "Green Team", "Blue Team", "Purple Team"]

_lock = threading.Lock()
_subscribers = set()


def blank_state():
    return {
        "title": "Taskmaster",
        "seal": "BE",
        "teams": [{"name": n, "roster": ""} for n in TEAMS],
        "scores": [[None] * len(TEAMS) for _ in TASKS],
        "rev": 0,
    }


def load_state():
    if SAVE.exists():
        try:
            saved = json.loads(SAVE.read_text(encoding="utf-8"))
            state = blank_state()
            state.update({k: saved[k] for k in ("title", "seal") if k in saved})
            if isinstance(saved.get("teams"), list):
                for i, t in enumerate(saved["teams"][: len(TEAMS)]):
                    if isinstance(t, dict):
                        state["teams"][i].update(
                            {k: t[k] for k in ("name", "roster") if isinstance(t.get(k), str)}
                        )
            if isinstance(saved.get("scores"), list):
                for r, row in enumerate(saved["scores"][: len(TASKS)]):
                    if isinstance(row, list):
                        for c, v in enumerate(row[: len(TEAMS)]):
                            state["scores"][r][c] = v if valid(r, v) else None
            state["rev"] = int(saved.get("rev", 0))
            return state
        except Exception as exc:                       # noqa: BLE001
            print(f"  could not read {SAVE.name} ({exc}); starting a fresh night")
    return blank_state()


def valid(task_index, value):
    if not isinstance(value, int) or isinstance(value, bool):
        return False
    name, buttons, open_ended = TASKS[task_index]
    return 0 <= value <= (OPEN_LIMIT if open_ended else buttons)


STATE = load_state()


def persist():
    try:
        SAVE.write_text(json.dumps(STATE), encoding="utf-8")
    except OSError as exc:                             # noqa: BLE001
        print(f"  could not save state: {exc}")


def broadcast():
    """Hand the current state to every open stream."""
    payload = json.dumps(STATE)
    for q in list(_subscribers):
        try:
            q.put_nowait(payload)
        except queue.Full:
            _subscribers.discard(q)


def apply_round(task_index, scores):
    """Write a whole round at once, so the board updates in one go."""
    with _lock:
        for c, v in enumerate(scores[: len(TEAMS)]):
            if v is None or valid(task_index, v):
                STATE["scores"][task_index][c] = v
        STATE["rev"] += 1
        persist()
        broadcast()


def apply_patch(patch):
    with _lock:
        if isinstance(patch.get("title"), str):
            STATE["title"] = patch["title"]
        if isinstance(patch.get("seal"), str):
            STATE["seal"] = patch["seal"]
        if isinstance(patch.get("teams"), list):
            for i, t in enumerate(patch["teams"][: len(TEAMS)]):
                if isinstance(t, dict):
                    for k in ("name", "roster"):
                        if isinstance(t.get(k), str):
                            STATE["teams"][i][k] = t[k]
        if isinstance(patch.get("scores"), list):
            for r, row in enumerate(patch["scores"][: len(TASKS)]):
                if isinstance(row, list):
                    for c, v in enumerate(row[: len(TEAMS)]):
                        STATE["scores"][r][c] = v if valid(r, v) else None
        STATE["rev"] += 1
        persist()
        broadcast()


def reset_scores():
    with _lock:
        STATE["scores"] = [[None] * len(TEAMS) for _ in TASKS]
        STATE["rev"] += 1
        persist()
        broadcast()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass                                            # keep the console quiet

    # ── helpers ──────────────────────────────────────────────
    def _send(self, code, body=b"", ctype="text/plain; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _page(self, path):
        if not path.exists():
            self._send(404, b"Not built yet - run: python3 build.py")
            return
        self._send(200, path.read_bytes(), "text/html; charset=utf-8")

    def _json(self, obj):
        self._send(200, json.dumps(obj).encode(), "application/json")

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except (ValueError, TypeError):
            return {}

    # ── routes ───────────────────────────────────────────────
    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path == "/":
            self._page(BOARD)
        elif path == "/remote":
            self._page(REMOTE)
        elif path == "/api/state":
            self._json(STATE)
        elif path == "/api/tasks":
            self._json({
                "tasks": [{"name": n, "max": m, "open": o} for n, m, o in TASKS],
                "teams": STATE["teams"],
            })
        elif path == "/api/events":
            self._stream()
        else:
            self._send(404, b"not found")

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        body = self._body()
        if path == "/api/round":
            task = body.get("task")
            scores = body.get("scores")
            if not isinstance(task, int) or not 0 <= task < len(TASKS) \
               or not isinstance(scores, list):
                self._send(400, b"expected {task:int, scores:[...]}")
                return
            apply_round(task, scores)
            self._json({"ok": True, "rev": STATE["rev"]})
        elif path == "/api/state":
            apply_patch(body)
            self._json({"ok": True, "rev": STATE["rev"]})
        elif path == "/api/reset":
            reset_scores()
            self._json({"ok": True, "rev": STATE["rev"]})
        else:
            self._send(404, b"not found")

    # ── live stream ──────────────────────────────────────────
    def _stream(self):
        q = queue.Queue(maxsize=32)
        _subscribers.add(q)
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(f"data: {json.dumps(STATE)}\n\n".encode())
            self.wfile.flush()
            while True:
                try:
                    payload = q.get(timeout=20)
                    self.wfile.write(f"data: {payload}\n\n".encode())
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")     # keep phones from dozing off
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            _subscribers.discard(q)


def lan_addresses():
    """Best guess at the addresses a phone on the same wifi can reach."""
    found = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))                      # no packets are sent
        found.append(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127.") and ip not in found:
                found.append(ip)
    except OSError:
        pass
    return found


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True

    hosts = lan_addresses()
    print()
    print("  TASKMASTER is running.")
    print()
    print(f"    Board  (this laptop) :  http://localhost:{PORT}/")
    if hosts:
        for ip in hosts:
            print(f"    Remote (your phone)  :  http://{ip}:{PORT}/remote")
    else:
        print(f"    Remote (your phone)  :  http://<this-laptop's-ip>:{PORT}/remote")
    print()
    print(f"  Scores are saved to {SAVE.name} as you go. Ctrl+C to stop.")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped. The scores are safe in " + SAVE.name + ".\n")


if __name__ == "__main__":
    main()
