#!/usr/bin/env python3
"""Ziyorat kartalari: markdown -> strukturaviy ma'lumot.

Matn AYNAN saqlanadi: hech qanday qisqartirish, qo'shish yoki tahrir yo'q.
"""
import json
import re
import sys

ARABIC = re.compile(r'[؀-ۿ]')


def parse(md_path):
    raw = open(md_path, encoding='utf-8').read()
    lines = raw.split('\n')

    cards = []
    city = None
    card = None
    usage = []          # "ISHLATISH TARTIBI" bo'limi
    in_usage = False
    doc_title = None

    def flush():
        nonlocal card
        if card is not None:
            cards.append(card)
            card = None

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # H1: hujjat sarlavhasi / shahar / ishlatish tartibi
        if s.startswith('# '):
            head = s[2:].strip()
            if head == 'MADINA':
                flush()
                city, in_usage = 'madina', False
            elif head == 'MAKKA':
                flush()
                city, in_usage = 'makka', False
            elif head == 'ISHLATISH TARTIBI':
                flush()
                in_usage = True
            else:
                doc_title = head
            i += 1
            continue

        # H2: yangi karta
        if s.startswith('## '):
            flush()
            head = s[3:].strip()
            m = re.match(r'^(\d+)\.\s*(.+)$', head)
            num, rest = int(m.group(1)), m.group(2).strip()

            title, arabic = rest, None
            # Em-dash'dan keyingi qism arab yozuvida bo'lsagina ajratamiz
            # ("Hiro g'ori - Jabal un-Nur" kabi lotin nomlar butun qoladi).
            if '—' in rest:
                left, _, right = rest.rpartition('—')
                if ARABIC.search(right):
                    title, arabic = left.strip(), right.strip()

            card = {
                'num': num, 'city': city, 'title': title, 'arabic': arabic,
                'lat': None, 'lng': None, 'coordNote': None,
                'body': [], 'remember': None, 'practical': None,
            }
            i += 1
            continue

        if not s or s == '---':
            i += 1
            continue

        if s.startswith('>'):        # build uchun eslatma - kontent emas
            i += 1
            continue

        if in_usage:
            usage.append(s)
            i += 1
            continue

        if card is None:
            i += 1
            continue

        # Koordinata qatori: **LAT, LNG** *(izoh)*
        m = re.match(r'^\*\*(-?[\d.]+),\s*(-?[\d.]+)\*\*\s*(?:\*\((.+)\)\*)?$', s)
        if m and card['lat'] is None:
            card['lat'], card['lng'] = m.group(1), m.group(2)
            card['coordNote'] = m.group(3)
            i += 1
            continue

        m = re.match(r'^\*\*Turganingda esla:\*\*\s*(.+)$', s)
        if m:
            card['remember'] = m.group(1).strip()
            i += 1
            continue

        m = re.match(r'^\*\*Amaliy:\*\*\s*(.+)$', s)
        if m:
            card['practical'] = m.group(1).strip()
            i += 1
            continue

        card['body'].append(s)
        i += 1

    flush()
    return {'docTitle': doc_title, 'cards': cards, 'usage': usage}


def verify(data, md_path):
    """Har bir matn bo'lagi manba faylda AYNAN borligini tekshiramiz."""
    raw = open(md_path, encoding='utf-8').read()
    checked = 0
    for c in data['cards']:
        chunks = list(c['body'])
        for k in ('title', 'arabic', 'remember', 'practical', 'coordNote'):
            if c[k]:
                chunks.append(c[k])
        for ch in chunks:
            if ch not in raw:
                sys.exit('MATN MOS EMAS (karta %s): %r' % (c['num'], ch[:80]))
            checked += 1
    for u in data['usage']:
        if u not in raw:
            sys.exit('MATN MOS EMAS (ishlatish): %r' % u[:80])
        checked += 1
    return checked


if __name__ == '__main__':
    d = parse(sys.argv[1])
    n = verify(d, sys.argv[1])
    print('kartalar:', len(d['cards']), '| tekshirilgan bo\'lak:', n)
    print(json.dumps(d, ensure_ascii=False, indent=1)[:1400])
