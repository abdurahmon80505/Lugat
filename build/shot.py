#!/usr/bin/env python3
"""Pixel o'lchamida skrinshot + interaktiv tekshiruv."""
import pathlib
import sys

from playwright.sync_api import sync_playwright

OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else 'shots')
OUT.mkdir(exist_ok=True)
URL = 'file://' + str(pathlib.Path(sys.argv[1]).resolve())

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
                           args=['--no-sandbox'])
    # Pixel 7 ga yaqin
    pg = b.new_page(viewport={'width': 412, 'height': 915}, device_scale_factor=2,
                    is_mobile=True, has_touch=True)

    errs = []
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda x: errs.append(str(x)))
    reqs = []
    pg.on('request', lambda r: reqs.append(r.url))

    pg.goto(URL)
    pg.wait_for_timeout(400)

    def shot(name, full=False):
        pg.screenshot(path=str(OUT / f'{name}.png'), full_page=full)

    shot('01-yopiq')

    # 1-kartani ochish
    pg.click('.card[data-s] .head')
    pg.wait_for_timeout(600)
    shot('02-ochiq')

    # ochilgan kartaning ichi
    pg.evaluate("document.querySelectorAll('.card')[0].scrollIntoView()")
    pg.wait_for_timeout(300)
    shot('03-ichki')

    # yopish
    pg.click('.card .head')
    pg.wait_for_timeout(500)

    # filtr: Madina
    pg.click('.filters button[data-city=madina]')
    pg.wait_for_timeout(300)
    vis = pg.eval_on_selector_all('.card:not(.hide)', 'e=>e.length')
    cities = pg.eval_on_selector_all('.card:not(.hide)', 'e=>[...new Set(e.map(x=>x.dataset.city))]')
    print('filtr Madina -> ko\'rinadi:', vis, cities, '| sanoq:', pg.inner_text('#shown'))
    shot('04-madina')

    # qidiruv (apostrofsiz yozilgan so'z ham topilishi kerak)
    pg.click('.filters button[data-city=all]')
    pg.fill('#q', 'gor')
    pg.wait_for_timeout(300)
    n = pg.eval_on_selector_all('.card:not(.hide)', 'e=>e.map(x=>x.querySelector(".name").textContent)')
    print('qidiruv "gor" ->', n)
    shot('05-qidiruv')

    pg.fill('#q', 'xandaq')
    pg.wait_for_timeout(250)
    print('qidiruv "xandaq" ->',
          pg.eval_on_selector_all('.card:not(.hide)', 'e=>e.map(x=>x.querySelector(".name").textContent)'))

    pg.fill('#q', 'zzzz')
    pg.wait_for_timeout(250)
    print('qidiruv "zzzz" -> bo\'sh holat:', pg.is_visible('#empty'))
    shot('06-bosh')

    pg.click('#clr')
    pg.wait_for_timeout(250)
    print('tozalashdan keyin:', pg.eval_on_selector_all('.card:not(.hide)', 'e=>e.length'))

    # Maps havolasi
    href = pg.get_attribute('.card .maps', 'href')
    print('maps href:', href)

    # gorizontal skroll bormi
    ow = pg.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
    print('scrollWidth/innerWidth:', ow)

    # hamma kartani ochib to'liq sahifa
    pg.evaluate("""document.querySelectorAll('.card').forEach(c=>{
        c.classList.add('open'); c.querySelector('.head').setAttribute('aria-expanded','true');})""")
    pg.wait_for_timeout(700)
    shot('07-hammasi', full=True)

    print('tarmoq so\'rovlari:', [r for r in reqs if not r.startswith('file:')] or 'yo\'q (faqat local)')
    print('konsol xatolari:', errs or 'yo\'q')
    b.close()
