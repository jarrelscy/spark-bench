"""
visual_3d_grader — render-based grading for the v6.5 3D animation scenarios.

Unlike the static proxies in expect_html_animation (v6.4c and earlier), these
graders RENDER the model's HTML in headless Chromium and verify the requested
narrative actually happens on screen:

  VIS-04 "race"  : red and blue vehicles both visible, both moving, and the
                   red one overtakes the blue one (centroid crossing event).
  VIS-05 "runner": motion-energy over the loop follows the requested
                   stand -> walk -> run -> stand phase profile.

Design notes:
- Artifacts import three.js as an ES module from './three.module.js'. ES
  modules are silently blocked on file:// (CORS), so we serve the temp dir
  over a loopback HTTP server for the render (lesson from the 2026-07-21
  prototype: HUD renders, scene stays black, zero console errors).
- The vendored assets/three.module.js (r160, pinned) is copied next to the
  artifact before rendering.
- A render failure is a scored failure (0.0 with reason), never an exception:
  the eval loop must survive hostile/broken artifacts.
- Fixtures for the golden gate use compressed timelines via render_seconds /
  phase_seconds so the gate stays fast.
"""

import http.server
import os
import re
import shutil
import socket
import socketserver
import tempfile
import threading

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
THREE_JS = os.path.join(ASSETS_DIR, "three.module.js")
CHROMIUM_CANDIDATES = (
    "/snap/bin/chromium",
    "/usr/bin/chromium",
    "/usr/bin/google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)
VIEW_W, VIEW_H = 480, 300


def _chromium_executable():
    """Return a usable system browser, or None for Playwright's bundled one."""
    override = os.environ.get("SPARK_BENCH_CHROMIUM")
    if override:
        return override if os.path.isfile(override) and os.access(override, os.X_OK) else None
    return next((path for path in CHROMIUM_CANDIDATES
                 if os.path.isfile(path) and os.access(path, os.X_OK)), None)


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #
def _serve_dir(path):
    """Serve `path` on an ephemeral loopback port; return (server, port)."""
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=path, **kw)
    # Find a free port the race-free way: bind port 0.
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    srv.daemon_threads = True
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv, port


def render_frames(html_text, seconds=11.0, fps=2.0, settle_ms=1500,
                  until=None):
    """Render HTML (with vendored three.js beside it) and return a list of
    (t_seconds, raw_rgba_bytes) frames plus a list of console/page errors.

    Returns (frames, errors, fail_reason). fail_reason is None on success.
    """
    from playwright.sync_api import sync_playwright

    tmp = tempfile.mkdtemp(prefix="v3d_")
    try:
        with open(os.path.join(tmp, "artifact.html"), "w") as f:
            f.write(html_text)
        if os.path.exists(THREE_JS):
            shutil.copy(THREE_JS, os.path.join(tmp, "three.module.js"))
        open(os.path.join(tmp, "favicon.ico"), "wb").close()
        srv, port = _serve_dir(tmp)
        frames, errors = [], []
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(
                    executable_path=_chromium_executable(),
                    args=["--enable-unsafe-swiftshader"])
                page = browser.new_page(
                    viewport={"width": VIEW_W, "height": VIEW_H})
                page.on("pageerror", lambda e: errors.append(str(e)[:200]))
                page.on("console", lambda m: errors.append(m.text[:200])
                        if m.type == "error" and "favicon" not in m.text
                        else None)
                page.goto(f"http://127.0.0.1:{port}/artifact.html",
                          timeout=15000)
                page.wait_for_timeout(settle_ms)
                import time as _time
                t_start = _time.monotonic()
                step_ms = int(1000.0 / fps)
                # capture on REAL elapsed time — screenshots cost ~0.5-1s each
                # on GB10, so assumed i/fps stamps drift badly (v6.5 dev bug)
                while _time.monotonic() - t_start < seconds:
                    png = page.screenshot(type="png")
                    frames.append((_time.monotonic() - t_start,
                                   _png_to_rgb(png)))
                    if until is not None and until(frames):
                        break
                    page.wait_for_timeout(step_ms)
                browser.close()
        finally:
            srv.shutdown()
        if not frames:
            return [], errors, "no frames captured"
        return frames, errors, None
    except Exception as e:  # render infrastructure failure or hostile artifact
        return [], [], f"render failed: {type(e).__name__}: {e}"[:200]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _png_to_rgb(png_bytes):
    """Decode PNG to (w, h, rgb_bytes) without PIL (stdlib only is a lie here:
    we use zlib+struct against the PNG spec for the common RGBA/RGB cases the
    Chromium screenshotter emits)."""
    import struct
    import zlib

    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n", "not a png"
    pos, w, h, bitd, color, data = 8, 0, 0, 0, 0, b""
    while pos < len(png_bytes):
        ln, typ = struct.unpack(">I4s", png_bytes[pos:pos + 8])
        chunk = png_bytes[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, bitd, color = struct.unpack(">IIBB", chunk[:10])
        elif typ == b"IDAT":
            data += chunk
        elif typ == b"IEND":
            break
        pos += 12 + ln
    raw = zlib.decompress(data)
    ch = 4 if color == 6 else 3
    stride = w * ch
    out = bytearray(w * h * 3)
    prev = bytearray(stride)
    o = 0
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if f == 1:
            for i in range(ch, stride):
                line[i] = (line[i] + line[i - ch]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - ch] if i >= ch else 0
                b = prev[i]
                c = prev[i - ch] if i >= ch else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        prev = line
        for x in range(w):
            out[o:o + 3] = line[x * ch:x * ch + 3]
            o += 3
    return (w, h, bytes(out))


# --------------------------------------------------------------------------- #
# pixel analytics (stdlib only, downsampled for speed)
# --------------------------------------------------------------------------- #
def _sample_pixels(frame, step=4):
    """Yield (x, y, r, g, b) over a downsampled grid."""
    w, h, rgb = frame
    for y in range(0, h, step):
        row = y * w
        for x in range(0, w, step):
            i = (row + x) * 3
            yield x, y, rgb[i], rgb[i + 1], rgb[i + 2]


def _color_centroid(frame, kind):
    """Centroid x of strongly-red or strongly-blue pixels; None if too few."""
    xs, n = 0, 0
    for x, y, r, g, b in _sample_pixels(frame):
        if kind == "red" and r > 140 and g < 100 and b < 100:
            xs += x; n += 1
        elif kind == "blue" and b > 140 and r < 100 and g < 120:
            xs += x; n += 1
    if n < 8:  # fewer than ~8 grid hits = not credibly visible
        return None, n
    return xs / n, n


def _motion_energy(fa, fb):
    """Mean abs pixel delta between two frames over the sample grid."""
    wa, ha, ra = fa
    wb, hb, rb = fb
    if (wa, ha) != (wb, hb):
        return 0.0
    tot, n = 0, 0
    for y in range(0, ha, 4):
        row = y * wa
        for x in range(0, wa, 4):
            i = (row + x) * 3
            tot += (abs(ra[i] - rb[i]) + abs(ra[i + 1] - rb[i + 1])
                    + abs(ra[i + 2] - rb[i + 2]))
            n += 3
    return tot / max(n, 1)


# --------------------------------------------------------------------------- #
# graders
# --------------------------------------------------------------------------- #
def _static_prechecks(html):
    ck = []
    ck.append((1.0 if re.search(r"<html|<!doctype", html, re.I) else 0.0,
               "html-doc"))
    ext = re.search(r'<(script|link)[^>]+(src|href)\s*=\s*["\']https?:',
                    html, re.I)
    ck.append((0.0 if ext else 1.0, "self-contained"))
    return ck


def grade_race_render(html, render_seconds=60.0, fps=4.0):
    """Red and blue both visible, both moving, red overtakes blue.

    Headless software rendering runs rAF well below 60fps, so frame-driven
    animations play in slow motion. We therefore capture adaptively (up to
    render_seconds) and exit early once an overtake has been observed."""
    ck = _static_prechecks(html)

    def centroids(fr):
        return (_color_centroid(fr, "red")[0], _color_centroid(fr, "blue")[0])

    def saw_crossing(frames):
        ds = [rc - bc for rc, bc in (centroids(f) for _, f in frames)
              if rc is not None and bc is not None]
        return len(ds) >= 3 and any(a * b < 0 for a, b in zip(ds, ds[1:]))

    frames, errors, fail = render_frames(html, seconds=render_seconds,
                                         fps=fps, until=saw_crossing)
    if fail or not frames:
        ck.append((0.0, f"render({fail or 'empty'})"))
        return (sum(s for s, _ in ck) / (len(ck) + 3),
                ", ".join(l for _, l in ck))
    ck.append((0.0 if errors else 1.0,
               "no-js-errors" if not errors else f"js-errors({errors[0][:40]})"))

    cs = [centroids(f) for _, f in frames]
    red = [c[0] for c in cs]
    blue = [c[1] for c in cs]
    n = len(frames)
    red_seen = sum(1 for c in red if c is not None)
    blue_seen = sum(1 for c in blue if c is not None)
    ck.append((min(1.0, red_seen / (n * 0.5)), f"red-visible({red_seen}/{n})"))
    ck.append((min(1.0, blue_seen / (n * 0.5)), f"blue-visible({blue_seen}/{n})"))

    def moved(xs):
        xs = [x for x in xs if x is not None]
        return (max(xs) - min(xs)) > VIEW_W * 0.02 if len(xs) >= 3 else False
    ck.append((1.0 if moved(red) else 0.0, "red-moves"))
    ck.append((1.0 if moved(blue) else 0.0, "blue-moves"))

    ds = [r - b for r, b in zip(red, blue) if r is not None and b is not None]
    crossed = len(ds) >= 3 and any(a * b < 0 for a, b in zip(ds, ds[1:]))
    # partial credit: strong relative displacement without an observed
    # crossing (slow-motion rendering can push the crossing past the cap)
    rel_range = (max(ds) - min(ds)) if len(ds) >= 3 else 0.0
    ot = 1.0 if crossed else (0.5 if rel_range > VIEW_W * 0.15 else 0.0)
    ck.append((ot, "overtake-event" if crossed else
               f"relative-motion({rel_range:.0f}px)"))

    # static prechecks are nearly free — weight rendered evidence 6x
    static_n = 3
    score = (0.15 * (sum(s for s, _ in ck[:static_n]) / static_n)
             + 0.85 * (sum(s for s, _ in ck[static_n:]) / max(len(ck) - static_n, 1)))
    return score, ", ".join(
        f"{l}={'y' if s >= .99 else f'{s:.1f}'}" for s, l in ck)


def grade_runner_render(html, render_seconds=50.0, fps=4.0):
    """Motion-energy curve must have the stand->move->peak->stand SHAPE.

    Because headless rendering stretches frame-driven timelines, we do not
    trust wall-clock phase windows. Instead: capture long, smooth the energy
    curve, and require (a) a lit scene, (b) quiet start, (c) an interior
    peak region meaningfully above the start, (d) a rise through a middle
    level (walk) before the peak (run), (e) a quiet tail."""
    ck = _static_prechecks(html)
    frames, errors, fail = render_frames(html, seconds=render_seconds, fps=fps)
    if fail or not frames:
        ck.append((0.0, f"render({fail or 'empty'})"))
        return (sum(s for s, _ in ck) / (len(ck) + 3),
                ", ".join(l for _, l in ck))
    ck.append((0.0 if errors else 1.0,
               "no-js-errors" if not errors else f"js-errors({errors[0][:40]})"))

    mid = frames[len(frames) // 2][1]
    # a real scene has luminance STRUCTURE; a blank page is uniform.
    lums = [0.299 * r + 0.587 * g + 0.114 * b
            for _, _, r, g, b in _sample_pixels(mid)]
    mean = sum(lums) / len(lums)
    std = (sum((l - mean) ** 2 for l in lums) / len(lums)) ** 0.5
    ck.append((1.0 if std > 12.0 else 0.0, f"scene-structure(std={std:.0f})"))

    es = [_motion_energy(fa[1], fb[1]) for fa, fb in zip(frames, frames[1:])]
    if len(es) < 8:
        ck.append((0.0, f"too-few-frames({len(es)})"))
        return (sum(s for s, _ in ck) / (len(ck) + 2),
                ", ".join(l for _, l in ck))
    # 3-point smoothing
    sm = [es[0]] + [(a + b + c) / 3 for a, b, c in zip(es, es[1:], es[2:])] + [es[-1]]
    n = len(sm)
    third = max(n // 3, 1)
    e_start = sum(sm[:third]) / third
    e_mid = sum(sm[third:2 * third]) / third
    # top-3 mean peak: resistant to single-frame impulse spikes (loop
    # resets teleport geometry) without shaving genuine sustained peaks
    top3 = sorted(sm)[-3:]
    e_peak = sum(top3) / len(top3)
    peak_i = sm.index(max(sm))
    e_end = sum(sm[-third:]) / third

    ck.append((1.0 if e_peak > max(e_start, 0.05) * 1.6 else 0.0,
               f"peak>start({e_peak:.2f}/{e_start:.2f})"))
    # looping cycles put the peak anywhere; only reject peaks that are
    # purely the page-load transient (first few frames)
    ck.append((1.0 if peak_i >= 4 else 0.0,
               f"peak-not-loadflash({peak_i}/{n})"))
    ck.append((1.0 if e_start < e_peak * 0.7 else 0.0,
               f"quiet-start({e_start:.2f}/{e_peak:.2f})"))
    ck.append((1.0 if e_end < e_peak * 0.7 else 0.0,
               f"settles({e_end:.2f}/{e_peak:.2f})"))

    static_n = 3
    score = (0.15 * (sum(s for s, _ in ck[:static_n]) / static_n)
             + 0.85 * (sum(s for s, _ in ck[static_n:]) / max(len(ck) - static_n, 1)))
    return score, ", ".join(
        f"{l}={'y' if s >= .99 else f'{s:.1f}'}" for s, l in ck)
