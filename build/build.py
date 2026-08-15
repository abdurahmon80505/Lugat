#!/usr/bin/env python3
"""index.html ni yasaydi: bitta fayl, tashqi bog'liqliksiz, to'liq offline.

- Yozuv: kirill (asosiy) / lotin - tepadagi tugma bilan almashadi
- Mavzu: telefondagi tun/kun rejimiga ergashadi + qo'lda almashtirish
- Filtr: Madina (birinchi, asosiy) / Makka
"""
import base64
import glob as _glob
import html
import io
import os
import re
import sys

from art import scene_svg
from parse import parse, verify
from translit import to_cyrillic

MD = sys.argv[1] if len(sys.argv) > 1 else 'ziyorat-kartalari.md'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'index.html'

CITY = {'madina': 'Madina', 'makka': 'Makka'}

# Ixtiyoriy: images/<raqam>.jpg bo'lsa, o'sha rasm 800px / JPEG 75% qilib
# base64 holda HTML ichiga joylashtiriladi. Rasm bo'lmasa - ichki SVG manzara.
IMG_DIR = os.environ.get('ZIYORAT_IMG_DIR', 'images')


def e(s):
    return html.escape(s, quote=True)


def T(latin, tag='span', cls=''):
    """Ikki yozuvli matn: ko'rinadigani kirill, lotini data-l da turadi."""
    c = f' class="t {cls}"'.replace('  ', ' ') if cls else ' class="t"'
    return f'<{tag}{c} data-l="{e(latin)}">{e(to_cyrillic(latin))}</{tag}>'


def T_rich(s):
    """**qalin** bo'lakli matn - har bo'lak alohida almashadi."""
    out, last = [], 0
    for m in re.finditer(r'\*\*(.+?)\*\*', s):
        if s[last:m.start()]:
            out.append(T(s[last:m.start()]))
        out.append(T(m.group(1), 'strong'))
        last = m.end()
    if s[last:]:
        out.append(T(s[last:]))
    return ''.join(out)


def norm(s):
    """Qidiruv uchun normallashtirish (JS'dagi norm() bilan bir xil)."""
    s = s.lower()
    for ch in 'ʻʼ‘’‛`´\'ъьЪЬ':
        s = s.replace(ch, '')
    return ' '.join(''.join(c if c.isalnum() else ' ' for c in s).split())


def embedded_image(num, alt):
    """images/<num>.* -> 800px, JPEG 75%, base64 data URI."""
    hits = [f for x in ('jpg', 'jpeg', 'png', 'webp')
            for f in _glob.glob(os.path.join(IMG_DIR, f'{num}.{x}'))]
    if not hits:
        return None
    try:
        from PIL import Image
    except ImportError:
        print(f'  ! Pillow yo\'q, {hits[0]} o\'tkazib yuborildi')
        return None
    im = Image.open(hits[0]).convert('RGB')
    if im.width > 800:
        im = im.resize((800, round(im.height * 800 / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=75, optimize=True, progressive=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    print(f'  + {num}: {os.path.basename(hits[0])} -> {len(b64)//1024} KB base64')
    return (f'<img class="art" src="data:image/jpeg;base64,{b64}" alt="{e(alt)}"'
            f' loading="lazy" decoding="async" width="800" height="{im.height}">')


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%; font-size:19px}  /* katta matn: rem shu yerdan */

/* ---------- kunduzgi (asosiy) ---------- */
:root{
  color-scheme:light dark;
  --bg:#f6f4ee; --card:#fffefb; --card2:#faf8f3;
  --line:#e4e0d5; --line2:#d2cdbe;
  --tx:#191d24; --tx2:#3c4552; --tx3:#6f7885;
  --madina:#15734c; --makka:#8a5a0d;
  --seg:#eceae2; --shadow:0 1px 2px rgba(30,25,10,.05);
  --acc:var(--makka); --r:18px;
  /* Matn o'lchami: --k hamma narsani mutanosib kichraytiradi,
     --sh esa quti balandligini biroz pasaytiradi (46px dan pastga tushmaydi). */
  --k:1; --sh:0px;             /* Katta - asosiysi */
  --fs:calc(1.1rem * var(--k));
}
:root[data-size=m]{--k:.909; --sh:2px}   /* O'rta */
:root[data-size=s]{--k:.818; --sh:4px}   /* Kichik */
/* ---------- tungi: telefon sozlamasiga ergashadi ---------- */
@media (prefers-color-scheme:dark){
  :root:not([data-theme=light]){
    --bg:#070a0f; --card:#111823; --card2:#0d131c;
    --line:#1e2836; --line2:#2b3849;
    --tx:#e9edf4; --tx2:#b3bdcb; --tx3:#7d8899;
    --madina:#6ec49b; --makka:#d7a44b;
    --seg:#0c121b; --shadow:none;
  }
}
/* ---------- qo'lda tanlangan tungi ---------- */
:root[data-theme=dark]{
  --bg:#070a0f; --card:#111823; --card2:#0d131c;
  --line:#1e2836; --line2:#2b3849;
  --tx:#e9edf4; --tx2:#b3bdcb; --tx3:#7d8899;
  --madina:#6ec49b; --makka:#d7a44b;
  --seg:#0c121b; --shadow:none;
}

html,body{background:var(--bg)}
body{
  margin:0; color:var(--tx);
  /* faqat tizim shriftlari - hech narsa yuklanmaydi.
     Oxirdagi arabcha shriftlar "ﷺ" belgisi uchun zaxira. */
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans",
              "Helvetica Neue",Arial,"Noto Naskh Arabic","Noto Sans Arabic",sans-serif;
  font-size:1rem; line-height:1.6;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  overflow-x:hidden;
  padding-bottom:calc(40px + env(safe-area-inset-bottom));
}
:focus-visible{outline:2px solid var(--acc); outline-offset:3px; border-radius:8px}

/* ---------- yuqori panel ---------- */
.top{
  position:sticky; top:0; z-index:20;
  background:color-mix(in srgb,var(--bg) 94%,transparent);
  -webkit-backdrop-filter:blur(14px); backdrop-filter:blur(14px);
  border-bottom:1px solid var(--line);
  padding:calc(10px + env(safe-area-inset-top)) 13px 10px;
}
.bar{display:flex; align-items:center; gap:8px; margin-bottom:10px}
.brand{flex:1; min-width:0}
.brand h1{
  margin:0; font-size:.88rem; font-weight:700; letter-spacing:-.1px;
  line-height:1.25; color:var(--tx); white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis;
}
.brand p{margin:2px 0 0; font-size:.68rem; color:var(--tx3); white-space:nowrap}

/* segment (Кирилл | Lotin) */
.seg{
  display:flex; flex:none; gap:2px; padding:3px;
  background:var(--seg); border:1px solid var(--line);
  border-radius:13px;
}
.seg button{
  min-height:36px; padding:0 8px;
  background:none; border:0; border-radius:10px;
  color:var(--tx3); font:inherit; font-size:.57rem; font-weight:750;
  letter-spacing:.3px; text-transform:uppercase; cursor:pointer;
  -webkit-tap-highlight-color:transparent; white-space:nowrap;
}
.seg button[aria-pressed=true]{
  background:var(--card); color:var(--acc);
  box-shadow:var(--shadow);
  border:1px solid color-mix(in srgb,var(--acc) 28%,transparent);
}
.icon{
  flex:none; width:42px; height:42px; display:grid; place-items:center;
  background:var(--seg); color:var(--tx2);
  border:1px solid var(--line); border-radius:13px;
  cursor:pointer; -webkit-tap-highlight-color:transparent;
}
.icon:active{background:var(--line)}
.icon svg{width:21px; height:21px; fill:none; stroke:currentColor;
  stroke-width:2; stroke-linecap:round; stroke-linejoin:round}
.icon .sun{display:none}                       /* kunduzda: oy (tunga o'tish) */
:root[data-theme=dark] .icon .sun{display:block}
:root[data-theme=dark] .icon .moon{display:none}
@media (prefers-color-scheme:dark){             /* tunda: quyosh (kunga o'tish) */
  :root:not([data-theme=light]) .icon .sun{display:block}
  :root:not([data-theme=light]) .icon .moon{display:none}
}

.sbox{position:relative; display:flex; align-items:center}
.sbox>svg{
  position:absolute; left:15px; width:21px; height:21px;
  fill:none; stroke:var(--tx3); stroke-width:2; pointer-events:none;
}
#q{
  width:100%; height:calc(54px - var(--sh)); padding:0 50px 0 47px;
  background:var(--card); color:var(--tx);
  border:1px solid var(--line2); border-radius:14px;
  font:inherit; font-size:calc(.95rem * var(--k));
}
#q::placeholder{color:var(--tx3)}
#q:focus{border-color:var(--acc); outline:none;
  box-shadow:0 0 0 3px color-mix(in srgb,var(--acc) 18%,transparent)}
#clr{
  position:absolute; right:6px; width:44px; height:44px;
  display:none; place-items:center;
  background:none; border:0; border-radius:11px;
  color:var(--tx2); font-size:1.4rem; line-height:1; cursor:pointer;
}
#clr.on{display:grid}

.filters{display:flex; gap:9px; margin-top:10px}
.cities{display:flex; flex:1; gap:9px; min-width:0}
.filters button{
  flex:1; min-height:calc(50px - var(--sh));
  display:flex; align-items:center; justify-content:center; gap:8px;
  background:var(--card); color:var(--tx2);
  border:1px solid var(--line2); border-radius:14px;
  font:inherit; font-size:calc(1rem * var(--k)); font-weight:600; cursor:pointer;
  -webkit-tap-highlight-color:transparent;
}
.filters button .n{
  font-size:calc(.78rem * var(--k)); color:var(--tx3); font-variant-numeric:tabular-nums;
  background:color-mix(in srgb,var(--tx3) 14%,transparent);
  padding:2px 8px; border-radius:20px;
}
.filters button[aria-pressed=true]{color:#fff; font-weight:700}
.filters button[data-city=madina][aria-pressed=true]{background:var(--madina); border-color:var(--madina)}
.filters button[data-city=makka][aria-pressed=true]{background:var(--makka); border-color:var(--makka)}
:root[data-theme=dark] .filters button[aria-pressed=true],
.filters button[aria-pressed=true]{color:#fff}
@media (prefers-color-scheme:dark){
  :root:not([data-theme=light]) .filters button[aria-pressed=true]{color:#08110d}
}
:root[data-theme=dark] .filters button[aria-pressed=true]{color:#08110d}
.filters button[aria-pressed=true] .n{background:rgba(0,0,0,.18); color:inherit; opacity:.75}

/* Matn o'lchami: har bosilganda kichrayadi. Ichidagi "Aa" joriy o'lchamni
   ko'rsatadi, shuning uchun alohida ro'yxat kerak emas.
   Selektor ".filters .tsz" - ".filters button" dan spetsifikroq, aks holda
   u yerdagi flex:1 tugmani yarim qatorga cho'zib yuboradi. */
.filters .tsz{
  flex:0 0 auto; width:68px; padding:0;
  display:grid; place-items:center;              /* markazda tursin */
  color:var(--tx3);
}
/* "A" va "a" bitta matn oqimida - o'zi bir xil chiziqqa tushadi */
.filters .tsz .aa{line-height:1; white-space:nowrap}
.filters .tsz .a1{font-size:calc(1.15rem * var(--k)); font-weight:700}
.filters .tsz .a2{font-size:calc(.82rem * var(--k)); font-weight:600}

/* ---------- ro'yxat ---------- */
main{padding:16px 12px 0; max-width:780px; margin:0 auto}
.card{
  --acc:var(--makka);
  background:linear-gradient(180deg,var(--card),var(--card2));
  border:1px solid var(--line); border-radius:var(--r);
  margin-bottom:13px; overflow:hidden; box-shadow:var(--shadow);
}
.card[data-city=madina]{--acc:var(--madina)}
.card.hide{display:none}

.head{
  width:100%; display:flex; align-items:center; gap:13px;
  padding:16px 14px; margin:0;
  background:none; border:0; color:inherit;
  font:inherit; text-align:left; cursor:pointer;
  -webkit-tap-highlight-color:transparent;
}
.head:active{background:color-mix(in srgb,var(--acc) 7%,transparent)}
.num{
  flex:none; width:44px; height:44px; border-radius:13px;
  display:grid; place-items:center;
  background:color-mix(in srgb,var(--acc) 13%,transparent);
  border:1px solid color-mix(in srgb,var(--acc) 34%,transparent);
  color:var(--acc); font-size:1.02rem; font-weight:700;
  font-variant-numeric:tabular-nums;
}
.ttl{flex:1; min-width:0}
.city{
  display:block; font-size:.7rem; font-weight:700; letter-spacing:.9px;
  text-transform:uppercase; color:var(--acc); opacity:.9; margin-bottom:3px;
}
.name{display:block; font-size:var(--fs); font-weight:650; line-height:1.36; color:var(--tx)}
.ar{
  display:block; margin-top:4px; font-size:1rem; color:var(--tx3);
  font-family:"Noto Naskh Arabic","Traditional Arabic",serif; direction:rtl;
}
.chev{flex:none; width:26px; height:26px; color:var(--tx3);
  transition:transform .28s ease,color .2s}
.card.open .chev{transform:rotate(180deg); color:var(--acc)}

/* accordion: yopiq turadi */
.panel{display:grid; grid-template-rows:0fr; transition:grid-template-rows .3s ease}
.card.open .panel{grid-template-rows:1fr}
.panel>.in{overflow:hidden; min-height:0}

.art{display:block; width:100%; height:auto; aspect-ratio:800/260; background:#070b14}
img.art{object-fit:cover}
.artwrap{position:relative; border-block:1px solid var(--line)}
.body{padding:17px 16px 19px}
.body p{margin:0 0 16px; font-size:var(--fs); line-height:1.78; color:var(--tx2)}
.body p:last-of-type{margin-bottom:0}

.note{
  margin-top:17px; padding:15px 16px;
  border-radius:14px; border:1px solid var(--line2);
  background:color-mix(in srgb,var(--tx3) 6%,transparent);
  font-size:var(--fs); line-height:1.74; color:var(--tx2);
}
.note.esla{
  border-color:color-mix(in srgb,var(--acc) 32%,transparent);
  background:color-mix(in srgb,var(--acc) 9%,transparent);
  color:var(--tx);
}
.note b{display:block; margin-bottom:6px; font-size:.76rem; font-weight:750;
  letter-spacing:1.1px; text-transform:uppercase; color:var(--acc)}
.note.amaliy b{color:var(--tx3)}

.maps{
  display:flex; align-items:center; justify-content:center; gap:10px;
  min-height:58px; margin-top:18px; padding:0 18px;
  background:color-mix(in srgb,var(--acc) 12%,transparent);
  border:1px solid color-mix(in srgb,var(--acc) 42%,transparent);
  border-radius:15px;
  color:var(--acc); font-size:1.04rem; font-weight:650; text-decoration:none;
  -webkit-tap-highlight-color:transparent;
}
.maps:active{background:color-mix(in srgb,var(--acc) 22%,transparent)}
.maps svg{width:21px; height:21px; flex:none}
.coord{margin-top:11px; text-align:center; font-size:.88rem;
  color:var(--tx3); font-variant-numeric:tabular-nums}
.coord i{font-style:normal; opacity:.85}

#empty{display:none; padding:54px 20px; text-align:center; color:var(--tx3)}
#empty.on{display:block}
#empty b{display:block; margin-bottom:7px; color:var(--tx2); font-size:1.08rem}

.usage{max-width:780px; margin:24px auto 0; padding:22px 16px 28px;
  border-top:1px solid var(--line)}
.usage h2{margin:0 0 14px; font-size:.78rem; font-weight:750;
  letter-spacing:1.4px; text-transform:uppercase; color:var(--tx3)}
.usage p{margin:0 0 14px; font-size:var(--fs); line-height:1.78; color:var(--tx2)}
.usage p:last-child{margin-bottom:0}
.usage strong{color:var(--tx); font-weight:700}

/* tor telefonlar (360px va undan kichik) */
@media (max-width:389px){
  .brand h1{font-size:.79rem}
  .brand p{font-size:.6rem}
  .seg button{font-size:.52rem; padding:0 6px}
  .icon{width:38px; height:38px}
  .top{padding-inline:10px}
}
@media (min-width:620px){
  .brand h1{font-size:1.18rem}
}
@media (prefers-reduced-motion:reduce){*{transition:none !important}}
"""

JS = r"""
(function(){
  var root=document.documentElement,
      q=document.getElementById('q'), clr=document.getElementById('clr'),
      empty=document.getElementById('empty'),
      cards=[].slice.call(document.querySelectorAll('.card')),
      fbtn=[].slice.call(document.querySelectorAll('.cities button')),
      sbtn=[].slice.call(document.querySelectorAll('.seg button')),
      tsz=document.getElementById('tsz'),
      city='madina', mode='c', size=0;

  function save(k,v){ try{localStorage.setItem(k,v);}catch(e){} }
  function load(k){ try{return localStorage.getItem(k);}catch(e){return null;} }

  /* ---------- yozuv: kirill / lotin ---------- */
  function setScript(m){
    mode=m;
    document.querySelectorAll('.t').forEach(function(el){
      if(el.dataset.c===undefined) el.dataset.c=el.textContent;   // kirillni saqlab qolamiz
      el.textContent = m==='l' ? el.dataset.l : el.dataset.c;
    });
    q.placeholder = m==='l' ? q.dataset.pl : q.dataset.pc;
    q.setAttribute('aria-label', m==='l' ? 'Kartalar ichidan qidirish' : 'Карталар ичидан қидириш');
    root.lang = m==='l' ? 'uz' : 'uz-Cyrl';
    sbtn.forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.m===m?'true':'false'); });
    save('yozuv',m);
    setSize(size);                 // o'lcham yozuvi ham yangi yozuvda bo'lsin
  }
  sbtn.forEach(function(b){
    b.addEventListener('click',function(){ setScript(b.dataset.m); });
  });

  /* ---------- matn o'lchami: bosgan sari kichrayadi ---------- */
  var SZ=['','m','s'],                                  // '' = Katta
      SZN={c:['Катта','Ўрта','Кичик'], l:['Katta',"O'rta",'Kichik']};
  function setSize(i){
    size=i;
    if(SZ[i]) root.setAttribute('data-size',SZ[i]); else root.removeAttribute('data-size');
    var nm=SZN[mode==='l'?'l':'c'][i];
    tsz.setAttribute('aria-label', (mode==='l'?"Matn o'lchami: ":'Матн ўлчами: ')+nm);
    tsz.title=nm;
    save('olcham', String(i));
  }
  tsz.addEventListener('click',function(){ setSize((size+1)%3); });

  /* ---------- mavzu: telefon sozlamasi + qo'lda ---------- */
  function setTheme(t){
    if(t) root.setAttribute('data-theme',t); else root.removeAttribute('data-theme');
    save('mavzu', t||'');
  }
  document.getElementById('th').addEventListener('click',function(){
    var dark = root.getAttribute('data-theme')==='dark' ||
      (!root.getAttribute('data-theme') &&
       matchMedia('(prefers-color-scheme:dark)').matches);
    setTheme(dark?'light':'dark');
  });

  /* ---------- qidiruv + filtr ---------- */
  function norm(s){
    return s.toLowerCase().replace(/[ʻʼ‘’‛`´'ъь]/g,'')
            .replace(/[^\p{L}\p{N}]+/gu,' ').trim();
  }
  function close(c){
    c.classList.remove('open');
    c.querySelector('.head').setAttribute('aria-expanded','false');
  }
  function apply(){
    var t=norm(q.value), terms=t?t.split(' '):[], n=0;
    cards.forEach(function(c){
      var ok=(c.dataset.city===city);
      if(ok&&terms.length){
        var h=c.dataset.s;
        for(var i=0;i<terms.length;i++){ if(h.indexOf(terms[i])<0){ok=false;break;} }
      }
      c.classList.toggle('hide',!ok);
      if(ok){n++;} else if(c.classList.contains('open')){ close(c); }
    });
    empty.classList.toggle('on',n===0);
    clr.classList.toggle('on',q.value.length>0);
  }
  fbtn.forEach(function(b){
    b.addEventListener('click',function(){
      city=b.dataset.city;
      fbtn.forEach(function(x){ x.setAttribute('aria-pressed',x===b?'true':'false'); });
      apply();
      window.scrollTo({top:0,behavior:'smooth'});
    });
  });
  q.addEventListener('input',apply);
  q.addEventListener('keydown',function(ev){ if(ev.key==='Enter') q.blur(); });
  clr.addEventListener('click',function(){ q.value=''; apply(); q.focus(); });

  /* ---------- accordion ---------- */
  cards.forEach(function(c){
    c.querySelector('.head').addEventListener('click',function(){
      var open=!c.classList.contains('open');
      c.classList.toggle('open',open);
      this.setAttribute('aria-expanded',open?'true':'false');
      if(open){
        var y=c.getBoundingClientRect().top,
            top=document.querySelector('.top').offsetHeight;
        if(y<top) window.scrollBy({top:y-top-8,behavior:'smooth'});
      }
    });
  });

  // o'lcham yozuvdan OLDIN tiklanadi: setScript() setSize() ni chaqiradi va
  // aks holda saqlangan qiymat o'qilgunicha ustidan yozib yuborilardi
  var sz=parseInt(load('olcham')||'0',10);
  setSize(sz>=0&&sz<=2 ? sz : 0);                  // asosiysi - Katta
  setScript(load('yozuv')==='l' ? 'l' : 'c');      // asosiysi - kirill
  var th=load('mavzu'); if(th) setTheme(th);       // yo'q bo'lsa telefonga ergashadi
  apply();
})();
"""

I_SEARCH = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/>'
            '<path d="M20 20l-3.6-3.6" stroke-linecap="round"/></svg>')
I_CHEV = ('<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
          ' stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
          ' aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>')
I_PIN = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"'
         ' stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 1 1 16 0z"/>'
         '<circle cx="12" cy="10" r="3"/></svg>')
I_THEME = ('<svg class="sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/>'
           '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2'
           'M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
           '<svg class="moon" viewBox="0 0 24 24" aria-hidden="true">'
           '<path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a6.7 6.7 0 0 0 10.5 10.5z"/></svg>')


def card_html(c):
    num, city = c['num'], c['city']
    head = T(c['title'], 'span', 'name')
    if c['arabic']:
        head += (f'<span class="ar" dir="rtl" lang="ar">{e(c["arabic"])}</span>')

    # qidiruv uchun: lotin ham, kirill ham
    src = ' '.join(filter(None, [
        c['title'], CITY[city], str(num), ' '.join(c['body']),
        c['remember'], c['practical'], c['coordNote'], c['lat'], c['lng']]))
    hay = norm(src) + ' ' + norm(to_cyrillic(src))

    body = ''.join(T(p, 'p') for p in c['body'])
    body += (f'<div class="note esla">{T("Turganingizda eslang", "b")}'
             f'{T(c["remember"])}</div>')
    if c['practical']:
        body += f'<div class="note amaliy">{T("Amaliy", "b")}{T(c["practical"])}</div>'

    maps = f'https://www.google.com/maps/search/?api=1&query={c["lat"]},{c["lng"]}'
    # "Google Maps" - brend nomi, o'girilmaydi; faqat qo'shimcha almashadi
    body += (f'<a class="maps" href="{e(maps)}" target="_blank" rel="noopener noreferrer">'
             f'{I_PIN}<span><span>Google Maps’</span>{T("da ochish")}</span></a>')
    coord = f'{c["lat"]}, {c["lng"]}'
    if c['coordNote']:
        coord += ' ' + T(f'({c["coordNote"]})', 'i')
    body += f'<div class="coord">{coord}</div>'

    return (
        f'<article class="card" data-city="{city}" data-s="{e(hay)}">'
        f'<h2 style="margin:0;font:inherit">'
        f'<button class="head" type="button" aria-expanded="false" aria-controls="p{num}">'
        f'<span class="num">{num}</span>'
        f'<span class="ttl">{T(CITY[city], "span", "city")}{head}</span>'
        f'{I_CHEV}</button></h2>'
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
    ph = 'Qidiruv: joy, ism, voqea'

    # Madina kartalari birinchi, keyin Makka (manbadagi tartib saqlanadi)
    cards = sorted(cards, key=lambda c: (c['city'] != 'madina', c['num']))

    doc = f"""<!DOCTYPE html>
<html lang="uz-Cyrl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f6f4ee" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#070a0f" media="(prefers-color-scheme:dark)">
<title>{e(to_cyrillic(title))}</title>
<style>{CSS}</style>
</head>
<body>
<header class="top">
  <div class="bar">
    <div class="brand">
      <h1>{T('Ziyorat kartalari')}</h1>
      <p>{T(f'{title.split(" ")[0]} · {len(cards)} ta joy')}</p>
    </div>
    <div class="seg" role="group" aria-label="Yozuv">
      <button type="button" data-m="c" aria-pressed="true">Кирилл</button>
      <button type="button" data-m="l" aria-pressed="false">Lotin</button>
    </div>
    <button id="th" class="icon" type="button" aria-label="Kunduzgi/tungi rejim">{I_THEME}</button>
  </div>
  <div class="sbox">
    {I_SEARCH}
    <input id="q" type="search" inputmode="search" autocomplete="off" autocapitalize="off"
           spellcheck="false" data-pc="{e(to_cyrillic(ph))}" data-pl="{e(ph)}"
           placeholder="{e(to_cyrillic(ph))}" aria-label="Карталар ичидан қидириш">
    <button id="clr" type="button" aria-label="Тозалаш">&times;</button>
  </div>
  <div class="filters">
    <div class="cities" role="group" aria-label="Shahar">
      <button type="button" data-city="madina" aria-pressed="true">{T('Madina')} <span class="n">{n_mad}</span></button>
      <button type="button" data-city="makka" aria-pressed="false">{T('Makka')} <span class="n">{n_mak}</span></button>
    </div>
    <button id="tsz" class="tsz" type="button" aria-label="Матн ўлчами"><span
      class="aa"><span class="a1">A</span><span class="a2">a</span></span></button>
  </div>
</header>

<main>
{''.join(card_html(c) for c in cards)}
<div id="empty">{T('Hech narsa topilmadi', 'b')}{T("Boshqa so'z bilan qidirib ko'ring.")}</div>
</main>

<section class="usage">
  <h2>{T('Ishlatish tartibi')}</h2>
  {''.join(f'<p>{T_rich(u)}</p>' for u in data['usage'])}
</section>

<script>{JS}</script>
</body>
</html>
"""
    open(OUT, 'w', encoding='utf-8').write(doc)
    print(f'{OUT} yozildi: {len(cards)} karta, {len(doc.encode()):,} bayt')


if __name__ == '__main__':
    main()
