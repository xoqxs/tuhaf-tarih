"""Tek bir çekimin dikey karesini hazırlar (1188x2112: kamera hareketi için %10 pay).

Düzenler:
  doldur  : fotoğraf ekranı kaplar (odak noktasına göre kırpılır)
  bulanik : arkada bulanık-karartılmış kopya, önde fotoğrafın tamamı (yatay arşiv fotoğrafları için)
  cerceve : bulanık arka plan + beyaz kenarlı, hafif eğik "eski fotoğraf"
  detay   : fotoğrafın bir bölgesine yakın plan (aynı görsel ikinci kez kullanılırsa)
  kart    : yazı kartı (yıl, sayı, yer adı) — fotoğraf yok
"""
import os, random
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from ortak import FONT_DIR, font_bilgi, palet_bilgi, tr_upper

KW, KH = 1188, 2112


def _cover(im, w, h, fx=0.5, fy=0.5):
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, int(im.width * s + 0.5)), max(h, int(im.height * s + 0.5))), Image.LANCZOS)
    x = int((im.width - w) * fx); y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def _contain(im, w, h):
    s = min(w / im.width, h / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def ton_uygula(im, ton):
    im = im.convert("RGB")
    if ton == "sepya":
        g = ImageOps.grayscale(im)
        im = ImageOps.colorize(g, black="#1c140c", white="#f3e3c3", mid="#8a6a45")
    elif ton == "soguk":
        im = ImageEnhance.Color(im).enhance(0.75)
        r, g, b = im.split(); b = b.point(lambda v: min(255, int(v * 1.08 + 6))); r = r.point(lambda v: int(v * 0.94))
        im = Image.merge("RGB", (r, g, b))
    elif ton == "sicak":
        r, g, b = im.split(); r = r.point(lambda v: min(255, int(v * 1.07 + 5))); b = b.point(lambda v: int(v * 0.9))
        im = Image.merge("RGB", (r, g, b))
    elif ton == "solgun":
        im = ImageEnhance.Color(im).enhance(0.55)
        im = im.point(lambda v: int(18 + v * 0.9))
    elif ton == "kontrast":
        im = ImageEnhance.Contrast(im).enhance(1.25); im = ImageEnhance.Color(im).enhance(1.1)
    return ImageEnhance.Contrast(im).enhance(1.05)


def _bulanik_zemin(im, ton):
    z = _cover(im, KW, KH).filter(ImageFilter.GaussianBlur(38))
    z = ImageEnhance.Brightness(ton_uygula(z, ton)).enhance(0.45)
    return z


def kare_foto(yol, duzen, ton, cikis, odak=(0.5, 0.5), tohum=0):
    r = random.Random(tohum)
    im = Image.open(yol)
    im = ImageOps.exif_transpose(im).convert("RGB")
    if duzen == "doldur":
        out = ton_uygula(_cover(im, KW, KH, *odak), ton)
    elif duzen == "detay":
        z = r.uniform(1.6, 2.1)
        cw, ch = int(im.width / z), int(im.height / z)
        cx = int(odak[0] * im.width); cy = int(odak[1] * im.height)
        x = min(max(0, cx - cw // 2), im.width - cw); y = min(max(0, cy - ch // 2), im.height - ch)
        out = ton_uygula(_cover(im.crop((x, y, x + cw, y + ch)), KW, KH), ton)
    else:
        out = _bulanik_zemin(im, ton)
        on = ton_uygula(im, ton)
        if duzen == "cerceve":
            on = _contain(on, int(KW * 0.84), int(KH * 0.55))
            kenar = 22
            kart = Image.new("RGB", (on.width + 2 * kenar, on.height + 2 * kenar + 40), "#f4efe4")
            kart.paste(on, (kenar, kenar))
            aci = r.uniform(-3.5, 3.5)
            kart = kart.convert("RGBA").rotate(aci, expand=True, resample=Image.BICUBIC)
            golge = Image.new("RGBA", kart.size, (0, 0, 0, 0))
            golge.paste((0, 0, 0, 150), mask=kart.split()[3])
            golge = golge.filter(ImageFilter.GaussianBlur(18))
            x = (KW - kart.width) // 2; y = int(KH * 0.40 - kart.height / 2)
            out.paste(golge, (x + 14, y + 22), golge); out.paste(kart, (x, y), kart)
        else:  # bulanik
            on = _contain(on, int(KW * 0.96), int(KH * 0.62))
            x = (KW - on.width) // 2; y = int(KH * 0.42 - on.height / 2)
            golge = Image.new("RGBA", (on.width + 60, on.height + 60), (0, 0, 0, 0))
            ImageDraw.Draw(golge).rectangle((30, 30, on.width + 30, on.height + 30), fill=(0, 0, 0, 170))
            golge = golge.filter(ImageFilter.GaussianBlur(22))
            out.paste(golge, (x - 30, y - 18), golge); out.paste(on, (x, y))
    out.save(cikis, quality=95)


def _sigdir(draw, metin, font_yolu, max_w, boy):
    while boy > 40:
        f = ImageFont.truetype(font_yolu, boy)
        if draw.textlength(metin, font=f) <= max_w:
            return f
        boy -= 6
    return ImageFont.truetype(font_yolu, boy)


def kare_kart(kart, stil, cikis, tohum=0):
    """kart: {"ust": "ST. LOUIS", "ana": "1904", "alt": "OLİMPİYAT MARATONU"}"""
    r = random.Random(tohum)
    p = palet_bilgi(stil["palet"])
    f = font_bilgi(stil["font"])
    fy = os.path.join(FONT_DIR, f["dosya"])
    taban = Image.new("RGB", (KW, KH), "#0d0d0f")
    # hafif doku + renk ışığı
    isik = Image.new("RGB", (KW, KH), p["etiket"])
    maske = Image.new("L", (KW, KH), 0)
    cx, cy = r.randint(200, KW - 200), r.randint(500, KH - 700)
    ImageDraw.Draw(maske).ellipse((cx - 700, cy - 700, cx + 700, cy + 700), fill=120)
    taban = Image.composite(isik, taban, maske.filter(ImageFilter.GaussianBlur(260)))
    noise = Image.effect_noise((KW, KH), 22).convert("RGB")
    taban = Image.blend(taban, noise, 0.06)
    d = ImageDraw.Draw(taban)
    yukari = lambda s: tr_upper(s) if s else s
    ana = yukari(kart.get("ana", ""))
    fa = _sigdir(d, ana, fy, KW - 160, 420)
    bb = d.textbbox((0, 0), ana, font=fa)
    ah = bb[3] - bb[1]
    y0 = int(KH * 0.40 - ah / 2)
    d.text(((KW - (bb[2] - bb[0])) / 2 - bb[0], y0 - bb[1]), ana, font=fa, fill=p["vurgu"])
    fk = ImageFont.truetype(os.path.join(FONT_DIR, "Oswald.ttf"), 64)
    if kart.get("ust"):
        u = yukari(kart["ust"]); w = d.textlength(u, font=fk)
        d.text(((KW - w) / 2, y0 - 120), u, font=fk, fill="#e9e4da")
        d.line(((KW - w) / 2, y0 - 30, (KW + w) / 2, y0 - 30), fill=p["vurgu"], width=6)
    if kart.get("alt"):
        a = yukari(kart["alt"]); fa2 = _sigdir(d, a, fy, KW - 180, 96)
        w = d.textlength(a, font=fa2)
        d.text(((KW - w) / 2, y0 + ah + 60), a, font=fa2, fill="#ffffff")
    taban.save(cikis, quality=95)
