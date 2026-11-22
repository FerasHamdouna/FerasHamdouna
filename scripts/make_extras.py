"""Animated SVGs for the lower part of the GitHub profile README:
three project cards, a stack board and a footer ribbon, in light and dark.
Same identity as the header: off-white / ink, blue #1F5EFF, Anton (as paths), sparkle separators.
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
CAP = FONT["OS/2"].sCapHeight / UPM
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

THEMES = {
    "light": dict(bg="#F3F3F1", card="#FFFFFF", ink="#0B0B0C", muted="#6B6B72", line="#DCDCD8",
                  blue="#1F5EFF", soft="#E8EEFF", on_ink="#F3F3F1", edge="#2A2A2E"),
    "dark": dict(bg="#0B0B0C", card="#141416", ink="#F3F3F1", muted="#9A9AA2", line="#2A2A2E",
                 blue="#1F5EFF", soft="#14204A", on_ink="#0B0B0C", edge="#B9B9B4"),
}

REDUCED = "@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; } }"


def text_path(s, size, tracking=0.0):
    scale = size / UPM
    pen = SVGPathPen(GS)
    x = 0.0
    for ch in s:
        if ch == " ":
            x += HMTX["space"][0] * scale + tracking
            continue
        g = CMAP[ord(ch)]
        GS[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x, 0)))
        x += HMTX[g][0] * scale + tracking
    return pen.getCommands(), x - tracking


def star(cx, cy, r):
    k = r * 0.28
    return (f"M{cx:.1f},{cy - r:.1f} Q{cx + k:.1f},{cy - k:.1f} {cx + r:.1f},{cy:.1f} Q{cx + k:.1f},{cy + k:.1f} {cx:.1f},{cy + r:.1f} "
            f"Q{cx - k:.1f},{cy + k:.1f} {cx - r:.1f},{cy:.1f} Q{cx - k:.1f},{cy - k:.1f} {cx:.1f},{cy - r:.1f}Z")


def svg(w, h, title, desc, style, body, t):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">
  <title id="t">{title}</title>
  <desc id="d">{desc}</desc>
  <style>
    @keyframes rise {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(.75); }} }}
    .in {{ animation: rise .8s cubic-bezier(.2,.7,.2,1) both; }}
    .spark {{ transform-box: fill-box; transform-origin: center; animation: pulse 2.4s ease-in-out infinite; }}
    {style}
    {REDUCED}
  </style>
  <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="22" fill="{t['bg']}" stroke="{t['line']}" stroke-width="2"/>
{body}
</svg>
"""


def chips(tags, x, y, t, size=16, gap=10, cls=""):
    """Outlined pill tags in Anton. Returns (svg, end x)."""
    out = []
    for tag in tags:
        d, w = text_path(tag.upper(), size, tracking=0.8)
        cw = w + 28
        out.append(f'<g class="{cls}" transform="translate({x:.1f},{y})"><rect width="{cw:.1f}" height="32" rx="16" fill="none" stroke="{t["line"]}" stroke-width="2"/>'
                   f'<path transform="translate(14,{16 + size * CAP / 2:.1f})" fill="{t["ink"]}" d="{d}"/></g>')
        x += cw + gap
    return "".join(out), x


# ---------- project cards ----------

CW, CH = 1280, 270


def card_frame(t, num, name, tagline, tags):
    num_d, _ = text_path(num, 20, tracking=2)
    name_d, _ = text_path(name.upper(), 66, tracking=1)
    tag_svg, _ = chips(tags, 56, 206, t)
    return f"""  <g class="in" style="animation-delay:.05s"><path class="spark" fill="{t['blue']}" d="{star(64, 58, 8)}"/>
    <path transform="translate(82,65)" fill="{t['muted']}" d="{num_d}"/></g>
  <g class="in" style="animation-delay:.15s"><path transform="translate(54,146)" fill="{t['ink']}" d="{name_d}"/></g>
  <text class="in" style="animation-delay:.25s" x="56" y="184" fill="{t['muted']}" font-family="{SANS}" font-size="21">{tagline}</text>
  <g class="in" style="animation-delay:.35s">{tag_svg}</g>
  <rect x="840" y="28" width="412" height="214" rx="16" fill="{t['card']}" stroke="{t['line']}" stroke-width="2"/>"""


def staged(prefix, loop, starts, dx=0, dy=10):
    """One keyframe set per element so items appear one by one, then all leave together and the loop restarts clean."""
    css = []
    for i, s in enumerate(starts):
        a = s / loop * 100
        css.append(f"@keyframes {prefix}{i} {{ 0%, {a:.1f}% {{ opacity: 0; transform: translate({dx}px,{dy}px); }} {a + 6:.1f}%, 88% {{ opacity: 1; transform: none; }} 95%, 100% {{ opacity: 0; }} }}"
                   f" .{prefix}{i} {{ opacity: 0; animation: {prefix}{i} {loop}s cubic-bezier(.2,.7,.2,1) infinite; }}")
    return "\n    ".join(css)


def bubble(x, y, w, text, mine, t, idx):
    fill = t["blue"] if mine else t["bg"]
    stroke = t["blue"] if mine else t["line"]
    color = "#FFFFFF" if mine else t["ink"]
    return (f'<g class="msg{idx}"><rect x="{x}" y="{y}" width="{w}" height="40" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<text x="{x + 16}" y="{y + 26}" fill="{color}" font-family="{SANS}" font-size="16">{text}</text></g>')


def gazagate(t):
    loop = 7
    style = f"""
    {staged("msg", loop, [0.3, 1.6, 3.0])}
    @keyframes dot {{ 0%, 60%, 100% {{ opacity: .25; }} 30% {{ opacity: 1; }} }}
    .dot {{ animation: dot 1.2s ease-in-out infinite; }}
    @keyframes live {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: .35; }} }}
    .live {{ animation: live 1.6s ease-in-out infinite; }}"""
    head_d, _ = text_path("SELLER CHAT", 15, tracking=1.2)
    body = card_frame(t, "01", "Gaza Gate", "Local marketplace with multi-seller orders and real-time chat.",
                      ["Socket.io", "Multi-seller", "Trust score", "MySQL"])
    body += f"""
  <path transform="translate(866,62)" fill="{t['muted']}" d="{head_d}"/>
  <circle class="live" cx="1226" cy="56" r="6" fill="#22C55E"/>
  <line x1="840" y1="78" x2="1252" y2="78" stroke="{t['line']}" stroke-width="2"/>
  {bubble(864, 92, 210, "Is this still available?", False, t, 0)}
  {bubble(1010, 142, 222, "Yes, it ships today", True, t, 1)}
  {bubble(864, 192, 150, "Ordering now", False, t, 2)}
  <g transform="translate(1188,212)"><circle class="dot" cx="0" cy="0" r="4" fill="{t['muted']}"/><circle class="dot" style="animation-delay:.2s" cx="13" cy="0" r="4" fill="{t['muted']}"/><circle class="dot" style="animation-delay:.4s" cx="26" cy="0" r="4" fill="{t['muted']}"/></g>"""
    return svg(CW, CH, "Gaza Gate", "Gaza Gate: local marketplace with multi-seller orders, real-time chat over Socket.io and a seller trust score.", style, body, t)


def dafter(t):
    loop = 8
    rows = [("Bread and milk", "+ 12.50"), ("Paid cash", "- 10.00"), ("Rice 5 kg", "+ 18.00"), ("Sugar", "+ 6.25")]
    style = f"""
    {staged("row", loop, [0.3, 1.2, 2.1, 3.0], dy=14)}
    @keyframes off {{ 0%, 55% {{ opacity: 1; }} 60%, 100% {{ opacity: 0; }} }}
    @keyframes on {{ 0%, 55% {{ opacity: 0; }} 60%, 92% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
    .off {{ animation: off {loop}s steps(1) infinite; }} .on {{ opacity: 0; animation: on {loop}s steps(1) infinite; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .spin {{ transform-box: fill-box; transform-origin: center; animation: spin 1.4s linear infinite; }}"""
    head_d, _ = text_path("LEDGER · APPEND-ONLY", 15, tracking=1.2)
    off_d, ow = text_path("OFFLINE", 13, tracking=1)
    on_d, nw = text_path("SYNCED", 13, tracking=1)
    body = card_frame(t, "02", "Dafter", "Digital debt ledger for shops. Works offline, syncs when back online.",
                      ["Offline-first", "Append-only", "OpenAPI", "Sync"])
    body += f"""
  <path transform="translate(866,62)" fill="{t['muted']}" d="{head_d}"/>
  <g class="off"><rect x="{1228 - ow - 20:.1f}" y="44" width="{ow + 20:.1f}" height="24" rx="12" fill="none" stroke="{t['muted']}" stroke-width="2"/>
    <path transform="translate({1238 - ow - 20:.1f},{56 + 13 * CAP / 2:.1f})" fill="{t['muted']}" d="{off_d}"/></g>
  <g class="on"><rect x="{1228 - nw - 20:.1f}" y="44" width="{nw + 20:.1f}" height="24" rx="12" fill="{t['blue']}"/>
    <path transform="translate({1238 - nw - 20:.1f},{56 + 13 * CAP / 2:.1f})" fill="#FFFFFF" d="{on_d}"/></g>
  <line x1="840" y1="78" x2="1252" y2="78" stroke="{t['line']}" stroke-width="2"/>"""
    for i, (label, amt) in enumerate(rows):
        y = 104 + i * 36
        col = t["blue"] if amt.startswith("+") else t["muted"]
        body += f"""
  <g class="row{i}"><text x="866" y="{y}" fill="{t['ink']}" font-family="{SANS}" font-size="16">{label}</text>
    <text x="1226" y="{y}" text-anchor="end" fill="{col}" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="16">{amt}</text>
    <line x1="866" y1="{y + 12}" x2="1226" y2="{y + 12}" stroke="{t['line']}" stroke-width="1" stroke-dasharray="3 5"/></g>"""
    return svg(CW, CH, "Dafter", "Dafter: digital debt ledger for neighborhood shops with offline-first sync, an append-only ledger and a contract-first OpenAPI spec.", style, body, t)


def qr_cells():
    """A fixed QR-looking pattern (decorative, not a real code)."""
    import random
    rnd = random.Random(7)
    n = 17
    cells = set()
    for r in range(n):
        for c in range(n):
            finder = any(r0 <= r < r0 + 7 and c0 <= c < c0 + 7 for r0, c0 in ((0, 0), (0, n - 7), (n - 7, 0)))
            if finder:
                rr, cc = (r % (n - 7) if r >= n - 7 else r), (c % (n - 7) if c >= n - 7 else c)
                ring = rr in (0, 6) or cc in (0, 6) or (2 <= rr <= 4 and 2 <= cc <= 4)
                if ring:
                    cells.add((r, c))
            elif not (r < 8 and c < 8) and not (r < 8 and c >= n - 8) and not (r >= n - 8 and c < 8):
                if rnd.random() < 0.48:
                    cells.add((r, c))
    return n, cells


def rivera(t):
    loop = 3.2
    n, cells = qr_cells()
    size, x0, y0 = 170, 872, 52
    cs = size / n
    rects = "".join(f'<rect x="{x0 + c * cs:.1f}" y="{y0 + r * cs:.1f}" width="{cs + .3:.1f}" height="{cs + .3:.1f}"/>' for r, c in cells)
    style = f"""
    @keyframes scan {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY({size - 4}px); }} }}
    .scan {{ animation: scan {loop}s ease-in-out infinite; }}
    {staged("item", 7, [0.4, 1.0, 1.6, 2.2], dx=10, dy=0)}"""
    menu = [("Espresso", "8"), ("Latte", "12"), ("Club sandwich", "22"), ("Cheesecake", "15")]
    head_d, _ = text_path("MENU", 15, tracking=1.2)
    body = card_frame(t, "03", "Rivera", "Digital QR menu and admin dashboard for a cafe and restaurant.",
                      ["Next.js", "Supabase", "Row Level Security", "QR"])
    body += f"""
  <g fill="{t['ink']}">{rects}</g>
  <rect class="scan" x="{x0 - 8}" y="{y0}" width="{size + 16}" height="4" rx="2" fill="{t['blue']}" opacity=".9"/>
  <path transform="translate(1072,66)" fill="{t['muted']}" d="{head_d}"/>"""
    for i, (item, price) in enumerate(menu):
        y = 104 + i * 36
        body += f"""
  <g class="item{i}"><text x="1072" y="{y}" fill="{t['ink']}" font-family="{SANS}" font-size="16">{item}</text>
    <text x="1228" y="{y}" text-anchor="end" fill="{t['blue']}" font-family="{SANS}" font-size="16">{price}</text></g>"""
    return svg(CW, CH, "Rivera", "Rivera: digital QR menu and admin dashboard for a cafe and restaurant, built on Supabase with Row Level Security.", style, body, t)


# ---------- stack board ----------

STACK = [
    ("Backend", ["Node.js", "Express", "Sequelize", "Socket.io", "REST", "OpenAPI"]),
    ("Databases", ["PostgreSQL", "MySQL", "Supabase", "SQLite"]),
    ("Web and mobile", ["React", "Next.js", "React Native", "Expo", "Flutter", "Tailwind"]),
    ("Deploy", ["Coolify", "Cloudflare", "Vercel"]),
]


def stack(t):
    W, H = 1280, 336
    loop = 9
    total = sum(len(r[1]) for r in STACK)
    style = f"""
    @keyframes glow {{ 0%, 4% {{ fill: {t['blue']}; stroke: {t['blue']}; }} 9%, 100% {{ fill: transparent; stroke: {t['line']}; }} }}
    @keyframes glowt {{ 0%, 4% {{ fill: #FFFFFF; }} 9%, 100% {{ fill: {t['ink']}; }} }}
    .chip rect {{ animation: glow {loop}s linear infinite; }}
    .chip path {{ animation: glowt {loop}s linear infinite; }}"""
    body, k = "", 0
    for i, (label, items) in enumerate(STACK):
        y = 44 + i * 72
        ld, _ = text_path(label.upper(), 18, tracking=1.5)
        body += f'\n  <g class="in" style="animation-delay:{0.1 + i * 0.12:.2f}s"><path class="spark" style="animation-delay:{i * 0.4:.1f}s" fill="{t["blue"]}" d="{star(62, y + 16, 7)}"/><path transform="translate(80,{y + 16 + 18 * CAP / 2:.1f})" fill="{t["muted"]}" d="{ld}"/>'
        x = 290
        for it in items:
            d, w = text_path(it.upper(), 17, tracking=0.8)
            cw = w + 32
            delay = k * loop / total
            body += (f'<g class="chip" transform="translate({x:.1f},{y})"><rect style="animation-delay:{delay:.2f}s" width="{cw:.1f}" height="34" rx="17" fill="transparent" stroke="{t["line"]}" stroke-width="2"/>'
                     f'<path style="animation-delay:{delay:.2f}s" transform="translate(16,{17 + 17 * CAP / 2:.1f})" fill="{t["ink"]}" d="{d}"/></g>')
            x += cw + 12
            k += 1
        body += "</g>"
        if i < len(STACK) - 1:
            body += f'\n  <line x1="56" y1="{y + 54}" x2="{W - 56}" y2="{y + 54}" stroke="{t["line"]}" stroke-width="1.5" stroke-dasharray="2 6"/>'
    desc = "Stack. " + ". ".join(f"{l}: {', '.join(i)}" for l, i in STACK) + "."
    return svg(W, H, "Stack", desc, style, body, t)


# ---------- footer ribbon ----------

def footer(t):
    W, H = 1280, 170
    items = ["Open for freelance work", "Systems", "APIs", "Web and mobile apps", "ferashamdouna.vercel.app"]
    size, gap = 40, 26
    parts, stars, x = [], [], 0.0
    for it in items:
        d, w = text_path(it.upper(), size, tracking=0.4)
        parts.append(f'<path transform="translate({x:.1f},0)" d="{d}"/>')
        x += w + gap
        stars.append(star(x, -size * CAP / 2, 9))
        x += gap
    seq_w = x
    copies = int((W + 600) // seq_w) + 2
    uses = "".join(f'<use href="#fs" x="{i * seq_w:.1f}"/>' for i in range(copies))
    dur = seq_w / 50
    cy, hgt, ang = 88, 68, -2.2
    style = f"""
    @keyframes fmove {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-{seq_w:.1f}px); }} }}
    #ftrack {{ animation: fmove {dur:.1f}s linear infinite; }}
    @keyframes bmove {{ from {{ transform: translateX(-{seq_w:.1f}px); }} to {{ transform: translateX(0); }} }}
    #btrack {{ animation: bmove {dur * 1.6:.1f}s linear infinite; }}"""
    body = f"""  <defs><g id="fs"><g fill="{t['on_ink']}">{''.join(parts)}</g><path fill="{t['blue']}" d="{' '.join(stars)}"/></g>
    <g id="bs"><g fill="#FFFFFF">{''.join(parts)}</g><path fill="#FFFFFF" d="{' '.join(stars)}"/></g>
    <clipPath id="fc"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22"/></clipPath></defs>
  <g clip-path="url(#fc)">
    <g transform="rotate(2.6 {W / 2} {cy + 6}) skewX(-5)">
      <rect x="-300" y="{cy + 6 - 24}" width="{W + 600}" height="48" fill="{t['blue']}"/>
      <g transform="translate(-300,{cy + 6 + 14}) scale(.62)"><g id="btrack">{uses.replace('#fs', '#bs')}</g></g>
    </g>
    <g transform="rotate({ang} {W / 2} {cy}) skewX({-ang * 2.2:.2f})">
      <rect x="-300" y="{cy - hgt / 2 + 7}" width="{W + 600}" height="{hgt}" fill="{t['edge']}"/>
      <rect x="-300" y="{cy - hgt / 2}" width="{W + 600}" height="{hgt}" fill="{t['ink']}"/>
      <g transform="translate(-300,{cy + size * CAP / 2:.1f})"><g id="ftrack">{uses}</g></g>
    </g>
  </g>"""
    return svg(W, H, "Open for freelance work", "Open for freelance work: systems, APIs, web and mobile apps. ferashamdouna.vercel.app", style, body, t)


BUILDERS = {"project-gazagate": gazagate, "project-dafter": dafter, "project-rivera": rivera, "stack": stack, "footer": footer}
for name, fn in BUILDERS.items():
    for th, t in THEMES.items():
        with open(f"{OUT}/{name}-{th}.svg", "w", encoding="utf-8") as fh:
            fh.write(fn(t))
print("ok")
