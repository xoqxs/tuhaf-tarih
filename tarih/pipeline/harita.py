#!/usr/bin/env python3
"""Telifsiz harita animasyonu (Natural Earth verisi, kamu malı).

Dünyadan hedef noktaya yakınlaşan dikey klip üretir; hedef ülke vurgulanır,
noktada nabız halkası ve etiket çıkar. İsteğe bağlı --yol ile bir başlangıç
noktasından hedefe kesik çizgi rota çizilir (ör. İsrail → Entebbe).

Kullanım:
  python3 harita.py CIKIS.mp4 --hedef 61.75,59.45 --etiket "Ural Dağları" \
      [--ulke Russia] [--yol 31.9,34.9] [--sure 3.0] [--vurgu "#FF3B30"] [--kare 2.0]
--kare t verilirse yalnızca o andaki kareyi PNG olarak yazar (önizleme).
"""
import argparse, json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import FONT_DIR

VERI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "veri")
W, H, FPS = 1080, 1920, 30


import numpy as np
GENISLIK = None
_yy, _xx = np.mgrid[0:H, 0:W]
_r = np.sqrt(((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H * 0.46) / (H * 0.62)) ** 2)
VINYET = Image.fromarray((np.clip((_r - 0.55) / 0.6, 0, 1) ** 1.6 * 200).astype("uint8"), "L")


def mesafe_km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def merc(lat, lon):
    lat = max(-85.0, min(85.0, lat))
    x = math.radians(lon)
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return x, y


def halkalar(geom):
    t = geom["type"]
    if t == "Polygon":
        return [geom["coordinates"]]
    if t == "MultiPolygon":
        return geom["coordinates"]
    return []


def yukle():
    d = json.load(open(os.path.join(VERI, "ne_50m_admin_0_countries.geojson")))
    ulkeler = []
    for f in d["features"]:
        p = f["properties"]
        adlar = {str(p.get(k, "")).lower() for k in ("NAME", "NAME_EN", "ADMIN", "NAME_TR", "ISO_A3", "SOVEREIGNT") if p.get(k)}
        polys = []
        for poly in halkalar(f["geometry"]):
            ring = poly[0]
            polys.append([merc(la, lo) for lo, la in ring])
        ulkeler.append((adlar, polys))
    return ulkeler


def renk(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def ease(t):
    return t * t * (3 - 2 * t)


def font(boy):
    for f in ("Anton-Regular.ttf", "Oswald-Bold.ttf", "BebasNeue-Regular.ttf"):
        p = os.path.join(FONT_DIR, f)
        if os.path.exists(p):
            return ImageFont.truetype(p, boy)
    return ImageFont.load_default()


def kare(t, sure, ulkeler, hedef, yol, ulke, etiket, vurgu):
    hx, hy = merc(*hedef)
    # ölçek: piksel / mercator birimi. Başlangıç: ~yarım küre, bitiş: ~1200 km genişlik
    s0 = W / 2.2
    son_km = GENISLIK or (max(1500.0, mesafe_km(hedef, yol) * 1.6) if yol else 2500.0)
    s1 = W / (son_km / (6371.0 * max(0.2, math.cos(math.radians(hedef[0])))))
    z = ease(min(1.0, t / (sure * 0.72)))
    s = s0 * (s1 / s0) ** z
    # merkez: başlangıçta hedefle yol arasının ortası, sonra hedef
    if yol:
        yx, yy = merc(*yol)
        cx0, cy0 = (hx + yx) / 2, (hy + yy) / 2
    else:
        cx0, cy0 = hx, hy
    cx = cx0 + (hx - cx0) * z
    cy = cy0 + (hy - cy0) * z

    def P(x, y):
        return (W / 2 + (x - cx) * s, H * 0.46 - (y - cy) * s)

    im = Image.new("RGBA", (W, H), renk("#0B1622"))
    d = ImageDraw.Draw(im, "RGBA")
    kara, sinir, vur = renk("#2A3542"), renk("#45525F"), renk(vurgu, 70)
    vurgulu = []
    for adlar, polys in ulkeler:
        sec = ulke and ulke.lower() in adlar
        for ring in polys:
            pts = [P(x, y) for x, y in ring]
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            if max(xs) < -50 or min(xs) > W + 50 or max(ys) < -50 or min(ys) > H + 50:
                continue
            if len(pts) > 2:
                d.polygon(pts, fill=kara, outline=sinir)
                if sec:
                    vurgulu.append(pts)
    for pts in vurgulu:
        d.polygon(pts, fill=vur)
        d.line(pts + [pts[0]], fill=renk(vurgu, 230), width=5)
    # ızgara hissi: hafif enlem/boylam çizgileri
    for lon in range(-180, 181, 10):
        x, _ = P(*merc(0, lon)); d.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=1)
    for lat in range(-80, 81, 10):
        _, y = P(*merc(lat, 0)); d.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)
    # rota
    tx, ty = P(hx, hy)
    if yol:
        ax, ay = P(*merc(*yol))
        ilerle = min(1.0, t / (sure * 0.55))
        n = 60
        for i in range(int(n * ilerle)):
            if i % 2:
                continue
            a, b = i / n, (i + 1) / n
            d.line([(ax + (tx - ax) * a, ay + (ty - ay) * a), (ax + (tx - ax) * b, ay + (ty - ay) * b)], fill=renk("#FFFFFF", 230), width=6)
        d.ellipse([ax - 10, ay - 10, ax + 10, ay + 10], fill=renk("#FFFFFF"))
    # nabız
    faz = (t * 1.4) % 1.0
    r = 18 + 70 * faz
    d.ellipse([tx - r, ty - r, tx + r, ty + r], outline=renk(vurgu, int(255 * (1 - faz))), width=6)
    d.ellipse([tx - 16, ty - 16, tx + 16, ty + 16], fill=renk(vurgu))
    # etiket
    if etiket and t > sure * 0.55:
        al = min(1.0, (t - sure * 0.55) / 0.35)
        f = font(78)
        metin = etiket.upper().replace("i", "İ")
        bw = d.textlength(metin, font=f)
        x0 = max(40, min(W - bw - 80, tx - bw / 2 - 20)); y0 = ty + 60
        d.rounded_rectangle([x0, y0, x0 + bw + 40, y0 + 110], 14, fill=(0, 0, 0, int(170 * al)))
        d.text((x0 + 20, y0 + 12), metin, font=f, fill=(255, 255, 255, int(255 * al)))
    im = im.convert("RGB")
    return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, VINYET)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cikis")
    ap.add_argument("--hedef", required=True)
    ap.add_argument("--etiket", default="")
    ap.add_argument("--ulke", default="")
    ap.add_argument("--yol", default="")
    ap.add_argument("--sure", type=float, default=3.0)
    ap.add_argument("--vurgu", default="#FF3B30")
    ap.add_argument("--kare", type=float, default=None)
    ap.add_argument("--genislik", type=float, default=None, help="bitişte ekran genişliği (km)")
    a = ap.parse_args()
    hedef = tuple(float(v) for v in a.hedef.split(","))
    yol = tuple(float(v) for v in a.yol.split(",")) if a.yol else None
    global GENISLIK
    GENISLIK = a.genislik
    ulkeler = yukle()
    if a.kare is not None:
        kare(a.kare, a.sure, ulkeler, hedef, yol, a.ulke, a.etiket, a.vurgu).save(a.cikis)
        return
    gecici = a.cikis + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", gecici], stdin=subprocess.PIPE)
    for i in range(int(a.sure * FPS)):
        p.stdin.write(kare(i / FPS, a.sure, ulkeler, hedef, yol, a.ulke, a.etiket, a.vurgu).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(gecici, a.cikis)
        print("TAMAM", a.cikis)
    else:
        sys.exit("ffmpeg hata")


if __name__ == "__main__":
    main()
