"""Creator Kit: turn guide files (guides/*.json) into branded, phone-first pages (dist/).

    python build.py                 # build every guide with the default theme
    python build.py --theme themes/human-edge.json

No dependencies (Python standard library only). Each guide becomes dist/<slug>/index.html,
plus dist/index.html listing all guides. The dist/ folder is a plain static site: put it on
GitHub Pages (or any free static host) and share dist/<slug>/ links in DMs.
Content lives in guides/*.json and the look in themes/*.json, so nobody has to touch code.
"""
from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def e(text) -> str:
    return html.escape(str(text or ""), quote=True)


def font_link(theme) -> str:
    fams = [theme["fonts"]["display"], theme["fonts"]["body"] + ":wght@400;600;800", theme["fonts"]["mono"]]
    q = "&".join("family=" + quote(f).replace("%3A", ":").replace("%3B", ";").replace("%40", "@") for f in fams)
    return f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?{q}&display=swap">'


def css(theme) -> str:
    c, f = theme["colors"], theme["fonts"]
    return f"""
:root{{--paper:{c['paper']};--card:{c['card']};--ink:{c['ink']};--soft:{c['soft']};--line:{c['line']};
--accent:{c['accent']};--accent-ink:{c['accent_ink']};--shadow:{c['shadow']};}}
*{{box-sizing:border-box}} html,body{{margin:0;background:var(--paper);color:var(--ink)}}
body{{font-family:'{f['body']}',system-ui,sans-serif;font-size:17px;line-height:1.5;
background-image:radial-gradient(rgba(0,0,0,.035) 1.2px,transparent 1.3px);background-size:24px 24px}}
.wrap{{max-width:620px;margin:0 auto;padding:22px 16px 48px}}
.top{{display:flex;align-items:center;gap:12px;font-weight:800;font-size:14px;color:var(--soft)}}
.top a{{color:var(--ink);text-decoration:none}}
.hero{{display:flex;align-items:flex-end;gap:14px;margin:18px 0 6px}}
.hero img{{width:84px;height:auto;image-rendering:pixelated;flex:none}}
h1{{font-family:'{f['display']}',sans-serif;font-weight:400;font-size:clamp(30px,8.5vw,44px);line-height:1.05;margin:0;
text-shadow:3px 3px 0 var(--shadow);letter-spacing:.2px}}
.reel{{display:inline-block;margin:10px 0 0;background:var(--accent);color:var(--accent-ink);font-weight:800;font-size:13px;
padding:4px 12px;border-radius:999px}}
.intro{{color:var(--soft);margin:14px 0 4px}}
h2{{font-family:'{f['display']}',sans-serif;font-weight:400;font-size:22px;margin:30px 0 12px}}
.card{{background:var(--card);border:2.5px solid var(--line);border-radius:16px;padding:16px;margin:0 0 16px;
box-shadow:6px 6px 0 var(--ink)}}
.card h3{{margin:0 0 4px;font-size:21px;font-weight:800}}
.card p{{margin:0 0 12px}}
.tags{{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 12px}}
.tag{{font-size:12px;font-weight:800;border:1.5px solid var(--line);border-radius:999px;padding:1px 9px}}
.copy{{margin:0 0 10px}}
.copy .label{{font-size:13px;color:var(--soft);font-weight:600;margin-bottom:4px}}
.row{{display:flex;gap:8px;align-items:stretch}}
code{{flex:1;min-width:0;font-family:'{f['mono']}',monospace;font-size:14px;background:#151515;color:#F1EDE4;
border-radius:10px;padding:10px 12px;white-space:pre-wrap;word-break:break-all}}
button.cp{{flex:none;font:800 14px '{f['body']}',sans-serif;border:2px solid var(--line);background:var(--paper);
border-radius:10px;padding:0 14px;cursor:pointer;color:var(--ink)}}
button.cp.ok{{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}}
a.open{{display:inline-flex;align-items:center;gap:6px;font-weight:800;color:var(--accent-ink);background:var(--accent);
text-decoration:none;border-radius:10px;padding:9px 14px;margin-top:4px}}
.steps{{counter-reset:s;list-style:none;padding:0;margin:0}}
.steps li{{counter-increment:s;position:relative;padding:0 0 0 44px;margin:0 0 14px}}
.steps li::before{{content:counter(s);position:absolute;left:0;top:-2px;width:32px;height:32px;border-radius:50%;
background:var(--ink);color:var(--paper);font-weight:800;display:flex;align-items:center;justify-content:center}}
.note{{font-family:'{f['display']}',sans-serif;font-size:20px;text-align:center;margin:30px 0 8px}}
.src{{font-size:13px;color:var(--soft);border-top:1.5px dashed var(--shadow);margin-top:26px;padding-top:12px}}
.src a{{color:var(--soft)}}
.follow{{display:block;text-align:center;margin:22px 0 0;font-weight:800;color:var(--ink)}}
.foot{{text-align:center;font-size:12px;color:var(--soft);margin-top:18px}}
.list a{{display:block;background:var(--card);border:2.5px solid var(--line);border-radius:14px;padding:14px 16px;margin:0 0 12px;
color:var(--ink);text-decoration:none;font-weight:800;box-shadow:4px 4px 0 var(--ink)}}
.meta{{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:12px 0 0}}
.upd{{font-size:13px;font-weight:800;color:var(--soft);border:1.5px dashed var(--shadow);border-radius:999px;padding:3px 11px}}
.bar{{display:flex;gap:10px;margin:18px 0 6px}}
.bar button{{flex:1;font:800 15px '{f['body']}',sans-serif;border:2.5px solid var(--line);border-radius:12px;padding:12px 10px;
cursor:pointer;box-shadow:4px 4px 0 var(--ink);background:var(--card);color:var(--ink)}}
.bar button.main{{background:var(--accent);color:var(--accent-ink)}}
.bar button.ok{{background:var(--ink);color:var(--paper)}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.grid a{{display:block;background:var(--card);border:2.5px solid var(--line);border-radius:16px;overflow:hidden;color:var(--ink);
text-decoration:none;box-shadow:4px 4px 0 var(--ink)}}
.grid img{{display:block;width:100%;aspect-ratio:9/12;object-fit:cover;object-position:top;background:var(--shadow)}}
.grid .ph{{aspect-ratio:9/12;display:flex;align-items:center;justify-content:center;background:var(--shadow);
font-family:'{f['display']}',sans-serif;font-size:18px;line-height:1.15;padding:14px;text-align:center;overflow-wrap:anywhere}}
.grid span{{display:block;padding:10px 12px 12px;font-weight:800;font-size:15px;line-height:1.25}}
"""


JS = """<script>
document.querySelectorAll('button.cp').forEach(b=>b.addEventListener('click',async()=>{
  const t=b.previousElementSibling.textContent;
  try{await navigator.clipboard.writeText(t);}catch(_){const r=document.createRange();r.selectNodeContents(b.previousElementSibling);
    const s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('copy');s.removeAllRanges();}
  b.textContent='Copied';b.classList.add('ok');setTimeout(()=>{b.textContent='Copy';b.classList.remove('ok')},1600);
}));
async function put(t){try{await navigator.clipboard.writeText(t);return true}catch(_){const a=document.createElement('textarea');
  a.value=t;document.body.appendChild(a);a.select();const ok=document.execCommand('copy');a.remove();return ok}}
function flash(b,txt){const o=b.textContent;b.textContent=txt;b.classList.add('ok');setTimeout(()=>{b.textContent=o;b.classList.remove('ok')},1700)}
const all=document.getElementById('copyall');
if(all)all.addEventListener('click',async()=>{
  const lines=[...document.querySelectorAll('.card')].map(c=>{const n=c.querySelector('h3')?.textContent||'';
    const l=c.querySelector('a.open')?.href||'';const k=[...c.querySelectorAll('code')].map(x=>x.textContent);
    return [n,l,...k].filter(Boolean).join('\\n')}).filter(Boolean);
  if(await put(document.title.split(' | ')[0]+'\\n\\n'+lines.join('\\n\\n')+'\\n\\n'+location.href))flash(all,'Copied all');});
const sh=document.getElementById('share');
if(sh)sh.addEventListener('click',async()=>{const d={title:document.title,url:location.href};
  if(navigator.share){try{await navigator.share(d);return}catch(_){return}}
  if(await put(location.href))flash(sh,'Link copied');});
</script>"""


def tool_card(t) -> str:
    tags = "".join(f'<span class="tag">{e(x)}</span>' for x in t.get("tags", []))
    copies = "".join(
        f'<div class="copy"><div class="label">{e(c["label"])}</div>'
        f'<div class="row"><code>{e(c["text"])}</code><button class="cp" type="button">Copy</button></div></div>'
        for c in t.get("copy", [])
    )
    link = f'<a class="open" href="{e(t["link"])}" target="_blank" rel="noopener">Open {e(t["name"])} &rarr;</a>' if t.get("link") else ""
    return (f'<div class="card"><h3>{e(t["name"])}</h3><p>{e(t.get("what"))}</p>'
            f'{f"<div class=tags>{tags}</div>" if tags else ""}{copies}{link}</div>')


def section(s) -> str:
    out = f'<h2>{e(s.get("heading"))}</h2>' if s.get("heading") else ""
    if s.get("steps"):
        out += '<ol class="steps">' + "".join(f"<li>{e(x)}</li>" for x in s["steps"]) + "</ol>"
    out += "".join(tool_card(t) for t in s.get("tools", []))
    return out


def nice_date(iso: str) -> str:
    """2026-11-17 -> 17 Nov 2026"""
    from datetime import date
    try:
        return date.fromisoformat(iso).strftime("%d %b %Y").lstrip("0")
    except ValueError:
        return iso


def has_links(guide) -> bool:
    return any(t.get("link") or t.get("copy") for s in guide.get("sections", []) for t in s.get("tools", []))


def page(guide, theme, depth: int) -> str:
    up = "../" * depth
    sources = "".join(
        f'<div>{e(s)}</div>' if not str(s).startswith("http") else f'<div><a href="{e(s)}">{e(s)}</a></div>'
        for s in guide.get("sources", []))
    body = "".join(section(s) for s in guide.get("sections", []))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(guide['title'])} | {e(theme['brand'])}</title>
<meta name="description" content="{e(guide.get('intro'))}">
<meta property="og:title" content="{e(guide['title'])}"><meta property="og:description" content="{e(guide.get('intro'))}">
{font_link(theme)}<style>{css(theme)}</style></head><body><div class="wrap">
<div class="top"><a href="{up}">{e(theme['brand'])}</a><span>&middot;</span><span>{e(theme['handle'])}</span></div>
<div class="hero"><img src="{up}{e(theme['mascot'])}" alt=""><h1>{e(guide['title'])}</h1></div>
<div class="meta">{f'<span class="reel" style="margin:0">{e(guide["reel"])}</span>' if guide.get("reel") else ""}
{f'<span class="upd">Updated {e(nice_date(guide["updated"]))}</span>' if guide.get("updated") else ""}</div>
<p class="intro">{e(guide.get('intro'))}</p>
<div class="bar">{'<button id="copyall" class="main" type="button">Copy all links</button>' if has_links(guide) else ''}<button id="share" type="button">Share this list</button></div>
{body}
{f'<div class="note">{e(guide["note"])}</div>' if guide.get("note") else ""}
<a class="follow" href="{e(theme['profile_url'])}">Follow {e(theme['handle'])} for more &rarr;</a>
<div class="src">Sources{(' &middot; updated ' + e(guide['updated'])) if guide.get('updated') else ''}{sources}</div>
<div class="foot">{e(theme['footer'])}</div>
</div>{JS}</body></html>"""


def index(guides, theme) -> str:
    def tile(g):
        pic = f'<img src="{e(g["cover"])}" alt="" loading="lazy">' if g.get("cover") else f'<div class="ph">{e(g["title"])}</div>'
        return f'<a href="{e(g["slug"])}/">{pic}<span>{e(g["title"])}</span></a>'
    newest = sorted(guides, key=lambda g: g.get("updated", ""), reverse=True)
    items = "".join(tile(g) for g in newest)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Guides | {e(theme['brand'])}</title>
{font_link(theme)}<style>{css(theme)}</style></head><body><div class="wrap">
<div class="hero"><img src="{e(theme['mascot'])}" alt=""><h1>{e(theme['brand'])} guides</h1></div>
<p class="intro">Every link and command from the reels, in one place. Newest first.</p><div class="grid">{items}</div>
<a class="follow" href="{e(theme['profile_url'])}">Follow {e(theme['handle'])} &rarr;</a>
<div class="foot">{e(theme['footer'])}</div></div></body></html>"""


def main() -> int:
    theme_path = ROOT / "themes" / "human-edge.json"
    if "--theme" in sys.argv:
        theme_path = Path(sys.argv[sys.argv.index("--theme") + 1])
    theme = json.loads(theme_path.read_text(encoding="utf-8"))
    guides = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "guides").glob("*.json"))]
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "assets", DIST / "assets")        # includes assets/covers/
    for g in guides:
        out = DIST / g["slug"] / "index.html"
        out.parent.mkdir(parents=True)
        out.write_text(page(g, theme, depth=1), encoding="utf-8")
        print("built", out.relative_to(ROOT))
    (DIST / "index.html").write_text(index(guides, theme), encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print("built dist/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
