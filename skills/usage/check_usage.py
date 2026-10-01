#!/usr/bin/env python3
"""Print Claude plan usage: the data behind Claude Code's /usage view."""
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import unicodedata
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_DIR = os.environ.get("CLAUDE_CONFIG_DIR")
URL = "https://api.anthropic.com/api/oauth/usage"
WINDOW = {"session": timedelta(hours=5), "weekly": timedelta(days=7)}
STAMP = "%a %Y-%m-%d %H:%M"


def credentials():
    if sys.platform == "darwin":
        service = "Claude Code-credentials"
        if CONFIG_DIR:
            # Claude Code suffixes the Keychain item for a custom config dir.
            digest = hashlib.sha256(unicodedata.normalize("NFC", CONFIG_DIR).encode())
            service += "-" + digest.hexdigest()[:8]
        return subprocess.run(
            ["/usr/bin/security", "find-generic-password", "-s", service, "-w"],
            capture_output=True, text=True, check=True,
        ).stdout
    return (Path(CONFIG_DIR or Path.home() / ".claude") / ".credentials.json").read_text()


def fetch():
    token = json.loads(credentials())["claudeAiOauth"]["accessToken"]
    request = urllib.request.Request(URL, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            minutes = -(-int(e.headers["retry-after"]) // 60)
            sys.exit(f"rate-limited: try again in {minutes}m")
        sys.exit(f"usage request failed: HTTP {e.code}\n{e.read().decode()}")


def until(reset, now):
    minutes = max(0, int((reset - now).total_seconds() // 60))
    hours, m = divmod(minutes, 60)
    days, h = divmod(hours, 24)
    if days:
        return f"{days}d{h}h{m:02d}m"
    if hours:
        return f"{hours}h{m:02d}m"
    return f"{m}m"


def pace(limit, reset, now):
    """Project usage at reset, assuming the rate so far in the window continues."""
    window = WINDOW[limit["group"]]
    start = reset - window
    elapsed = now - start
    percent = limit["percent"]
    if elapsed < window / 10 or percent >= 100:
        return ""
    projected = percent * (window / elapsed)
    if projected <= 100:
        return f", on pace for {projected:.0f}% by reset"
    out = minute(start + elapsed * 100 / percent)
    return f", on pace to run out in {until(out, now)} at {out.strftime(STAMP)}"


def minute(dt):
    return (dt + timedelta(seconds=30)).replace(second=0, microsecond=0)


def fmt(data, now):
    now = minute(now)
    lines = [now.strftime(f"now {STAMP} %Z")]
    for limit in data["limits"]:
        reset = minute(datetime.fromisoformat(limit["resets_at"]).astimezone())
        model = ((limit.get("scope") or {}).get("model") or {}).get("display_name")
        name = f'{limit["group"]} {model or "(all models)"}'
        lines.append("%s: %d%% used, resets in %s at %s%s" % (
            name, limit["percent"], until(reset, now), reset.strftime(STAMP), pace(limit, reset, now),
        ))
    spend = data["spend"]
    if spend["enabled"]:
        used = spend["used"]
        lines.append(
            "spend: %.2f %s, %d%% used"
            % (used["amount_minor"] / 10 ** used["exponent"], used["currency"], spend["percent"])
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(fmt(fetch(), datetime.now().astimezone()))
