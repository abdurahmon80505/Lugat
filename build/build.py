#!/usr/bin/env python3
"""index.html ni yasaydi: bitta fayl, tashqi bog'liqliksiz, to'liq offline."""
import base64
import glob as _glob
import html
import io
import os
import re
import sys

from art import scene_svg
from parse import parse, verify

# Ixtiyoriy: images/<raqam>.jpg bo'lsa, o'sha rasm 800px / JPEG 75% qilib
# base64 holda HTML ichiga joylashtiriladi. Rasm bo'lmasa - ichki SVG manzara.
IMG_DIR = os.environ.get('ZIYORAT_IMG_DIR', 'images')


def embedded_image(num, alt):
    """images/<num>.* -> 800px, JPEG 75%, base64 data URI."""
    hits = [f for e in ('jpg', 'jpeg', 'png', 'webp')
            for f in _glob.glob(os.path.join(IMG_DIR, f'{num}.{e}'))]
    if not hits:
        return None
    try:
        from PIL import Image
    except ImportError:
        print(f'  ! Pillow yo\'q, {hits[0]} o\'tkazib yuborildi')
        return None
    im = Image.open(hits[0])
    im = im.convert('RGB')
    if im.width > 800:
        im = im.resize((800, round(im.height * 800 / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=75, optimize=True, progressive=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    print(f'  + {num}: {os.path.basename(hits[0])} -> {len(b64)//1024} KB base64')
    return (f'<img class="art" src="data:image/jpeg;base64,{b64}" alt="{e(alt)}"'
            f' loading="lazy" decoding="async" width="800"'
            f' height="{im.height}">')

MD = sys.argv[1] if len(sys.argv) > 1 else 'ziyorat-kartalari.md'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'index.html'

CITY_LABEL = {'madina': 'Madina', 'makka': 'Makka'}


def e(s):
    return html.escape(s, quote=True)


def strong(s):
    """Markdown **qalin** -> <strong>. Matnning o'zi o'zgarmaydi."""
    out, last = [], 0
    for m in re.finditer(r'\*\*(.+?)\*\*', s):
        out.append(e(s[last:m.start()]))
        out.append('<strong>' + e(m.group(1)) + '</strong>')
        last = m.end()
    out.append(e(s[last:]))
    return ''.join(out)


def norm(s):
    """Qidiruv uchun normallashtirish (JS'dagi norm() bilan bir xil)."""
    s = s.lower()
    for ch in 'ʻʼ‘’‛`´\'':
        s = s.replace(ch, '')
    return ' '.join(''.join(c if c.isalnum() else ' ' for c in s).split())


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
:root{
  color-scheme:dark only;
  --bg:#070a0f; --bg2:#0b1017;
  --card:#111823; --card2:#0d131c;
  --line:#1e2836; --line2:#2b3849;
  --tx:#e9edf4; --tx2:#aeb9c9; --tx3:#7d8899;
  --madina:#6ec49b; --makka:#d7a44b;
  --acc:var(--makka);
  --r:18px;
  --tap:56px;
}
html,body{background:var(--bg)}
body{
  margin:0; color:var(--tx);
  /* faqat tizim shriftlari - hech narsa yuklanmaydi.
     Oxirdagi arabcha shriftlar "ﷺ" belgisi uchun zaxira. */
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,
              "Noto Naskh Arabic","Noto Sans Arabic",sans-serif;
  font-size:17px; line-height:1.6;
  -webkit-font-smoothing:antialiased;
  overflow-x:hidden;
  padding-bottom:calc(40px + env(safe-area-inset-bottom));
}
body::before{ /* yumshoq tungi yorug'lik */
  content:""; position:fixed; inset:0 0 auto 0; height:340px; z-index:-1;
  background:radial-gradient(120% 100% at 50% 0,rgba(120,150,210,.10),transparent 70%);
  pointer-events:none;
}
:focus-visible{outline:2px solid var(--acc); outline-offset:3px; border-radius:8px}

/* ---------- yuqori panel ---------- */
.top{
  position:sticky; top:0; z-index:20;
  background:rgba(7,10,15,.94);
  -webkit-backdrop-filter:blur(14px); backdrop-filter:blur(14px);
  border-bottom:1px solid var(--line);
  padding:calc(12px + env(safe-area-inset-top)) 14px 10px;
}
.brand{display:flex; align-items:baseline; gap:9px; margin:0 2px 11px}
.brand h1{
  margin:0; font-size:1.06rem; font-weight:650; letter-spacing:.2px;
  color:var(--tx);
}
.brand span{font-size:.8rem; color:var(--tx3); font-variant-numeric:tabular-nums}

.sbox{position:relative; display:flex; align-items:center}
.sbox svg{
  position:absolute; left:15px; width:20px; height:20px;
  fill:none; stroke:var(--tx3); stroke-width:2; pointer-events:none;
}
#q{
  width:100%; height:52px;
  padding:0 50px 0 46px;
  background:var(--card); color:var(--tx);
  border:1px solid var(--line2); border-radius:14px;
  font:inherit; font-size:1rem;
}
#q::placeholder{color:var(--tx3)}
#q:focus{border-color:var(--acc); outline:none; box-shadow:0 0 0 3px rgba(215,164,75,.15)}
#clr{
  position:absolute; right:6px;
  width:44px; height:44px; display:none; place-items:center;
  background:none; border:0; border-radius:11px;
  color:var(--tx2); font-size:1.35rem; line-height:1; cursor:pointer;
}
#clr.on{display:grid}
#clr:active{background:var(--line)}

.filters{display:flex; gap:8px; margin-top:10px}
.filters button{
  flex:1; min-height:48px;
  display:flex; align-items:center; justify-content:center; gap:7px;
  background:var(--card); color:var(--tx2);
  border:1px solid var(--line2); border-radius:13px;
  font:inherit; font-size:.95rem; font-weight:550; cursor:pointer;
  -webkit-tap-highlight-color:transparent;
  transition:background .15s,border-color .15s,color .15s;
}
.filters button .n{
  font-size:.76rem; color:var(--tx3); font-variant-numeric:tabular-nums;
  background:rgba(255,255,255,.05); padding:2px 7px; border-radius:20px;
}
.filters button:active{background:var(--line)}
.filters button[aria-pressed=true]{color:#080c10; font-weight:650}
.filters button[data-city=all][aria-pressed=true]{background:#c3ccdb; border-color:#c3ccdb}
.filters button[data-city=madina][aria-pressed=true]{background:var(--madina); border-color:var(--madina)}
.filters button[data-city=makka][aria-pressed=true]{background:var(--makka); border-color:var(--makka)}
.filters button[aria-pressed=true] .n{background:rgba(0,0,0,.17); color:rgba(0,0,0,.6)}

/* ---------- ro'yxat ---------- */
main{padding:16px 12px 0; max-width:760px; margin:0 auto}
.card{
  --acc:var(--makka);
  background:linear-gradient(180deg,var(--card),var(--card2));
  border:1px solid var(--line); border-radius:var(--r);
  margin-bottom:12px; overflow:hidden;
}
.card[data-city=madina]{--acc:var(--madina)}
.card.open{border-color:var(--line2)}
.card.hide{display:none}

.head{
  width:100%; min-height:var(--tap);
  display:flex; align-items:center; gap:13px;
  padding:15px 14px; margin:0;
  background:none; border:0; color:inherit;
  font:inherit; text-align:left; cursor:pointer;
  -webkit-tap-highlight-color:transparent;
}
.head:active{background:rgba(255,255,255,.035)}
.num{
  flex:none; width:40px; height:40px; border-radius:12px;
  display:grid; place-items:center;
  background:color-mix(in srgb,var(--acc) 15%,transparent);
  border:1px solid color-mix(in srgb,var(--acc) 40%,transparent);
  color:var(--acc); font-size:1rem; font-weight:680;
  font-variant-numeric:tabular-nums;
}
.ttl{flex:1; min-width:0}
.city{
  display:block; font-size:.68rem; font-weight:670; letter-spacing:.9px;
  text-transform:uppercase; color:var(--acc); opacity:.85; margin-bottom:2px;
}
.name{display:block; font-size:1.06rem; font-weight:600; line-height:1.34; color:var(--tx)}
.ar{
  display:block; margin-top:3px; font-size:.95rem; color:var(--tx3);
  font-family:"Noto Naskh Arabic","Traditional Arabic",serif; direction:rtl;
}
.chev{
  flex:none; width:26px; height:26px; color:var(--tx3);
  transition:transform .28s ease, color .2s;
}
.card.open .chev{transform:rotate(180deg); color:var(--acc)}

/* accordion: yopiq turadi */
.panel{display:grid; grid-template-rows:0fr; transition:grid-template-rows .3s ease}
.card.open .panel{grid-template-rows:1fr}
.panel>.in{overflow:hidden; min-height:0}

.art{display:block; width:100%; height:auto; aspect-ratio:800/260; background:#070b14}
img.art{object-fit:cover; filter:brightness(.82) saturate(.9)}  /* tungi rejimga moslash */
.artwrap{position:relative; border-block:1px solid var(--line)}
.artwrap::after{
  content:""; position:absolute; inset:auto 0 0 0; height:52%;
  background:linear-gradient(180deg,transparent,var(--card));
  pointer-events:none;
}
.body{padding:16px 16px 18px}
.body p{margin:0 0 15px; font-size:1.0625rem; line-height:1.78; color:var(--tx2)}
.body p:last-of-type{margin-bottom:0}

.note{
  margin-top:16px; padding:14px 15px;
  border-radius:13px; border:1px solid var(--line2);
  background:rgba(255,255,255,.022);
  font-size:1.0625rem; line-height:1.72; color:var(--tx2);
}
.note.esla{
  border-color:color-mix(in srgb,var(--acc) 34%,transparent);
  background:color-mix(in srgb,var(--acc) 8%,transparent);
  color:var(--tx);
}
.note b{display:block; margin-bottom:5px; font-size:.74rem; font-weight:700;
  letter-spacing:1.1px; text-transform:uppercase; color:var(--acc)}
.note.amaliy b{color:var(--tx3)}

.maps{
  display:flex; align-items:center; justify-content:center; gap:10px;
  min-height:54px; margin-top:17px; padding:0 18px;
  background:color-mix(in srgb,var(--acc) 13%,transparent);
  border:1px solid color-mix(in srgb,var(--acc) 45%,transparent);
  border-radius:14px;
  color:var(--acc); font-size:1rem; font-weight:620; text-decoration:none;
  -webkit-tap-highlight-color:transparent;
}
.maps:active{background:color-mix(in srgb,var(--acc) 24%,transparent)}
.maps svg{width:20px; height:20px; flex:none}
.coord{
  margin-top:10px; text-align:center;
  font-size:.83rem; color:var(--tx3); font-variant-numeric:tabular-nums;
}
.coord i{font-style:normal; opacity:.8}

#empty{display:none; padding:52px 20px; text-align:center; color:var(--tx3)}
#empty.on{display:block}
#empty b{display:block; margin-bottom:6px; color:var(--tx2); font-size:1.05rem}

.usage{
  max-width:760px; margin:22px auto 0; padding:20px 16px 26px;
  border-top:1px solid var(--line);
}
.usage h2{
  margin:0 0 13px; font-size:.76rem; font-weight:700;
  letter-spacing:1.4px; text-transform:uppercase; color:var(--tx3);
}
.usage p{margin:0 0 13px; font-size:1.0625rem; line-height:1.78; color:var(--tx2)}
.usage p:last-child{margin-bottom:0}
.usage strong{color:var(--tx); font-weight:670}

@media (min-width:620px){
  .brand h1{font-size:1.18rem}
  .name{font-size:1.12rem}
  main{padding-inline:16px}
}
@media (prefers-reduced-motion:reduce){
  *{transition:none !important; animation:none !important}
}
"""

JS = r"""
(function(){
  var q=document.getElementById('q'), clr=document.getElementById('clr'),
      empty=document.getElementById('empty'), shown=document.getElementById('shown'),
      cards=[].slice.call(document.querySelectorAll('.card')),
      btns=[].slice.call(document.querySelectorAll('.filters button')),
      city='all';

  function norm(s){
    s=s.toLowerCase().replace(/[ʻʼ‘’‛`´']/g,'');
    return s.replace(/[^\p{L}\p{N}]+/gu,' ').trim();
  }

  function apply(){
    var t=norm(q.value), terms=t?t.split(' '):[], n=0;
    cards.forEach(function(c){
      var ok=(city==='all'||c.dataset.city===city);
      if(ok&&terms.length){
        var h=c.dataset.s;
        for(var i=0;i<terms.length;i++){ if(h.indexOf(terms[i])<0){ok=false;break;} }
      }
      c.classList.toggle('hide',!ok);
      if(ok){n++;} else if(c.classList.contains('open')){ close(c); }
    });
    shown.textContent=n;
    empty.classList.toggle('on',n===0);
    clr.classList.toggle('on',q.value.length>0);
  }

  function close(c){
    c.classList.remove('open');
    c.querySelector('.head').setAttribute('aria-expanded','false');
  }

  cards.forEach(function(c){
    c.querySelector('.head').addEventListener('click',function(){
      var open=!c.classList.contains('open');
      c.classList.toggle('open',open);
      this.setAttribute('aria-expanded',open?'true':'false');
      if(open){
        var y=c.getBoundingClientRect().top, top=document.querySelector('.top').offsetHeight;
        if(y<top) window.scrollBy({top:y-top-8,behavior:'smooth'});
      }
    });
  });

  btns.forEach(function(b){
    b.addEventListener('click',function(){
      city=b.dataset.city;
      btns.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});
      apply();
    });
  });

  q.addEventListener('input',apply);
  q.addEventListener('keydown',function(ev){ if(ev.key==='Enter') q.blur(); });
  clr.addEventListener('click',function(){ q.value=''; apply(); q.focus(); });
  apply();
})();
"""

ICON_SEARCH = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/>'
               '<path d="M20 20l-3.6-3.6" stroke-linecap="round"/></svg>')
ICON_CHEV = ('<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
             ' stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
             ' aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>')
ICON_PIN = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"'
            ' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 1 1 16 0z"/>'
            '<circle cx="12" cy="10" r="3"/></svg>')


def card_html(c):
    num, city = c['num'], c['city']
    parts = [f'<span class="name">{e(c["title"])}</span>']
    if c['arabic']:
        parts.append(f'<span class="ar" dir="rtl" lang="ar">{e(c["arabic"])}</span>')

    hay = ' '.join(filter(None, [
        c['title'], c['arabic'], CITY_LABEL[city], str(num),
        ' '.join(c['body']), c['remember'], c['practical'], c['coordNote'],
        c['lat'], c['lng'],
    ]))

    body = ''.join(f'<p>{e(p)}</p>' for p in c['body'])
    body += (f'<div class="note esla"><b>Turganingda esla</b>{e(c["remember"])}</div>')
    if c['practical']:
        body += f'<div class="note amaliy"><b>Amaliy</b>{e(c["practical"])}</div>'

    maps = f'https://www.google.com/maps/search/?api=1&query={c["lat"]},{c["lng"]}'
    body += (f'<a class="maps" href="{e(maps)}" target="_blank" rel="noopener noreferrer">'
             f'{ICON_PIN}<span>Google Maps’da ochish</span></a>')
    coord = f'{c["lat"]}, {c["lng"]}'
    if c['coordNote']:
        coord += f' <i>({e(c["coordNote"])})</i>'
    body += f'<div class="coord">{coord}</div>'

    return (
        f'<article class="card" data-city="{city}" data-s="{e(norm(hay))}">'
        f'<h2 style="margin:0;font:inherit">'
        f'<button class="head" type="button" aria-expanded="false" aria-controls="p{num}">'
        f'<span class="num">{num}</span>'
        f'<span class="ttl"><span class="city">{CITY_LABEL[city]}</span>{"".join(parts)}</span>'
        f'{ICON_CHEV}</button></h2>'
        f'<div class="panel" id="p{num}" role="region"><div class="in">'
        f'<div class="artwrap">{embedded_image(num, c["title"]) or scene_svg(num, city)}</div>'
        f'<div class="body">{body}</div>'
        f'</div></div></article>'
    )


def main():
    data = parse(MD)
    verify(data, MD)
    cards = data['cards']
    n_mad = sum(1 for c in cards if c['city'] == 'madina')
    n_mak = sum(1 for c in cards if c['city'] == 'makka')
    title = data['docTitle']

    usage = ''.join(f'<p>{strong(u)}</p>' for u in data['usage'])

    doc = f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#070a0f">
<meta name="description" content="{e(title)} - offline ziyorat kartalari">
<title>{e(title)}</title>
<style>{CSS}</style>
</head>
<body>
<header class="top">
  <div class="brand"><h1>{e(title)}</h1><span><b id="shown">{len(cards)}</b>/{len(cards)}</span></div>
  <div class="sbox">
    {ICON_SEARCH}
    <input id="q" type="search" inputmode="search" autocomplete="off" autocapitalize="off"
           spellcheck="false" placeholder="Qidiruv: joy, voqea, ism…"
           aria-label="Kartalar ichidan qidirish">
    <button id="clr" type="button" aria-label="Qidiruvni tozalash">&times;</button>
  </div>
  <div class="filters" role="group" aria-label="Shahar bo'yicha filtr">
    <button type="button" data-city="all" aria-pressed="true">Hammasi <span class="n">{len(cards)}</span></button>
    <button type="button" data-city="madina" aria-pressed="false">Madina <span class="n">{n_mad}</span></button>
    <button type="button" data-city="makka" aria-pressed="false">Makka <span class="n">{n_mak}</span></button>
  </div>
</header>

<main>
{''.join(card_html(c) for c in cards)}
<div id="empty"><b>Hech narsa topilmadi</b>Boshqa so'z bilan qidirib ko'r.</div>
</main>

<section class="usage">
  <h2>Ishlatish tartibi</h2>
  {usage}
</section>

<script>{JS}</script>
</body>
</html>
"""
    open(OUT, 'w', encoding='utf-8').write(doc)
    print(f'{OUT} yozildi: {len(cards)} karta, {len(doc.encode()):,} bayt')


if __name__ == '__main__':
    main()
