#!/usr/bin/env python3
"""index.html ichidagi matn manba .md bilan AYNAN bir xilligini tekshiradi.

1) Manbadagi har bir bo'lak HTML'da lotin ko'rinishida (data-l) bormi;
2) Ko'rinadigan kirill matn AYNAN o'sha lotin matnning transliteratsiyasimi
   (ya'ni yozuv o'zgargan, matn o'zgarmagan);
3) HTML'dagi har bir matn manbadan yoki ruxsat etilgan interfeys
   yozuvlaridan kelganmi - qo'shib yuborilgani yo'qmi;
4) Maps havolalari va koordinatalar to'g'rimi.
"""
import re
import sys
from html.parser import HTMLParser

from parse import parse
from translit import to_cyrillic

SKIP = {'script', 'style', 'svg'}

# Interfeys yozuvlari (manba matni emas) - lotin ko'rinishida
UI = [
    'Makka–Madina ziyorat kartalari', 'Ziyorat kartalari', 'Makka–Madina · 22 ta joy',
    'Qidiruv: joy, ism, voqea', 'Madina', 'Makka',
    'Turganingizda eslang', 'Amaliy', 'da ochish',
    'Hech narsa topilmadi', "Boshqa so'z bilan qidirib ko'ring.",
    'Ishlatish tartibi',
]
# Almashmaydigan belgilar (raqam, koordinata, arabcha, ×)
FIXED = ['Кирилл', 'Lotin', '×', 'Google Maps’', 'A', 'a']


class T(HTMLParser):
    """data-l bo'lgan elementlarni va ularning ko'rinadigan matnini yig'adi."""

    def __init__(self):
        super().__init__()
        self.skip = 0
        self.stack = []          # ochiq data-l elementlari
        self.pairs = []          # (lotin, ko'rinadigan)
        self.nodes = []          # barcha ko'rinadigan matn tugunlari

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            return
        a = dict(attrs)
        if 'data-l' in a:
            self.stack.append([a['data-l'], ''])

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip:
            self.skip -= 1
            return
        if self.stack and tag in ('span', 'p', 'b', 'strong', 'i', 'h1', 'h2'):
            lat, seen = self.stack.pop()
            self.pairs.append((lat, seen))

    def handle_data(self, d):
        if self.skip:
            return
        if self.stack:
            self.stack[-1][1] += d
        if d.strip():
            self.nodes.append(d.strip())


def main(html_path, md_path):
    raw = open(html_path, encoding='utf-8').read()
    p = T()
    p.feed(raw)

    data = parse(md_path)
    chunks = []
    for c in data['cards']:
        chunks += c['body']
        for k in ('title', 'remember', 'practical'):
            if c[k]:
                chunks.append(c[k])
        if c['coordNote']:
            chunks.append(f'({c["coordNote"]})')
    # "Ishlatish tartibi" - **qalin** bo'laklarga bo'linadi
    frags = [f.strip() for u in data['usage'] for f in re.split(r'\*\*', u) if f.strip()]

    lat_seen = [lat for lat, _ in p.pairs]

    # --- 1) manba -> HTML (lotin) ---
    missing = [c for c in chunks if c not in lat_seen]
    if missing:
        print('YETISHMAYDI (%d):' % len(missing))
        for m in missing[:8]:
            print('  -', m[:90])
        return 1
    ufrag = [f for f in frags if not any(f in l for l in lat_seen)]
    if ufrag:
        print('ISHLATISH bo\'lagi yetishmaydi:', ufrag[:5])
        return 1
    print('1) manba -> HTML (lotin) : %d bo\'lak, hammasi aynan topildi' % len(chunks))

    # --- 2) kirill = transliteratsiya (matn o'zgarmagan) ---
    bad = [(l, s) for l, s in p.pairs if s != to_cyrillic(l)]
    if bad:
        print('KIRILL MOS EMAS (%d):' % len(bad))
        for l, s in bad[:8]:
            print('  lotin :', l[:70])
            print('  kirill:', s[:70])
            print('  kutil.:', to_cyrillic(l)[:70])
        return 1
    print('2) kirill = translit     : %d element, hammasi mos' % len(p.pairs))

    # --- 3) teskari tekshiruv: ortiqcha matn yo'q ---
    # Arab yozuvidagi sarlavhalar o'zgarmaydi - ular ham ruxsat etilgan
    arabic = [c['arabic'] for c in data['cards'] if c['arabic']]
    allowed = ([to_cyrillic(x) for x in chunks + UI + frags]
               + chunks + UI + frags + FIXED + arabic)
    rest = []
    for n in p.nodes:
        s = n
        for ok in sorted(allowed, key=len, reverse=True):
            s = s.replace(ok, ' ')
        s = re.sub(r'[\s\d.,/()–—:]+', '', s)
        if s:
            rest.append((n[:70], s[:70]))
    if rest:
        print('QO\'SHIMCHA MATN (%d):' % len(rest))
        for a, b in rest[:8]:
            print('  node=%r qoldiq=%r' % (a, b))
        return 1
    print('3) HTML -> manba         : %d matn tuguni, ortiqchasi yo\'q' % len(p.nodes))

    # --- 4) Maps havolalari ---
    for c in data['cards']:
        u = 'https://www.google.com/maps/search/?api=1&amp;query=%s,%s' % (c['lat'], c['lng'])
        if u not in raw:
            print('MAPS HAVOLASI XATO, karta', c['num'])
            return 1
    print('4) Maps havolalari       : %d ta, format va koordinatalar to\'g\'ri'
          % len(data['cards']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
