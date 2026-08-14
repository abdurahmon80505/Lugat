#!/usr/bin/env python3
"""Barcha 22 manzarani bitta varaqda ko'rish (faqat ishlab chiqish uchun)."""
import pathlib
import sys

from art import CARD_SCENE, scene_svg
from parse import parse

md = sys.argv[1]
out = pathlib.Path(sys.argv[2])
cards = parse(md)['cards']

items = ''.join(
    f'<figure><div class="w">{scene_svg(c["num"], c["city"])}</div>'
    f'<figcaption>{c["num"]}. {CARD_SCENE[c["num"]]} — {c["title"]}</figcaption></figure>'
    for c in cards)

out.write_text(f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{background:#070a0f;color:#aeb9c9;font:14px system-ui;margin:0;padding:14px}}
.g{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;max-width:1180px;margin:0 auto}}
figure{{margin:0;border:1px solid #1e2836;border-radius:14px;overflow:hidden;background:#111823}}
.w{{aspect-ratio:800/260}}
svg{{display:block;width:100%;height:100%}}
figcaption{{padding:9px 12px;font-size:13px;color:#7d8899}}
</style></head><body><div class="g">{items}</div></body></html>""", encoding='utf-8')
print('yozildi:', out)
