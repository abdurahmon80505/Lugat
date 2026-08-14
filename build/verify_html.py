#!/usr/bin/env python3
"""index.html ichidagi matn manba .md bilan AYNAN bir xilligini tekshiradi.

Ikki tomonlama:
  1) manbadagi har bir bo'lak HTML'da bormi;
  2) HTML'dagi har bir ko'rinadigan matn manbadan (yoki ruxsat etilgan
     interfeys yozuvlaridan) kelganmi - ya'ni qo'shib yuborilgani yo'qmi.
"""
import re
import sys
from html.parser import HTMLParser

from parse import parse

SKIP = {'script', 'style', 'svg'}

# Interfeys yozuvlari (manba matni emas)
UI = [
    'Makka–Madina ziyorat kartalari', 'Qidiruv: joy, voqea, ism…',
    'Qidiruvni tozalash', 'Kartalar ichidan qidirish', "Shahar bo'yicha filtr",
    'Hammasi', 'Madina', 'Makka', 'Turganingda esla', 'Amaliy',
    'Google Maps’da ochish', 'Hech narsa topilmadi', "Boshqa so'z bilan qidirib ko'r.",
    'Ishlatish tartibi', '×',
]


class T(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.out = []
        self.raw = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in SKIP and self.depth:
            self.depth -= 1

    def handle_data(self, d):
        if not self.depth:
            self.raw.append(d)          # <strong> ichidagi matn ham uzilmasin
            if d.strip():
                self.out.append(d.strip())


def main(html_path, md_path):
    p = T()
    p.feed(open(html_path, encoding='utf-8').read())
    nodes = p.out
    blob = '\n'.join(nodes)
    tight = ''.join(p.raw)      # inline bo'shliqlar saqlangan holat

    data = parse(md_path)
    chunks = []
    for c in data['cards']:
        chunks += c['body']
        for k in ('title', 'arabic', 'remember', 'practical', 'coordNote'):
            if c[k]:
                chunks.append(c[k])
    # "Ishlatish tartibi" matni HTML'da **qalin** belgisisiz chiqadi
    usage = [re.sub(r'\*\*(.+?)\*\*', r'\1', u) for u in data['usage']]

    missing = [c for c in chunks + usage if c not in blob and c not in tight]
    if missing:
        print('YETISHMAYDI (%d):' % len(missing))
        for m in missing[:10]:
            print('  -', m[:90])
        return 1
    print('1) manba -> HTML : %d bo\'lak, hammasi aynan topildi' % len(chunks + usage))

    # 2) teskari tekshiruv
    # <strong> matnni bo'laklarga bo'ladi - bo'laklarni ham ruxsat etamiz
    frags = [f.strip() for u in data['usage'] for f in re.split(r'\*\*', u) if f.strip()]

    rest = []
    for n in nodes:
        s = n
        for ok in sorted(chunks + usage + frags + UI, key=len, reverse=True):
            s = s.replace(ok, ' ')
        s = re.sub(r'[\s\d.,/()–—:]+', '', s)
        if s:
            rest.append((n[:70], s[:70]))
    if rest:
        print('QO\'SHIMCHA MATN TOPILDI (%d):' % len(rest))
        for a, b in rest[:10]:
            print('  node=%r  qoldiq=%r' % (a, b))
        return 1
    print('2) HTML -> manba : %d matn tugunining hammasi hisobga olindi' % len(nodes))

    # koordinatalar va Maps havolalari
    bad = 0
    raw = open(html_path, encoding='utf-8').read()
    for c in data['cards']:
        u = 'https://www.google.com/maps/search/?api=1&amp;query=%s,%s' % (c['lat'], c['lng'])
        if u not in raw:
            print('MAPS HAVOLASI XATO, karta', c['num'])
            bad = 1
    if bad:
        return 1
    print('3) Maps havolalari : %d ta, format va koordinatalar to\'g\'ri' % len(data['cards']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
