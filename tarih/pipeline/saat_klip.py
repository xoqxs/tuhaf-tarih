"""Saat animasyonu klipleri (1080x1920, 30 fps) — anma/özel videolar için.

python3 saat_klip.py cep    CIKIS.mp4 --sure 5 [--arka foto.jpg]   cep saati, saniye ibresi tıklar
python3 saat_klip.py kirik  CIKIS.mp4 --sure 5 [--arka foto.jpg]   aynı saat: darbe, parlama, çatlaklar, ibre durur
python3 saat_klip.py 0905   CIKIS.mp4 --sure 6 [--arka foto.jpg]   ibreler 09.05'e gelir ve durur
Kareler PIL ile çizilir, ffmpeg'e ham olarak aktarılır (tek kodlama).
"""
import argparse, math, os, random, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import FONT_DIR
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H, FPS = 1080, 1920, 30
SS = 2                      # saat 2x çizilip küçültülür (kenar yumuşatma)
CX, CY = W // 2, 880


def arka_plan(yol, koyuluk=0.30):
    if yol and os.path.exists(yol):
        im = ImageOps.grayscale(Image.open(yol)).convert("RGB")
        s = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
        x = (im.width - W) // 2; y = int((im.height - H) * 0.3)
        im = im.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(14))
        im = im.point(lambda v: int(v * koyuluk))
    else:
        im = Image.new("RGB", (W, H), (9, 9, 10))
    # merkezde hafif ışık, kenarlarda karartma
    isik = Image.new("L", (W, H), 0)
    ImageDraw.Draw(isik).ellipse((CX - 620, CY - 620, CX + 620, CY + 620), fill=70)
    isik = isik.filter(ImageFilter.GaussianBlur(220))
    im = Image.composite(Image.new("RGB", (W, H), (58, 50, 40)), im, isik)
    return im


def kadran(R, tur="cep"):
    """İbresiz saat gövdesi (RGBA, 2x). R: yarıçap (1x)."""
    r = R * SS; pad = int(r * 0.42); n = 2 * (r + pad)
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = n // 2
    if tur == "cep":
        # halka (askı) ve kurma kolu
        d.ellipse((c - r * 0.20, c - r * 1.40, c + r * 0.20, c - r * 1.02), outline=(196, 160, 78, 255), width=int(r * 0.045))
        d.rounded_rectangle((c - r * 0.085, c - r * 1.13, c + r * 0.085, c - r * 0.97), radius=int(r * 0.03), fill=(170, 136, 60, 255))
        # altın kasa: dıştan içe ton geçişi
        for i, (oran, renk) in enumerate([(1.00, (120, 92, 36)), (0.985, (214, 180, 96)), (0.955, (246, 222, 150)),
                                          (0.93, (190, 152, 70)), (0.905, (116, 88, 34))]):
            rr = r * oran; d.ellipse((c - rr, c - rr, c + rr, c + rr), fill=renk + (255,))
        yuz, cizgi = (244, 236, 214, 255), (38, 30, 22, 255)
    else:
        for oran, renk in [(1.00, (14, 14, 15)), (0.985, (220, 220, 220)), (0.965, (30, 30, 32))]:
            rr = r * oran; d.ellipse((c - rr, c - rr, c + rr, c + rr), fill=renk + (255,))
        yuz, cizgi = (243, 241, 236, 255), (18, 18, 20, 255)
    rf = r * 0.885
    d.ellipse((c - rf, c - rf, c + rf, c + rf), fill=yuz)
    # hafif iç gölge
    golge = Image.new("L", (n, n), 0); gd = ImageDraw.Draw(golge)
    gd.ellipse((c - rf, c - rf, c + rf, c + rf), outline=120, width=int(r * 0.06))
    golge = golge.filter(ImageFilter.GaussianBlur(r * 0.03))
    im = Image.composite(Image.new("RGBA", (n, n), (60, 44, 20, 255)), im, golge.point(lambda v: v // 2))
    d = ImageDraw.Draw(im)
    # dakika çizgileri
    for k in range(60):
        a = math.radians(k * 6 - 90)
        r1 = rf * (0.86 if k % 5 == 0 else 0.92); r2 = rf * 0.965
        w = int(r * (0.022 if k % 5 == 0 else 0.008))
        d.line((c + r1 * math.cos(a), c + r1 * math.sin(a), c + r2 * math.cos(a), c + r2 * math.sin(a)), fill=cizgi, width=max(2, w))
    # rakamlar
    f = ImageFont.truetype(os.path.join(FONT_DIR, "Oswald.ttf"), int(r * 0.17))
    rakamlar = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"] if tur == "cep" else [str(x) for x in [12] + list(range(1, 12))]
    for k, t in enumerate(rakamlar):
        a = math.radians(k * 30 - 90); rr = rf * 0.70
        bb = d.textbbox((0, 0), t, font=f)
        d.text((c + rr * math.cos(a) - (bb[2] + bb[0]) / 2, c + rr * math.sin(a) - (bb[3] + bb[1]) / 2), t, font=f, fill=cizgi)
    return im


def ibre(d, c, aci_derece, uzunluk, kalinlik, renk, kuyruk=0.0):
    a = math.radians(aci_derece - 90)
    x2, y2 = c + uzunluk * math.cos(a), c + uzunluk * math.sin(a)
    x1, y1 = c - kuyruk * math.cos(a), c - kuyruk * math.sin(a)
    d.line((x1, y1, x2, y2), fill=renk, width=max(2, int(kalinlik)))
    rr = kalinlik / 2
    d.ellipse((x2 - rr, y2 - rr, x2 + rr, y2 + rr), fill=renk)


def saat_ciz(govde, R, saat, dakika, saniye, saniye_renk=(170, 30, 30, 255), catlak=None, karart=1.0):
    im = govde.copy(); d = ImageDraw.Draw(im); c = im.width // 2; r = R * SS
    koyu = (24, 22, 22, 255)
    ibre(d, c, (saat % 12) * 30 + dakika * 0.5, r * 0.47, r * 0.055, koyu, r * 0.06)
    ibre(d, c, dakika * 6 + (saniye or 0) * 0.1, r * 0.70, r * 0.036, koyu, r * 0.08)
    if saniye is not None:
        ibre(d, c, saniye * 6, r * 0.76, r * 0.014, saniye_renk, r * 0.16)
    d.ellipse((c - r * 0.05, c - r * 0.05, c + r * 0.05, c + r * 0.05), fill=koyu)
    d.ellipse((c - r * 0.018, c - r * 0.018, c + r * 0.018, c + r * 0.018), fill=(200, 170, 90, 255))
    if catlak:
        for nokta, kalin in catlak:
            d.line([(c + x * r, c + y * r) for x, y in nokta], fill=(20, 16, 12, 255), width=max(2, int(r * kalin)), joint="curve")
            d.line([(c + x * r + r * 0.006, c + y * r + r * 0.006) for x, y in nokta], fill=(255, 255, 255, 120), width=max(1, int(r * kalin * 0.4)))
    if karart < 1.0:
        im = Image.composite(im, Image.new("RGBA", im.size, (0, 0, 0, 0)), im.split()[3])
        k = Image.new("RGBA", im.size, (0, 0, 0, int(255 * (1 - karart))))
        im = Image.alpha_composite(im, Image.composite(k, Image.new("RGBA", im.size, (0, 0, 0, 0)), im.split()[3]))
    return im


def catlak_uret(tohum=4):
    r = random.Random(tohum); merkez = (0.30, -0.22); out = []
    for i in range(9):
        a = r.uniform(0, 2 * math.pi); x, y = merkez; nokta = [merkez]
        uz = r.uniform(0.35, 1.25)
        for _ in range(r.randint(4, 7)):
            a += r.uniform(-0.55, 0.55); adim = uz / 6
            x += adim * math.cos(a); y += adim * math.sin(a)
            if x * x + y * y > 0.80 ** 2:
                break
            nokta.append((x, y))
        if len(nokta) > 1:
            out.append((nokta, r.uniform(0.006, 0.014)))
    return out, merkez


def yumusak(t):   # ease-out
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mod", choices=["cep", "kirik", "0905"]); ap.add_argument("cikis")
    ap.add_argument("--sure", type=float, default=5.0); ap.add_argument("--arka", default="")
    ap.add_argument("--kare", type=float, default=-1, help="yalnızca bu saniyedeki kareyi PNG olarak yaz (önizleme)")
    a = ap.parse_args()
    arka = arka_plan(a.arka, 0.26 if a.mod != "0905" else 0.20)
    R0 = 330
    govde = kadran(R0, "cep" if a.mod != "0905" else "duvar")
    catlaklar, cm = catlak_uret()
    rs = random.Random(7)
    n = int(a.sure * FPS)

    def kare(i):
        t = i / FPS
        buyume = 1.0 + 0.045 * (t / max(a.sure, 0.1))            # yavaş yaklaşma
        dx = dy = 0; parlama = 0.0; katman = None; halka = 0.0
        if a.mod == "cep":
            sn = math.floor(t) + (0.12 * math.sin(min(1, (t % 1) / 0.12) * math.pi) if (t % 1) < 0.12 else 0)
            katman = saat_ciz(govde, R0, 4, 37, 12 + sn)
        elif a.mod == "kirik":
            t0 = 0.55
            if t < t0:
                katman = saat_ciz(govde, R0, 4, 37, 12 + math.floor(t * 2) / 2)
            else:
                u = t - t0
                kac = max(1, int(len(catlaklar) * min(1, u / 0.18)))
                katman = saat_ciz(govde, R0, 4, 37, 12.5, catlak=catlaklar[:kac], karart=max(0.78, 1 - u * 0.25))
                parlama = max(0.0, 1 - u / 0.28)
                gen = 26 * math.exp(-u * 6)
                dx, dy = int(rs.uniform(-gen, gen)), int(rs.uniform(-gen, gen))
        else:  # 0905
            sweep = 2.2                                           # ibreler bu sürede 09.05'e gelir
            if t < sweep:
                dk = 8 * 60 + 47 + (18) * yumusak(t / sweep)      # 08.47 → 09.05
                sn = (t * 3.0) % 60
                katman = saat_ciz(govde, R0, dk // 60, dk % 60, None)
            else:
                katman = saat_ciz(govde, R0, 9, 5, None)
                halka = min(1.0, (t - sweep) / 1.0)
        boy = int(katman.width / SS * buyume)
        kat = katman.resize((boy, boy), Image.LANCZOS)
        fr = arka.copy()
        # saatin gölgesi
        g = Image.new("L", (boy, boy), 0); g.paste(kat.split()[3].point(lambda v: int(v * 0.55)), (0, 0))
        g = g.filter(ImageFilter.GaussianBlur(26))
        fr.paste((0, 0, 0), (CX - boy // 2 + 14 + dx, CY - boy // 2 + 26 + dy), g)
        fr.paste(kat, (CX - boy // 2 + dx, CY - boy // 2 + dy), kat)
        if halka > 0:   # 09.05'te duran saatin çevresinde kırmızı ince halka
            hd = ImageDraw.Draw(fr, "RGBA"); rr = int(R0 * buyume * 1.09)
            hd.ellipse((CX - rr, CY - rr, CX + rr, CY + rr), outline=(227, 10, 23, int(230 * halka)), width=7)
        if parlama > 0:
            fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 244, 220)), 0.75 * parlama)
        return fr

    if a.kare >= 0:
        kare(int(a.kare * FPS)).save(a.cikis); return
    gecici = a.cikis + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", "-r", str(FPS), gecici], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(kare(i).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg hata")
    os.replace(gecici, a.cikis)
    print("klip", a.mod, a.cikis, f"{a.sure}s")


if __name__ == "__main__":
    main()
