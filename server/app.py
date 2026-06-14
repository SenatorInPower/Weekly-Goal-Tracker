#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Weekly Goal Tracker — personal DAILY sync backend.

Stores per-day checklists (dailyLog) per Google account so the PWA stays in sync
between phone and computer. Auth = Google ID token (verified via Google tokeninfo).
Locked to a single allowed email. Behind nginx at https://lnpower.org/tracker-api/.

Endpoints (POST JSON):
  /sync  {idToken, dailyLog}  -> merge with stored (newest-by-mtime per date), return merged
  /load  {idToken}            -> return stored dailyLog
  /health (GET)               -> {ok, configured}
"""
import json, os, time, urllib.request, urllib.parse
from pathlib import Path
from flask import Flask, request, jsonify

BASE = Path('/opt/tracker-sync')
DATA = BASE / 'data'
DATA.mkdir(parents=True, exist_ok=True)


def _env(key, default=''):
    # env var wins; else read BASE/.env (KEY=VALUE lines)
    if key in os.environ:
        return os.environ[key]
    f = BASE / '.env'
    if f.exists():
        for line in f.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                if k.strip() == key:
                    return v.strip()
    return default


CLIENT_ID = _env('TRACKER_CLIENT_ID', '')                       # Google Web OAuth client id (audience)
ALLOWED_EMAIL = _env('TRACKER_ALLOWED_EMAIL', 'baksikpro@gmail.com').lower()
ALLOWED_ORIGINS = {'https://senatorinpower.github.io', 'https://lnpower.org'}

app = Flask(__name__)


@app.after_request
def _cors(resp):
    o = request.headers.get('Origin', '')
    if o in ALLOWED_ORIGINS:
        resp.headers['Access-Control-Allow-Origin'] = o
        resp.headers['Vary'] = 'Origin'
        resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        resp.headers['Access-Control-Max-Age'] = '86400'
    return resp


def verify(idtoken):
    """Verify a Google ID token -> account 'sub', or None. Locked to ALLOWED_EMAIL."""
    if not idtoken:
        return None
    try:
        url = 'https://oauth2.googleapis.com/tokeninfo?' + urllib.parse.urlencode({'id_token': idtoken})
        with urllib.request.urlopen(url, timeout=10) as r:
            c = json.loads(r.read())
    except Exception:
        return None
    if CLIENT_ID and c.get('aud') != CLIENT_ID:
        return None
    if c.get('email', '').lower() != ALLOWED_EMAIL:
        return None
    if str(c.get('email_verified', '')).lower() not in ('true', '1'):
        return None
    return c.get('sub')


def _store(sub):
    return DATA / (str(sub) + '.json')


def load_store(sub):
    p = _store(sub)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def save_store(sub, dailylog):
    _store(sub).write_text(json.dumps(dailylog, ensure_ascii=False), encoding='utf-8')


def merge(a, b):
    """Per-date newest-by-mtime wins."""
    out = dict(a or {})
    for k, v in (b or {}).items():
        if not isinstance(v, dict):
            continue
        if k not in out or (v.get('mtime', 0) > (out[k].get('mtime', 0) if isinstance(out[k], dict) else 0)):
            out[k] = v
    return out


@app.route('/health')
def health():
    # client_id is public by design — PWA fetches it so the Google button can be enabled
    # by setting it ONLY here (VPS .env), without re-deploying the frontend.
    return jsonify(ok=True, configured=bool(CLIENT_ID), client_id=CLIENT_ID)


@app.route('/sync', methods=['POST', 'OPTIONS'])
def sync():
    if request.method == 'OPTIONS':
        return ('', 204)
    body = request.get_json(silent=True) or {}
    sub = verify(body.get('idToken'))
    if not sub:
        return jsonify(error='unauthorized'), 401
    merged = merge(load_store(sub), body.get('dailyLog', {}))
    save_store(sub, merged)
    return jsonify(dailyLog=merged, ts=int(time.time()))


@app.route('/load', methods=['POST', 'OPTIONS'])
def load():
    if request.method == 'OPTIONS':
        return ('', 204)
    body = request.get_json(silent=True) or {}
    sub = verify(body.get('idToken'))
    if not sub:
        return jsonify(error='unauthorized'), 401
    return jsonify(dailyLog=load_store(sub), ts=int(time.time()))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5210, threaded=True)
