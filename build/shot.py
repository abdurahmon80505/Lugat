#!/usr/bin/env python3
"""Pixel o'lchamida skrinshot + interaktiv tekshiruv (kirill/lotin, tun/kun)."""
import pathlib
import sys

from playwright.sync_api import sync_playwright

CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else 'shots')
OUT.mkdir(exist_ok=True)
URL = 'file://' + str(pathlib.Path(sys.argv[1]).resolve())


def run(pw, scheme):
    b = pw.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 412, 'height': 915}, device_scale_factor=2,
                    is_mobile=True, has_touch=True, color_scheme=scheme)
    errs, reqs = [], []
    pg.on('pageerror', lambda x: errs.append(str(x)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('request', lambda r: reqs.append(r.url))
    pg.goto(URL)
    pg.wait_for_timeout(400)
    return b, pg, errs, reqs


with sync_playwright() as pw:
    # ---------- telefon TUNGI rejimda ----------
    b, pg, errs, reqs = run(pw, 'dark')
    bg = pg.eval_on_selector('body', 'e=>getComputedStyle(e).backgroundColor')
    print('telefon tungi -> fon:', bg)
    print('boshlang\'ich yozuv:', pg.inner_text('.brand h1'))
    print('boshlang\'ich filtr :', pg.eval_on_selector_all(
        '.filters button', 'e=>e.map(x=>[x.textContent.trim(),x.ariaPressed])'))
    print('ko\'rinadigan karta :', pg.eval_on_selector_all('.card:not(.hide)', 'e=>e.length'),
          pg.eval_on_selector_all('.card:not(.hide)', 'e=>[...new Set(e.map(x=>x.dataset.city))]'))
    pg.screenshot(path=str(OUT / '01-tun-kirill.png'))

    # kartani ochish
    pg.click('.card .head')
    pg.wait_for_timeout(600)
    pg.eval_on_selector('.card', "e=>e.scrollIntoView()")
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / '02-tun-ochiq.png'))

    # lotinga o'tish
    pg.click('.seg button[data-m=l]')
    pg.wait_for_timeout(300)
    print('lotinda sarlavha  :', pg.inner_text('.brand h1'))
    print('lotinda 1-karta   :', pg.inner_text('.card .name'))
    print('html lang         :', pg.get_attribute('html', 'lang'))
    pg.screenshot(path=str(OUT / '03-tun-lotin.png'))

    # kirillga qaytish
    pg.click('.seg button[data-m=c]')
    pg.wait_for_timeout(250)
    print('kirillga qaytdi   :', pg.inner_text('.card .name'))

    # qidiruv: kirillcha va lotincha bir xil ishlashi kerak
    for term in ('ғор', 'gor', 'ХАНДАҚ', 'кааба', 'uhud'):
        pg.fill('#q', term)
        pg.wait_for_timeout(220)
        # qidiruv ikkala shaharda ham ishlashi uchun filtrlarni sinaymiz
        res = []
        for cty in ('madina', 'makka'):
            pg.click(f'.filters button[data-city={cty}]')
            pg.wait_for_timeout(180)
            res += pg.eval_on_selector_all('.card:not(.hide) .name', 'e=>e.map(x=>x.textContent)')
        print(f'  qidiruv {term!r} -> {res}')
    pg.fill('#q', '')
    pg.click('.filters button[data-city=madina]')
    pg.wait_for_timeout(250)

    # mavzuni qo'lda kunduzgiga o'tkazish
    pg.click('#th')
    pg.wait_for_timeout(350)
    print('qo\'lda kunduzgi   :', pg.get_attribute('html', 'data-theme'),
          pg.eval_on_selector('body', 'e=>getComputedStyle(e).backgroundColor'))
    pg.screenshot(path=str(OUT / '04-qolda-kun.png'))

    print('tarmoq so\'rovlari :', [r for r in reqs if not r.startswith('file:')] or 'yo\'q')
    print('konsol xatolari   :', errs or 'yo\'q')
    ow = pg.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
    print('gorizontal skroll :', 'yo\'q' if ow[0] <= ow[1] else f'BOR {ow}')
    print('maps href         :', pg.get_attribute('.card .maps', 'href'))
    b.close()

    # ---------- telefon KUNDUZGI rejimda ----------
    b, pg, errs, reqs = run(pw, 'light')
    print('\ntelefon kunduzgi -> fon:',
          pg.eval_on_selector('body', 'e=>getComputedStyle(e).backgroundColor'))
    pg.screenshot(path=str(OUT / '05-kun-kirill.png'))
    pg.click('.filters button[data-city=makka]')
    pg.wait_for_timeout(300)
    pg.click('.card:not(.hide) .head')
    pg.wait_for_timeout(600)
    pg.eval_on_selector('.card:not(.hide)', "e=>e.scrollIntoView()")
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / '06-kun-makka.png'))
    print('konsol xatolari   :', errs or 'yo\'q')

    # o'lchamlar
    print('shrift (matn)     :', pg.eval_on_selector('.body p', 'e=>getComputedStyle(e).fontSize'))
    for sel, nm in (('.card:not(.hide) .head', 'karta sarlavhasi'),
                    ('.card:not(.hide) .maps', 'Maps tugmasi'),
                    ('.filters button', 'filtr'), ('.seg button', 'yozuv tugmasi'),
                    ('#th', 'mavzu tugmasi')):
        r = pg.eval_on_selector(sel, 'e=>{const r=e.getBoundingClientRect();'
                                     'return [Math.round(r.width),Math.round(r.height)]}')
        print(f'  {nm:18}: {r[0]}x{r[1]}')
    b.close()
