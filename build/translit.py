#!/usr/bin/env python3
"""O'zbek lotin -> kirill transliteratsiyasi.

Faqat yozuv o'zgaradi, matn o'zgarmaydi: so'zlar, tartib, tinish belgilari
bir xil qoladi. Arab yozuvi, raqamlar va ﷺ belgisi tegilmaydi.

Qoidalar:
  o' -> ў      g' -> ғ      sh -> ш      ch -> ч
  ya -> я      yo -> ё      yu -> ю      ye -> е
  e  -> э (so'z boshida yoki unlidan keyin), aks holda е
  '  -> ъ (tutuq belgisi)
  h  -> ҳ      x -> х       q -> қ       j -> ж
"""

APOS = "'‘’ʻʼ`´"

ONE = {
    'a': 'а', 'b': 'б', 'c': 'с', 'd': 'д', 'f': 'ф', 'g': 'г', 'h': 'ҳ',
    'i': 'и', 'j': 'ж', 'k': 'к', 'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о',
    'p': 'п', 'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у', 'v': 'в',
    'w': 'в', 'x': 'х', 'y': 'й', 'z': 'з',
}
DIG = {"o'": 'ў', "g'": 'ғ', 'sh': 'ш', 'ch': 'ч'}
YOD = {'ya': 'я', 'yo': 'ё', 'yu': 'ю', 'ye': 'е'}
VOWELS = set('aeiou')


def _case(src, out):
    """Manba bosh harf bo'lsa, natijani ham bosh harf qiladi."""
    return out.upper() if src[0].isupper() else out


def is_latin_letter(ch):
    return ch.isalpha() and ch.isascii()


def to_cyrillic(s):
    out = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        low = ch.lower()

        # --- o' va g' (apostrof variantlari bilan) ---
        if low in ('o', 'g') and i + 1 < n and s[i + 1] in APOS:
            out.append(_case(ch, DIG[low + "'"]))
            i += 2
            continue

        # --- sh, ch ---
        if i + 1 < n:
            two = (ch + s[i + 1]).lower()
            if two in ('sh', 'ch'):
                out.append(_case(ch, DIG[two]))
                i += 2
                continue

        # --- ya / yo / yu / ye ---
        if low == 'y' and i + 1 < n:
            nx = s[i + 1].lower()
            # "yo'q" = y + o' -> йў, shuning uchun apostrofni tekshiramiz
            follows_apos = i + 2 < n and s[i + 2] in APOS
            if nx in 'aoue' and not (nx in ('o', 'g') and follows_apos):
                out.append(_case(ch, YOD['y' + nx]))
                i += 2
                continue

        # --- tutuq belgisi ---
        if ch in APOS:
            out.append('ъ')
            i += 1
            continue

        # --- e: so'z boshida yoki unlidan keyin -> э ---
        if low == 'e':
            prev = s[i - 1] if i else ''
            start = (not prev) or (not is_latin_letter(prev))
            after_vowel = prev.lower() in VOWELS if prev else False
            out.append(_case(ch, 'э' if (start or after_vowel) else 'е'))
            i += 1
            continue

        if low in ONE:
            out.append(_case(ch, ONE[low]))
            i += 1
            continue

        out.append(ch)          # raqam, arab yozuvi, tinish belgisi, ﷺ
        i += 1
    return ''.join(out)


if __name__ == '__main__':
    import sys
    for line in sys.stdin:
        sys.stdout.write(to_cyrillic(line))
