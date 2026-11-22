"""Generate the animated 'tilted ticker' GitHub profile header (light + dark).

Text is converted to SVG paths (Anton, OFL) so it renders the same everywhere,
since an SVG served through <img> on GitHub can't load web fonts.
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT = TTFont(sys.argv[1])
OUT = sys.argv[2]
GS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
UPM = FONT["head"].unitsPerEm
HMTX = FONT["hmtx"]

W, H = 1280, 440

THEMES = {
    "light": dict(bg="#F3F3F1", ink="#0B0B0C", muted="#6B6B72", line="#DCDCD8", blue="#1F5EFF", on_ink="#F3F3F1", on_blue="#FFFFFF", edge="#2A2A2E"),
    "dark": dict(bg="#0B0B0C", ink="#F3F3F1", muted="#9A9AA2", line="#2A2A2E", blue="#1F5EFF", on_ink="#0B0B0C", on_blue="#FFFFFF", edge="#B9B9B4"),
}


def text_path(s, size, tracking=0.0):
    """Return (svg path d, width) for string s at font size, baseline at y=0."""
    scale = size / UPM
    pen = SVGPathPen(GS)
    x = 0.0
    for ch in s:
        if ch == " ":
            x += HMTX["space"][0] * scale + tracking
            continue
        gname = CMAP[ord(ch)]
        tp = TransformPen(pen, (scale, 0, 0, -scale, x, 0))
        GS[gname].draw(tp)
        x += HMTX[gname][0] * scale + tracking
    return pen.getCommands(), x - tracking


def star(cx, cy, r):
    """Four-point sparkle like the portfolio's ✦ separator."""
    k = r * 0.28
    return (f"M{cx},{cy - r} Q{cx + k},{cy - k} {cx + r},{cy} Q{cx + k},{cy + k} {cx},{cy + r} "
            f"Q{cx - k},{cy + k} {cx - r},{cy} Q{cx - k},{cy - k} {cx},{cy - r}Z")


def sequence(items, size, gap, star_r):
    """One loop of ticker text: words separated by sparkles. Returns (text d, star d, width)."""
    text_d, star_d, x = [], [], 0.0
    cap = FONT["OS/2"].sCapHeight * size / UPM
    for it in items:
        d, w = text_path(it, size, tracking=size * 0.01)
        text_d.append(f'<path transform="translate({x:.1f},0)" d="{d}"/>')
        x += w + gap
        star_d.append(star(x, -cap / 2, star_r))
        x += gap
    return "".join(text_d), " ".join(star_d), x


FRONT = ["Backend systems", "REST APIs", "Real-time", "Dashboards", "Offline-first", "AI integration"]
BACK = ["Node.js", "Express", "PostgreSQL", "MySQL", "Supabase", "Next.js", "React Native", "Flutter", "Cloudflare"]
FRONT = [s.upper() for s in FRONT]
BACK = [s.upper() for s in BACK]

name_d, name_w = text_path("FERAS HAMDOUNA", 128, tracking=1)
label_d, label_w = text_path("BACKEND DEVELOPER", 22, tracking=2.2)

f_text, f_stars, f_w = sequence(FRONT, 44, 26, 9)
b_text, b_stars, b_w = sequence(BACK, 30, 20, 6)


def ribbon(rid, text_d, stars_d, seq_w, cy, height, angle, fill, text_fill, star_fill, edge, direction, speed, baseline):
    """A tilted band with a scrolling, repeating text sequence and a thin 'thickness' edge."""
    copies = int((W + 400) // seq_w) + 2
    uses = "".join(f'<use href="#{rid}-seq" x="{i * seq_w:.1f}"/>' for i in range(copies))
    anim = f"{rid}-move"
    frm, to = ("0", f"-{seq_w:.1f}") if direction == "left" else (f"-{seq_w:.1f}", "0")
    dur = seq_w / speed
    y0 = cy - height / 2
    return f"""
  <style>
    @keyframes {anim} {{ from {{ transform: translateX({frm}px); }} to {{ transform: translateX({to}px); }} }}
    #{rid}-track {{ animation: {anim} {dur:.1f}s linear infinite; }}
  </style>
  <defs>
    <g id="{rid}-seq"><g fill="{text_fill}">{text_d}</g><path fill="{star_fill}" d="{stars_d}"/></g>
  </defs>
  <g transform="rotate({angle} {W / 2} {cy}) skewX({-angle * 2.2:.2f})">
    <rect x="-300" y="{y0 + 7:.1f}" width="{W + 600}" height="{height}" fill="{edge}"/>
    <rect x="-300" y="{y0:.1f}" width="{W + 600}" height="{height}" fill="{fill}"/>
    <g transform="translate(-200,{y0 + baseline:.1f})"><g id="{rid}-track">{uses}</g></g>
  </g>"""


def build(theme):
    t = THEMES[theme]
    back = ribbon("b", b_text, b_stars, b_w, cy=378, height=48, angle=2.4, fill=t["blue"],
                  text_fill=t["on_blue"], star_fill=t["on_blue"], edge="#0F3BB0",
                  direction="right", speed=38, baseline=36)
    front = ribbon("f", f_text, f_stars, f_w, cy=372, height=70, angle=-3.0, fill=t["ink"],
                   text_fill=t["on_ink"], star_fill=t["blue"], edge=t["edge"],
                   direction="left", speed=55, baseline=58)
    cap = FONT["OS/2"].sCapHeight * 22 / UPM
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">Feras Hamdouna — Backend Developer</title>
  <desc id="d">Feras Hamdouna, Backend Developer. Builds complete systems from the database to the interface: backend systems, REST APIs, real-time, dashboards, offline-first apps and AI integration.</desc>
  <style>
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(.78); }} }}
    .in {{ animation: rise .9s cubic-bezier(.2,.7,.2,1) both; }}
    .d1 {{ animation-delay: .1s; }} .d2 {{ animation-delay: .25s; }} .d3 {{ animation-delay: .4s; }}
    #spark {{ transform-box: fill-box; transform-origin: center; animation: pulse 2.4s ease-in-out infinite; }}
    @media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation: none !important; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="24" fill="{t['bg']}"/>
  <g class="in d1"><g transform="translate(72,84)">
    <path id="spark" fill="{t['blue']}" d="{star(9, -cap / 2, 9)}"/>
    <path transform="translate(30,0)" fill="{t['muted']}" d="{label_d}"/></g>
  </g>
  <g class="in d2"><path transform="translate(68,222)" fill="{t['ink']}" d="{name_d}"/></g>
  <text class="in d3" x="72" y="270" fill="{t['muted']}" font-family="-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="22">I build complete systems, from the database to the interface.</text>
  <svg x="0" y="0" width="{W}" height="{H}" overflow="hidden">
    <clipPath id="clip"><rect width="{W}" height="{H}" rx="24"/></clipPath>
    <g clip-path="url(#clip)">{back}{front}
    </g>
  </svg>
</svg>
"""


for th in THEMES:
    with open(f"{OUT}/header-{th}.svg", "w", encoding="utf-8") as fh:
        fh.write(build(th))
print("name width", round(name_w), "front seq", round(f_w), "back seq", round(b_w))
