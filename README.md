# Makka–Madina ziyorat kartalari

`index.html` — bitta fayl, **to'liq offline** ziyorat qo'llanmasi. 22 ta karta.

Faylni telefonga ko'chirib, brauzerda ochish kifoya. Internet **umuman** kerak emas.

## Nima bor

- **Tungi rejim** — oq yoki och fon yo'q, faqat qorong'i.
- **Qidiruv** — joy, voqea yoki ism bo'yicha. Apostrofga e'tibor bermaydi:
  `gor` deb yozsang ham `g'ori` topiladi.
- **Madina / Makka filtri** — yuqorida, qidiruv yonida.
- **Accordion kartalar** — yopiq turadi, bosilganda ochiladi.
- **Google Maps tugmasi** — har kartada:
  `https://www.google.com/maps/search/?api=1&query=LAT,LNG`
- **Mobil uchun** — Pixel o'lchamida sinalgan, katta matn (17px),
  barcha tugmalar 48px dan katta, gorizontal skroll yo'q.
- Vanilla JS, framework yo'q, tashqi CDN/shrift/rasm yo'q.

## Matn

Matn `ziyorat-kartalari.md` dan **aynan** olinadi — bir harf ham
o'zgartirilmagan. `build/verify_html.py` buni har ikki tomonlama tekshiradi:
manbadagi har bir bo'lak HTML'da bormi, va HTML'dagi har bir matn manbadan
kelganmi.

## Qayta yig'ish

```sh
python3 build/build.py ziyorat-kartalari.md index.html   # yig'ish
PYTHONPATH=build python3 build/verify_html.py index.html ziyorat-kartalari.md
```

## Rasmlar

Hozir har kartada **ichki SVG manzara** — kod bilan chizilgan, tashqi fayl yo'q
(bu sessiyada Wikimedia Commons tarmoq siyosati bilan bloklangan edi).

Haqiqiy fotosurat qo'shmoqchi bo'lsang, Wikimedia Commons'dan erkin litsenziyali
rasmni yuklab, `images/` papkasiga karta raqami bilan qo'y va qayta yig':

```sh
mkdir -p images
# images/1.jpg, images/4.jpg, images/9.jpg ...
pip install Pillow
python3 build/build.py ziyorat-kartalari.md index.html
```

Build o'zi 800px kenglikka kichraytiradi, JPEG 75% qiladi va base64 holda HTML
ichiga joylashtiradi. Rasm bo'lmagan kartalar SVG manzarasida qoladi.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| `index.html` | tayyor natija — shu faylning o'zi yetarli |
| `ziyorat-kartalari.md` | manba matn |
| `build/parse.py` | markdown → strukturaviy ma'lumot |
| `build/art.py` | 22 ta ichki SVG manzara |
| `build/build.py` | HTML yig'uvchi (+ base64 rasm) |
| `build/verify_html.py` | matn aynanligini tekshirish |
| `build/preview.py` | manzaralarni bitta varaqda ko'rish |
| `build/shot.py` | Pixel o'lchamida skrinshot va tekshiruv |
