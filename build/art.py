#!/usr/bin/env python3
"""Har bir karta uchun ichki (inline) SVG manzara.

Tashqi rasm/CDN/shrift ishlatilmaydi - hammasi HTML ichida chiziladi.
Tungi palitra: chuqur ko'k osmon, yulduzlar, ochroq siluetlar.
"""
import random

W, H = 800, 260
GND = 214            # yer chizig'i


class P:
    """Manzara palitrasi."""

    def __init__(self, city, uid=''):
        self.uid = uid
        self.acc = '#7fd3a8' if city == 'madina' else '#e0ac52'
        self.glow = '#a9edcb' if city == 'madina' else '#f6d18a'
        self.far = '#16202e'          # uzoq tog'/fon
        self.sil = '#26313f'          # asosiy silue (osmondan ochroq)
        self.dark = '#161f2b'         # soya tomoni
        self.gnd = '#0a0e14'          # yer


# ---------------------------------------------------------------- primitives
def dome(cx, base, rw, rh, f, edge=None, sw=1.5, finial=True):
    """Piyozsimon gumbaz (kengligi rw, balandligi rh)."""
    d = (f"M{cx-rw:.1f} {base:.1f}"
         f" C{cx-rw*1.04:.1f} {base-rh*0.42:.1f},{cx-rw*0.72:.1f} {base-rh*0.82:.1f},{cx:.1f} {base-rh:.1f}"
         f" C{cx+rw*0.72:.1f} {base-rh*0.82:.1f},{cx+rw*1.04:.1f} {base-rh*0.42:.1f},{cx+rw:.1f} {base:.1f} Z")
    s = f'<path d="{d}" fill="{f}"'
    if edge:
        s += f' stroke="{edge}" stroke-width="{sw}" stroke-linejoin="round"'
    s += '/>'
    if finial:
        c = edge or f
        s += (f'<path d="M{cx:.1f} {base-rh:.1f} v{-rh*0.20:.1f}" stroke="{c}"'
              f' stroke-width="{max(sw,1.6):.1f}" stroke-linecap="round"/>')
        s += f'<circle cx="{cx:.1f}" cy="{base-rh*1.24:.1f}" r="{max(rw*0.07,2):.1f}" fill="{c}"/>'
    return s


def box(x, y, w, h, f, edge=None, sw=1.4):
    s = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{f}"'
    if edge:
        s += f' stroke="{edge}" stroke-width="{sw}"'
    return s + '/>'


def minaret(x, base, h, w, p):
    """Minora: tana + ayvon + gumbazcha."""
    top = base - h
    s = box(x - w / 2, top + h * 0.20, w, h - h * 0.20, p.sil)
    s += box(x - w * 0.95, top + h * 0.18, w * 1.9, h * 0.045, p.sil)          # ayvon
    s += (f'<path d="M{x-w*0.95:.1f} {top+h*0.18:.1f} h{w*1.9:.1f}" stroke="{p.acc}"'
          f' stroke-width="1.6" opacity=".6"/>')
    s += box(x - w * 0.60, top + h * 0.075, w * 1.2, h * 0.105, p.sil)         # kichik bo'lim
    s += dome(x, top + h * 0.075, w * 0.60, h * 0.09, p.sil, p.acc, 1.3)
    return s


def arch(cx, base, w, h, f, edge=None, sw=1.6, op=1.0):
    """Nayzasimon ravoq."""
    d = (f"M{cx-w/2:.1f} {base:.1f} V{base-h*0.55:.1f}"
         f" Q{cx-w/2:.1f} {base-h:.1f} {cx:.1f} {base-h*1.06:.1f}"
         f" Q{cx+w/2:.1f} {base-h:.1f} {cx+w/2:.1f} {base-h*0.55:.1f}"
         f" V{base:.1f} Z")
    s = f'<path d="{d}" fill="{f}" opacity="{op}"'
    if edge:
        s += f' stroke="{edge}" stroke-width="{sw}"'
    return s + '/>'


def palm(x, base, s_, f):
    o = (f'<path d="M{x:.0f} {base:.0f} C{x-3*s_:.0f} {base-15*s_:.0f},'
         f'{x+3*s_:.0f} {base-23*s_:.0f},{x-1*s_:.0f} {base-32*s_:.0f}"'
         f' stroke="{f}" stroke-width="{3.0*s_:.1f}" fill="none" stroke-linecap="round"/>')
    ty = base - 32 * s_
    for a, k, dy in ((-1, 1.0, -3), (1, 1.0, -3), (-1, .66, 4), (1, .66, 4), (0, .5, 0)):
        if a == 0:
            o += (f'<path d="M{x-s_:.0f} {ty:.0f} C{x-3*s_:.0f} {ty-10*s_:.0f},'
                  f'{x+2*s_:.0f} {ty-13*s_:.0f},{x:.0f} {ty-17*s_:.0f}"'
                  f' stroke="{f}" stroke-width="{2.4*s_:.1f}" fill="none" stroke-linecap="round"/>')
        else:
            ex, ey = x + a * 17 * s_, ty + dy * s_
            o += (f'<path d="M{x-s_:.0f} {ty:.0f} Q{x+a*10*s_:.0f} {ty-13*s_*k:.0f},{ex:.0f} {ey:.0f}"'
                  f' stroke="{f}" stroke-width="{2.4*s_:.1f}" fill="none" stroke-linecap="round"/>')
    return o


def poly(pts, f, edge=None, sw=1.6, op=1.0):
    d = 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in pts) + ' Z'
    s = f'<path d="{d}" fill="{f}" opacity="{op}"'
    if edge:
        s += f' stroke="{edge}" stroke-width="{sw}" stroke-linejoin="round"'
    return s + '/>'


def mount(uid, pts, fill, facets='', edge=None, sw=2.0):
    """Tog' silueti + ichiga QIRQILGAN yorug' yonbag'irlar.

    Facet'lar clipPath bilan cheklanadi, shuning uchun ular hech qachon
    tog'dan tashqariga chiqib "osilib qolgan" shakl hosil qilmaydi.
    """
    d = 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in pts) + ' Z'
    o = f'<defs><clipPath id="{uid}"><path d="{d}"/></clipPath></defs>'
    o += f'<path d="{d}" fill="{fill}"/>'
    if facets:
        o += f'<g clip-path="url(#{uid})">{facets}</g>'
    if edge:
        o += (f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="{sw}"'
              f' stroke-linejoin="round"/>')
    return o


def face(ax, ay, x1, x2, fill):
    """Cho'qqidan pastga tushuvchi yorug' yonbag'ir.

    Uchburchak kadr tagigacha cho'ziladi va mount() clip'i uni tog'ning
    haqiqiy chetiga qarab kesadi - shuning uchun "osilib qolgan romb" chiqmaydi.
    """
    return poly([(ax, ay), (x1, 420), (x2, 420)], fill)


def ground(p):
    return box(0, GND, W, H - GND, p.gnd)


def glowpatch(cx, cy, rx, ry, p, op=.16):
    """Yumshoq yorug'lik dog'i - radial gradient bilan (chekkasi ko'rinmaydi)."""
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"'
            f' fill="url(#{p.uid}g)" opacity="{op*2.2:.2f}"/>')


# ------------------------------------------------------------------- scenes
def s_nabawi(p, uid):
    """Masjid un-Nabaviy: yashil gumbaz + minoralar."""
    o = poly([(0, GND), (0, 198), (W, 190), (W, GND)], p.far)
    o += glowpatch(400, 150, 150, 90, p, .13)
    o += box(110, 170, 580, GND - 170, p.sil)                    # asosiy bino
    for x in range(150, 660, 66):                                # tomdagi gumbazlar
        o += dome(x, 170, 19, 23, p.sil, p.acc, 1.1)
    o += box(334, 138, 132, 34, p.sil)                           # baraban
    o += glowpatch(400, 104, 80, 62, p, .20)
    o += dome(400, 140, 57, 74, '#5fbf92', '#bff0d6', 2.0)       # yashil gumbaz
    o += minaret(78, GND, 182, 19, p)
    o += minaret(722, GND, 182, 19, p)
    o += minaret(178, GND, 142, 14, p)
    o += minaret(622, GND, 142, 14, p)
    o += arch(400, GND, 46, 56, p.dark, p.acc, 1.5)
    return o + ground(p)


def s_ravza(p, uid):
    """Ravza: ravoqli ayvon, ichkaridan yorug'lik."""
    o = glowpatch(400, GND - 10, 260, 96, p, .17)
    # devor bir butun: ravoqlar undan "kesib" olinadi
    o = (f'<defs><mask id="{uid}"><rect width="{W}" height="{H}" fill="#fff"/>'
         + ''.join(arch(x, GND + 2, w, h, '#000')
                   for x, w, h in ((160, 128, 112), (400, 164, 142), (640, 128, 112)))
         + '</mask></defs>') + o
    for x, w, h in ((160, 128, 112), (400, 164, 142), (640, 128, 112)):
        o += arch(x, GND, w, h, '#0a0e15')                        # ravoq ichi
        o += arch(x, GND, w * 0.6, h * 0.70, p.glow, None, 0, .13)
    o += f'<g mask="url(#{uid})">'
    o += box(0, 104, W, GND - 104, p.sil)                          # devor
    for x in range(12, W, 44):
        o += box(x, 86, 24, 20, p.sil)                             # kungura
    o += '</g>'
    for x, w, h in ((160, 128, 112), (400, 164, 142), (640, 128, 112)):
        o += arch(x, GND, w, h, 'none', p.acc, 2.0)                # ravoq chizig'i
    o += minaret(50, GND, 162, 15, p)
    o += minaret(750, GND, 162, 15, p)
    return o


def s_baqiy(p, uid):
    """Jannatul Baqiy: sodda, belgisiz qabr toshlari."""
    o = poly([(0, 158), (0, 120), (230, 104), (500, 116), (W, 100), (W, 158)], p.far)
    o += f'<circle cx="682" cy="50" r="20" fill="{p.glow}" opacity=".6"/>'
    o += f'<circle cx="673" cy="45" r="20" fill="#0a1120"/>'        # yarim oy
    for x, s_ in ((78, 1.35), (726, 1.2)):
        o += palm(x, 156, s_, p.dark)
    o += box(0, 152, W, 8, '#1d2836')                               # past devor
    o += box(0, 160, W, H - 160, p.gnd)                             # qabriston yeri
    # uch qator belgisiz tosh: orqadan oldinga kattalashadi va yorishadi
    for row, (y, sc, col) in enumerate(((182, .95, '#1f2a38'),
                                        (212, 1.35, '#283442'),
                                        (250, 1.85, '#313e4e'))):
        w, h = 12 * sc, 22 * sc
        step = w * 3.6
        for i in range(int(W / step) + 2):
            x = i * step + (row % 2) * step / 2 - step / 2
            o += (f'<rect x="{x:.0f}" y="{y-h:.0f}" width="{w:.0f}" height="{h:.0f}"'
                  f' rx="{w/2:.0f}" fill="{col}"/>')
            o += (f'<rect x="{x:.0f}" y="{y-h:.0f}" width="{w*0.30:.0f}"'
                  f' height="{h:.0f}" rx="{w*0.15:.0f}" fill="{p.acc}"'
                  f' opacity="{.07+row*.05:.2f}"/>')
    return o


def s_uhud(p, uid):
    """Uhud tizmasi + oldindagi kichkina kamonchilar tepaligi."""
    ridge = [(0, GND), (120, 150), (238, 88), (330, 46), (424, 86), (516, 58),
             (648, 120), (W, 172), (W, GND)]
    facets = (face(330, 46, 330, 470, '#212d3d')      # cho'qqining yorug' yoni
              + face(516, 58, 516, 620, '#1b2735')
              + face(120, 150, 120, 300, '#1c2938'))
    o = mount(uid, ridge, '#17212f', facets)
    # ellik kamonchi turgan past tepalik - qasddan kichik
    o += poly([(70, GND), (150, 178), (238, 194), (312, GND)], p.sil, p.acc, 2.2)
    return o + ground(p)


def s_quba(p, uid):
    """Quba masjidi: bitta gumbaz, minora, xurmolar."""
    o = poly([(0, GND), (0, 196), (W, 188), (W, GND)], p.far)
    o += glowpatch(386, 158, 96, 56, p, .13)
    o += box(248, 168, 292, GND - 168, p.sil)
    o += box(346, 142, 82, 28, p.sil)
    o += dome(387, 144, 41, 56, p.sil, p.acc, 2.0)
    for x in (288, 486):
        o += dome(x, 168, 20, 24, p.sil, p.acc, 1.2)
    o += minaret(596, GND, 152, 16, p)
    o += arch(387, GND, 44, 54, p.dark, p.acc, 1.5)
    for x, s_ in ((116, 1.45), (704, 1.3), (186, 1.0)):
        o += palm(x, 198, s_, p.sil)
    return o + ground(p)


def s_qiblatayn(p, uid):
    """Qiblatayn: ikki gumbaz + qibla burilishi."""
    o = poly([(0, GND), (0, 194), (W, 186), (W, GND)], p.far)
    o += (f'<path d="M400 126 L166 58" stroke="{p.acc}" stroke-width="2" opacity=".3"'
          f' stroke-dasharray="7 7" fill="none"/>')
    o += f'<path d="M400 126 L656 62" stroke="{p.acc}" stroke-width="2.6" opacity=".85" fill="none"/>'
    o += (f'<path d="M656 62 l-16 -3 m16 3 l-13 9" stroke="{p.acc}" stroke-width="2.6"'
          f' opacity=".85" fill="none" stroke-linecap="round"/>')
    o += (f'<path d="M236 92 A180 180 0 0 1 592 78" fill="none" stroke="{p.acc}"'
          f' stroke-width="1.6" opacity=".35" stroke-dasharray="4 8"/>')
    o += box(250, 162, 300, GND - 162, p.sil)
    for x in (326, 474):
        o += box(x - 30, 138, 60, 24, p.sil)
        o += dome(x, 140, 30, 42, p.sil, p.acc, 1.8)
    o += minaret(180, GND, 156, 15, p)
    o += minaret(620, GND, 156, 15, p)
    o += arch(400, GND, 44, 52, p.dark, p.acc, 1.5)
    return o + ground(p)


def s_xandaq(p, uid):
    """Xandaq: yetti masjid + oldindagi qazilgan handaq."""
    o = poly([(0, 206), (0, 166), (W, 156), (W, 206)], p.far)
    for i, x in enumerate((124, 220, 316, 412, 508, 604, 700)):
        b = 172 - (i % 2) * 6
        o += box(x - 23, b - 2, 46, 40, p.sil)
        o += dome(x, b, 23, 28, p.sil, p.acc, 1.2)
    o += poly([(0, 206), (W, 200), (W, 218), (0, 222)], p.dark)
    # qazilgan xandaq: aniq V kesim, chetlari yoritilgan
    o += poly([(0, 220), (150, 214), (250, 260), (550, 260), (650, 212), (W, 208),
               (W, 260), (0, 260)], '#04070b')
    o += (f'<path d="M0 220 L150 214 L250 260 M{W} 208 L650 212 L550 260"'
          f' fill="none" stroke="{p.acc}" stroke-width="2.4" opacity=".65"'
          f' stroke-linejoin="round"/>')
    o += (f'<path d="M150 214 L250 260 M650 212 L550 260" fill="none" stroke="{p.glow}"'
          f' stroke-width="1.2" opacity=".3"/>')
    return o


def s_zulhulayfa(p, uid):
    """Zulhulayfa: miqot masjidi + chegara ustunlari."""
    o = poly([(0, GND), (0, 198), (W, 192), (W, GND)], p.far)
    o += glowpatch(400, 168, 110, 52, p, .11)
    o += box(300, 170, 200, GND - 170, p.sil)
    o += box(364, 146, 72, 24, p.sil)
    o += dome(400, 148, 36, 48, p.sil, p.acc, 1.9)
    o += minaret(548, GND, 146, 15, p)
    o += arch(400, GND, 42, 50, p.dark, p.acc, 1.5)
    for x in (96, 168, 660, 732):
        o += box(x - 5, GND - 54, 10, 54, p.sil)
        o += f'<circle cx="{x}" cy="{GND-60}" r="5" fill="{p.acc}" opacity=".75"/>'
    o += (f'<path d="M60 {GND-26} H740" stroke="{p.acc}" stroke-width="1.8"'
          f' opacity=".32" stroke-dasharray="10 10" fill="none"/>')
    return o + ground(p)


def s_kaaba(p, uid):
    """Ka'ba: kiswa kamari, Hajarul asvad, tavof doiralari."""
    o = glowpatch(400, GND - 4, 300, 74, p, .12)
    for rx, op in ((300, .28), (232, .2), (162, .14)):
        o += (f'<ellipse cx="400" cy="{GND-4}" rx="{rx}" ry="{rx*0.23:.0f}" fill="none"'
              f' stroke="{p.acc}" stroke-width="1.6" opacity="{op}"/>')
    o += poly([(320, 212), (320, 70), (400, 50), (480, 70), (480, 212), (400, 228)], '#080c12')
    o += poly([(320, 70), (400, 50), (400, 228), (320, 212)], '#101823')
    o += (f'<path d="M320 116 L400 96 L480 116" fill="none" stroke="{p.acc}"'
          f' stroke-width="8" opacity=".95"/>')
    o += (f'<path d="M320 130 L400 110 L480 130" fill="none" stroke="{p.acc}"'
          f' stroke-width="1.6" opacity=".38"/>')
    o += box(442, 142, 26, 68, p.acc)                             # eshik
    o += f'<circle cx="324" cy="152" r="10" fill="{p.acc}"/>'      # Hajarul asvad
    o += (f'<circle cx="324" cy="152" r="18" fill="none" stroke="{p.acc}"'
          f' stroke-width="2" opacity=".45"/>')
    return o


def s_maqam(p, uid):
    """Maqomi Ibrohim: shishali gumbazli kichik ravoq + oyoq izi."""
    o = glowpatch(400, GND, 200, 42, p, .11)
    o += box(318, 198, 164, 16, p.sil)
    o += box(340, 182, 120, 18, p.sil)
    for x in (354, 400, 446):
        o += box(x - 5, 118, 10, 64, p.sil)
    o += f'<ellipse cx="400" cy="152" rx="44" ry="32" fill="{p.acc}" opacity=".12"/>'
    o += box(332, 104, 136, 14, p.sil)
    o += dome(400, 106, 50, 64, p.sil, p.acc, 2.0)
    o += f'<ellipse cx="383" cy="168" rx="9" ry="15" fill="{p.acc}" opacity=".6"/>'
    o += f'<ellipse cx="415" cy="168" rx="9" ry="15" fill="{p.acc}" opacity=".6"/>'
    return o + ground(p)


def s_hijr(p, uid):
    """Hijr Ismoil: yarim doira devor + Ka'ba burchagi."""
    o = glowpatch(400, GND, 290, 52, p, .10)
    o += poly([(548, 200), (548, 62), (632, 42), (716, 62), (716, 200), (632, 216)], '#080c12')
    o += poly([(548, 62), (632, 42), (632, 216), (548, 200)], '#101823')
    o += (f'<path d="M548 106 L632 86 L716 106" fill="none" stroke="{p.acc}"'
          f' stroke-width="7" opacity=".92"/>')
    o += (f'<path d="M548 198 A152 116 0 1 0 548 96" fill="{p.acc}" opacity=".07"/>')
    o += (f'<path d="M548 198 A152 116 0 1 0 548 96" fill="none" stroke="{p.sil}"'
          f' stroke-width="18" stroke-linecap="round"/>')
    o += (f'<path d="M548 198 A152 116 0 1 0 548 96" fill="none" stroke="{p.acc}"'
          f' stroke-width="1.8" opacity=".5"/>')
    return o + ground(p)


def s_zamzam(p, uid):
    """Zamzam: yer ostidagi quduq va suv."""
    o = box(0, 152, W, H - 152, '#090d13')
    o += box(0, 146, W, 7, p.sil)
    o += poly([(350, 152), (450, 152), (438, 252), (362, 252)], '#04070b')
    o += (f'<path d="M350 152 L362 252 M450 152 L438 252" stroke="{p.acc}"'
          f' stroke-width="2" opacity=".55" fill="none"/>')
    for i, y in enumerate((218, 230, 242)):
        w = 32 - i * 4
        o += (f'<path d="M{400-w*1.5:.0f} {y} q{w/2:.0f} 8 {w:.0f} 0 q{w/2:.0f} -8 {w:.0f} 0'
              f' q{w/2:.0f} 8 {w:.0f} 0" fill="none" stroke="{p.acc}"'
              f' stroke-width="2.4" opacity="{.9-i*.24:.2f}"/>')
    o += arch(400, 146, 104, 82, p.sil, p.acc, 2.0)
    o += arch(400, 146, 62, 52, '#0a0e15', None, 0)
    for x, s_ in ((124, 1.35), (676, 1.2)):
        o += palm(x, 148, s_, p.sil)
    return o


def s_safo(p, uid):
    """Safo: chapdagi qoyali tepalik, yo'l o'ngga ketadi."""
    o = poly([(0, 200), (0, 150), (120, 120), (250, 142), (420, 128), (560, 150),
              (W, 138), (W, 200)], p.far)
    hill = [(0, GND), (0, 176), (68, 132), (150, 118), (232, 150), (286, GND)]
    o += mount(uid, hill, p.sil, face(150, 118, 150, 340, '#31404f'), p.acc, 2.2)
    o += arch(118, GND, 48, 58, '#0a0e15', p.acc, 1.6)
    o += (f'<path d="M300 {GND-12} H756" stroke="{p.acc}" stroke-width="2.6"'
          f' opacity=".45" stroke-dasharray="14 12" fill="none"/>')
    o += (f'<path d="M726 {GND-24} l22 12 l-22 12" fill="none" stroke="{p.acc}"'
          f' stroke-width="2.6" opacity=".8" stroke-linecap="round" stroke-linejoin="round"/>')
    return o + ground(p)


def s_marva(p, uid):
    """Marva: o'ngdagi tepalik, yo'l chapga qaytadi (sa'yning ikkinchi uchi)."""
    o = poly([(W, 200), (W, 150), (680, 120), (550, 142), (380, 128), (240, 150),
              (0, 138), (0, 200)], p.far)
    hill = [(W, GND), (W, 176), (732, 132), (650, 118), (568, 150), (514, GND)]
    o += mount(uid, hill, p.sil, face(650, 118, 650, 460, '#31404f'), p.acc, 2.2)
    o += arch(682, GND, 48, 58, '#0a0e15', p.acc, 1.6)
    o += (f'<path d="M44 {GND-12} H500" stroke="{p.acc}" stroke-width="2.6"'
          f' opacity=".45" stroke-dasharray="14 12" fill="none"/>')
    o += (f'<path d="M74 {GND-24} l-22 12 l22 12" fill="none" stroke="{p.acc}"'
          f' stroke-width="2.6" opacity=".8" stroke-linecap="round" stroke-linejoin="round"/>')
    return o + ground(p)


def s_hiro(p, uid):
    """Hiro: Jabal un-Nur cho'qqisi, tepadagi g'or, tik so'qmoq."""
    o = poly([(0, 210), (0, 168), (150, 140), (330, 156), (520, 132), (680, 156),
              (W, 140), (W, 210)], p.far)
    peak = [(46, GND), (196, 148), (312, 92), (382, 34), (452, 74), (520, 56),
            (610, 124), (764, GND)]
    o += mount(uid, peak, p.sil,
               face(382, 34, 382, 660, '#31404f')
               + face(520, 56, 520, 700, '#283443'))
    o += glowpatch(400, 88, 34, 26, p, .26)
    o += (f'<path d="M384 104 q0 -30 17 -30 q17 0 17 30 Z" fill="#04070b"'
          f' stroke="{p.acc}" stroke-width="2.2" stroke-linejoin="round"/>')
    o += (f'<path d="M401 106 C432 142,318 168,262 {GND-2}" fill="none" stroke="{p.acc}"'
          f' stroke-width="1.8" opacity=".4" stroke-dasharray="6 9"/>')
    return o + ground(p)


def s_savr(p, uid):
    """Savr: yumaloq tog', pastdagi g'or, janubga yo'nalish."""
    o = poly([(0, 206), (0, 172), (180, 150), (420, 164), (640, 146), (W, 162),
              (W, 206)], p.far)
    peak = [(0, GND), (104, 176), (244, 106), (400, 68), (560, 100), (700, 166),
            (W, GND)]
    o += mount(uid, peak, p.sil, face(400, 68, 400, 760, '#31404f'))
    o += glowpatch(400, GND - 20, 30, 22, p, .18)
    o += (f'<path d="M368 {GND-2} q0 -50 32 -50 q32 0 32 50 Z" fill="#04070b"'
          f' stroke="{p.acc}" stroke-width="2.2" stroke-linejoin="round"/>')
    return o + ground(p)


def s_mina(p, uid):
    """Mino: tartibli chodir qatorlari + jamarat ustuni."""
    o = poly([(0, 172), (0, 132), (190, 96), (400, 124), (620, 90), (W, 138), (W, 172)], p.far)
    o += box(0, 168, W, H - 168, p.gnd)                             # vodiy tubi
    o += box(386, 68, 28, 90, p.sil, p.acc, 2.0)                    # jamarat
    o += glowpatch(400, 150, 70, 26, p, .12)
    for row, (y, sc, col) in enumerate(((188, .74, '#1e2937'), (216, 1.0, '#26313f'),
                                        (252, 1.4, '#2e3a4a'))):
        w, h = 44 * sc, 36 * sc
        step = w * 1.95                                             # chodirlar orasi ochiq
        for i in range(int(W / step) + 2):
            x = i * step + (row % 2) * step / 2 - step / 2
            o += (f'<path d="M{x-w/2:.0f} {y:.0f} L{x:.0f} {y-h:.0f} L{x+w/2:.0f} {y:.0f} Z"'
                  f' fill="{col}" stroke="{p.acc}" stroke-width="1.4"'
                  f' stroke-opacity="{.22+row*.12:.2f}" stroke-linejoin="round"/>')
            o += (f'<path d="M{x:.0f} {y-h:.0f} L{x-w/2:.0f} {y:.0f} L{x-w*0.16:.0f} {y:.0f} Z"'
                  f' fill="{p.acc}" opacity="{.05+row*.03:.2f}"/>')
    return o


def s_arafat(p, uid):
    """Arafot: keng tekislik + Jabal Rahma ustuni."""
    o = poly([(0, 196), (0, 168), (210, 152), (430, 166), (640, 150), (W, 164),
              (W, 196)], p.far)
    o += box(0, 192, W, H - 192, p.gnd)
    hill = [(268, GND), (338, 130), (400, 98), (466, 130), (536, GND)]
    o += mount(uid, hill, p.sil, face(400, 98, 400, 620, '#31404f'), p.acc, 2.2)
    o += glowpatch(400, 74, 54, 40, p, .15)
    o += box(392, 50, 15, 50, p.sil, p.acc, 2.0)                    # Jabal Rahma ustuni
    for i in range(4):                                              # tekislikdagi olomon
        y = 226 + i * 9
        o += (f'<path d="M0 {y} H800" stroke="{p.acc}" stroke-width="{1.2+i*0.2:.1f}"'
              f' opacity="{.05+i*.02:.2f}" stroke-dasharray="{7+i*5} {12+i*3}" fill="none"/>')
    return o


def s_muzdalifa(p, uid):
    """Muzdalifa: bino yo'q - ochiq osmon va toshlar."""
    o = box(0, 198, W, H - 198, '#080b11')
    o += poly([(0, 198), (140, 176), (300, 188), (470, 172), (640, 186), (W, 170),
               (W, 198)], p.far)
    o += f'<path d="M0 198 H800" stroke="{p.sil}" stroke-width="3" fill="none"/>'
    r = random.Random(19)
    for _ in range(52):
        x, y = r.uniform(0, W), r.uniform(206, 256)
        rr = r.uniform(1.7, 3.8)
        o += (f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rr:.1f}" ry="{rr*0.6:.1f}"'
              f' fill="{p.acc}" opacity="{r.uniform(.22,.6):.2f}"/>')
    return o


def s_mualla(p, uid):
    """Jannatul Mualla: tog' bag'ridagi zinapoyali qabriston."""
    o = poly([(0, 210), (0, 118), (180, 64), (370, 104), (566, 58), (W, 110), (W, 210)], p.far)
    o += f'<circle cx="706" cy="46" r="18" fill="{p.glow}" opacity=".5"/>'
    o += f'<circle cx="698" cy="42" r="18" fill="#0c1320"/>'         # yarim oy
    # tog' bag'ridagi zinapoyalar: har biri to'la blok, ustida qabr toshlari
    for i, (y, col) in enumerate(((150, '#1b2532'), (186, '#232e3c'), (230, '#2b3644'))):
        o += f'<rect x="0" y="{y}" width="{W}" height="{H-y}" fill="{col}"/>'
        o += (f'<path d="M0 {y} H{W}" stroke="{p.acc}" stroke-width="1.6"'
              f' opacity="{.12+i*.06:.2f}"/>')
        sc = .85 + i * .4
        w, h = 10 * sc, 16 * sc
        step = w * 4.6
        for j in range(int(W / step) + 2):
            x = j * step + (i % 2) * step / 2 - step / 2
            o += (f'<rect x="{x:.0f}" y="{y-h:.0f}" width="{w:.0f}" height="{h:.0f}"'
                  f' rx="{w/2:.0f}" fill="{"#33404f" if i else "#242f3d"}"/>')
    return o


def s_mawlid(p, uid):
    """Tug'ilgan joy: hozir kutubxona - ravoqli bino."""
    o = poly([(0, GND), (0, 152), (W, 144), (W, GND)], p.far)
    for x, w, h_ in ((30, 92, 72), (140, 68, 48), (626, 84, 58), (724, 68, 78)):
        o += box(x, GND - h_, w, h_, p.dark)
    o += box(268, 122, 264, GND - 122, p.sil)
    o += box(254, 112, 292, 14, p.sil)
    for i in range(5):
        o += arch(292 + i * 54, 192, 34, 44, p.dark, p.acc, 1.4)
    o += arch(400, GND, 46, 56, p.dark, p.acc, 1.6)
    o += glowpatch(400, 178, 130, 62, p, .09)
    return o + ground(p)


def s_shib(p, uid):
    """Shi'b Abi Tolib: ikki qoya orasidagi tor dara."""
    # osmon faqat tepadagi tor tirqishda ko'rinadi
    o = f'<rect width="{W}" height="{H}" fill="#070c15"/>'
    o += starfield(220, 26, 120)
    o += glowpatch(400, 4, 88, 26, p, .07)
    o += poly([(0, 0), (262, 0), (322, 68), (292, 140), (344, 202), (322, 260), (0, 260)], p.dark)
    o += poly([(W, 0), (538, 0), (478, 64), (512, 136), (462, 204), (482, 260), (W, 260)], p.dark)
    o += poly([(0, 0), (238, 0), (292, 74), (262, 152), (306, 260), (0, 260)], p.sil)
    o += poly([(W, 0), (562, 0), (508, 70), (540, 150), (500, 260), (W, 260)], p.sil)
    o += (f'<path d="M292 74 L262 152 L306 260" fill="none" stroke="{p.acc}"'
          f' stroke-width="1.8" opacity=".3"/>')
    o += (f'<path d="M508 70 L540 150 L500 260" fill="none" stroke="{p.acc}"'
          f' stroke-width="1.8" opacity=".3"/>')
    return o


SCENES = {
    'nabawi': s_nabawi, 'ravza': s_ravza, 'baqiy': s_baqiy, 'uhud': s_uhud,
    'quba': s_quba, 'qiblatayn': s_qiblatayn, 'xandaq': s_xandaq,
    'zulhulayfa': s_zulhulayfa, 'kaaba': s_kaaba, 'maqam': s_maqam, 'hijr': s_hijr,
    'zamzam': s_zamzam, 'safo': s_safo, 'marva': s_marva, 'hiro': s_hiro,
    'savr': s_savr, 'mina': s_mina, 'arafat': s_arafat, 'muzdalifa': s_muzdalifa,
    'mualla': s_mualla, 'mawlid': s_mawlid, 'shib': s_shib,
}

CARD_SCENE = {
    1: 'nabawi', 2: 'ravza', 3: 'baqiy', 4: 'uhud', 5: 'quba', 6: 'qiblatayn',
    7: 'xandaq', 8: 'zulhulayfa', 9: 'kaaba', 10: 'maqam', 11: 'hijr', 12: 'zamzam',
    13: 'safo', 14: 'marva', 15: 'hiro', 16: 'savr', 17: 'mina', 18: 'arafat',
    19: 'muzdalifa', 20: 'mualla', 21: 'mawlid', 22: 'shib',
}


def starfield(seed, n=52, ymax=196):
    r = random.Random(seed * 977 + 5)
    out = []
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(2, ymax)
        rr = r.choice((0.7, 0.9, 1.1, 1.4, 1.9))
        op = r.uniform(.2, .85) * (1 - y / (ymax * 1.6))
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr}" fill="#e8eefc"'
                   f' opacity="{max(op,.08):.2f}"/>')
    return ''.join(out)


def scene_svg(num, city):
    """Karta uchun to'liq inline SVG (tashqi bog'liqliksiz)."""
    uid = f'sc{num}'
    p = P(city, uid)
    body = (
        f'<defs><linearGradient id="{uid}s" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#070b13"/>'
        f'<stop offset=".55" stop-color="#0c1420"/>'
        f'<stop offset="1" stop-color="#121b28"/></linearGradient>'
        f'<radialGradient id="{uid}h" cx=".5" cy="1" r=".85">'
        f'<stop offset="0" stop-color="{p.glow}" stop-opacity=".18"/>'
        f'<stop offset="1" stop-color="{p.glow}" stop-opacity="0"/></radialGradient><radialGradient id="{uid}g" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{p.glow}" stop-opacity=".55"/><stop offset=".6" stop-color="{p.glow}" stop-opacity=".2"/><stop offset="1" stop-color="{p.glow}" stop-opacity="0"/></radialGradient></defs>'
        f'<rect width="{W}" height="{H}" fill="url(#{uid}s)"/>'
        f'{starfield(num)}'
        f'<rect width="{W}" height="{H}" fill="url(#{uid}h)"/>'
    )
    body += SCENES[CARD_SCENE[num]](p, uid)
    return (f'<svg class="art" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice"'
            f' xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true"'
            f' focusable="false">{body}</svg>')
