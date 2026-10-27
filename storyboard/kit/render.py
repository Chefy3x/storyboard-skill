"""Render a storyboard: 9:16 frames, a contact sheet and a board page.

    python3 render.py <storyboard_dir>

<storyboard_dir> holds storyboard.json and frames/f01.html, frames/f02.html, ...
(the number is the shot's position). Each fragment is inner markup only: this script
wraps it with frame-kit.css and renders a 540x960 PNG with headless Chrome. Image paths
resolve relative to frames/; {{face}} becomes frames/face.jpg if it exists, otherwise a
neutral silhouette.

Writes frames/out/fNN.png, frames/out/contact-sheet.jpg and board.html, and prints the
runtime (VO at 3.4 words per second) and the face vs screen seconds.
"""
import glob, html, json, os, platform, re, shutil, subprocess, sys

WPS = 3.4
KIT = os.path.dirname(os.path.abspath(__file__))
SILHOUETTE = ("data:image/svg+xml;utf8," +
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 540 960'>"
    "<rect width='540' height='960' fill='%23b9bdbd'/>"
    "<circle cx='270' cy='400' r='120' fill='%23999e9e'/>"
    "<path d='M60 960c0-170 94-300 210-300s210 130 210 300z' fill='%23999e9e'/></svg>")


def find_chrome():
    names = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"]
    paths = {
        "Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                   "/Applications/Chromium.app/Contents/MacOS/Chromium",
                   "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
        "Windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"],
    }.get(platform.system(), [])
    for p in paths:
        if os.path.exists(p):
            return p
    for n in names:
        if shutil.which(n):
            return shutil.which(n)
    return None


def file_url(path):
    return "file://" + ("/" if not path.startswith("/") else "") + path.replace("\\", "/")


def render_frames(frames_dir, out_dir):
    chrome = find_chrome()
    if not chrome:
        sys.exit("No Chrome, Chromium or Edge found. Install Google Chrome and run this again.")
    css = open(os.path.join(KIT, "frame-kit.css"), encoding="utf-8").read()
    face_path = os.path.join(frames_dir, "face.jpg")
    face = file_url(face_path) if os.path.exists(face_path) else SILHOUETTE
    pngs = []
    for frag in sorted(glob.glob(os.path.join(frames_dir, "f[0-9][0-9].html"))):
        name = os.path.basename(frag)[:-5]
        body = open(frag, encoding="utf-8").read().replace("{{face}}", face)
        page = os.path.join(frames_dir, f".{name}.page.html")  # beside the fragment so relative src works
        with open(page, "w", encoding="utf-8") as f:
            f.write(f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>")
        png = os.path.join(out_dir, name + ".png")
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                        "--window-size=540,960", f"--screenshot={png}", file_url(page)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(page)
        ok = os.path.exists(png)
        print(name, "ok" if ok else "FAILED")
        if ok:
            pngs.append(png)
    return pngs


def contact_sheet(pngs, out_dir):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("sheet skipped (pip install pillow for a contact sheet)")
        return None
    cols, w, h, pad, lab = 7, 216, 384, 8, 26
    rows = (len(pngs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 2 * pad), rows * (h + 2 * pad + lab)), "#0b0d10")
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(pngs):
        x, y = (i % cols) * (w + 2 * pad) + pad, (i // cols) * (h + 2 * pad + lab) + pad
        sheet.paste(Image.open(p).convert("RGB").resize((w, h)), (x, y))
        draw.text((x + w // 2 - 6, y + h + 6), str(i + 1), fill="#e8e6e1")
    path = os.path.join(out_dir, "contact-sheet.jpg")
    sheet.save(path, quality=85)
    print("sheet", path)
    return path


def secs(vo):
    return len(vo.split()) / WPS


def board(sb_dir, sb, out_dir):
    shots, t, rows = sb.get("shots", []), 0.0, []
    for i, s in enumerate(shots, 1):
        d = secs(s.get("vo", ""))
        png = os.path.join(out_dir, f"f{i:02d}.png")
        img = f"<img src='frames/out/f{i:02d}.png'>" if os.path.exists(png) else "<div class='none'>no frame</div>"
        field = lambda k, label: (f"<p><b>{label}</b> {html.escape(s[k])}</p>" if s.get(k) else "")
        rows.append(
            f"<article{' class=thesis' if s.get('thesis') else ''}>{img}<div>"
            f"<h3>{i:02d} <span>{html.escape(s.get('type', ''))}</span> <i>{t:.1f}s to {t + d:.1f}s</i>"
            f"{' <em>thesis</em>' if s.get('thesis') else ''} <small>{html.escape(s.get('status', ''))}</small></h3>"
            f"<p class=vo>{html.escape(s.get('vo', ''))}</p>"
            f"{field('on_screen_text', 'Text')}{field('edit_note', 'Edit')}{field('sfx', 'SFX')}</div></article>")
        t += d
    sit = "".join(f"<li><b>{html.escape(x.get('label', ''))}</b> shots {', '.join(map(str, x.get('shots', [])))}"
                  f"<br>{html.escape(x.get('detail', ''))}</li>" for x in sb.get("sittings", []))
    title = html.escape(sb.get("title", "Storyboard"))
    page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
body{{margin:0;background:#e4e7e7;color:#1a1410;font:15px/1.45 -apple-system,"Segoe UI",Inter,sans-serif}}
main{{max-width:900px;margin:0 auto;padding:32px 16px 64px}} h1{{font-size:34px;margin:0 0 4px;text-transform:uppercase;letter-spacing:-.02em}}
.meta{{color:#555;margin:0 0 24px}} article{{display:grid;grid-template-columns:180px 1fr;gap:18px;background:#fff;border-radius:14px;padding:14px;margin:0 0 12px}}
article.thesis{{outline:3px solid #3b6cf6}} article img,.none{{width:180px;height:320px;border-radius:8px;object-fit:cover;background:#ccc;display:grid;place-items:center;color:#666}}
h3{{margin:0 0 8px;font-size:15px}} h3 span{{background:#1a1410;color:#fff;border-radius:5px;padding:1px 7px;font-size:12px;text-transform:uppercase}}
h3 i{{color:#777;font-style:normal;font-weight:500}} h3 em{{background:#3b6cf6;color:#fff;font-style:normal;border-radius:5px;padding:1px 7px;font-size:12px}}
h3 small{{color:#999;font-weight:500}} .vo{{font-size:18px;font-weight:600;margin:0 0 10px}} p{{margin:0 0 6px}} p b{{color:#3b6cf6;margin-right:4px}}
ul{{padding-left:20px}} li{{margin:0 0 10px}} @media (max-width:560px){{article{{grid-template-columns:110px 1fr}} article img,.none{{width:110px;height:196px}}}}
</style></head><body><main><h1>{title}</h1><p class="meta">{len(shots)} shots · {t:.1f}s
{f"(target {sb['target_seconds']}s)" if sb.get('target_seconds') else ""}</p>{''.join(rows)}<h2>Sittings</h2><ul>{sit}</ul></main></body></html>"""
    path = os.path.join(sb_dir, "board.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    print("board", path)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sb_dir = os.path.abspath(sys.argv[1])
    frames_dir = os.path.join(sb_dir, "frames")
    out_dir = os.path.join(frames_dir, "out")
    os.makedirs(out_dir, exist_ok=True)
    pngs = render_frames(frames_dir, out_dir) if os.path.isdir(frames_dir) else []
    if pngs:
        contact_sheet(pngs, out_dir)
    sb_path = os.path.join(sb_dir, "storyboard.json")
    if not os.path.exists(sb_path):
        return print("no storyboard.json, so no board.html")
    sb = json.load(open(sb_path, encoding="utf-8"))
    board(sb_dir, sb, out_dir)
    shots = sb.get("shots", [])
    total = sum(secs(s.get("vo", "")) for s in shots)
    face = sum(secs(s.get("vo", "")) for s in shots if s.get("type") in ("face", "split"))
    print(f"{len(shots)} shots, {total:.1f}s; face or split {face:.1f}s, other {total - face:.1f}s")
    if sum(1 for s in shots if s.get("thesis")) != 1:
        print("check: mark exactly one thesis shot")
    if sb.get("target_seconds") and abs(total - sb["target_seconds"]) > 0.15 * sb["target_seconds"]:
        print(f"check: runtime is off the {sb['target_seconds']}s target by more than 15%")


if __name__ == "__main__":
    main()
