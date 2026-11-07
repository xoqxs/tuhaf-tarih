"""Haftalık derleme: haftanın Shorts'larını yatay (1920x1080) tek videoda birleştirir.

python3 derleme.py CIKIS.mp4 IS1 IS2 ... [--baslik "Bu Haftanın En Tuhaf Savaş Hikâyeleri"]
IS = tarih/isler/<iş> klasörü (video.json + zaman.json) ; video dosyası tarih/v/<iş>.mp4
Çıktılar: CIKIS.mp4, CIKIS-bolumler.txt (YouTube bölümleri), CIKIS-kapak.jpg (1280x720 küçük resim)
Her Short'un son sahnesi ("Yarın: ..." duyurusu) kesilir; derlemede eski duyurular kalmaz.
"""
import argparse, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import FONT_DIR, oku, run, sure, tr_upper
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BURADA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURADA)
W, H, FPS = 1920, 1080, 30
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2"]


def font(ad, boy):
    return ImageFont.truetype(os.path.join(FONT_DIR, ad), boy)


def sigdir(d, metin, ad, max_w, boy):
    while boy > 30:
        f = font(ad, boy)
        if d.textlength(metin, font=f) <= max_w:
            return f
        boy -= 4
    return font(ad, boy)


def kart_resmi(yol, ust, ana, alt, arka=None, renk="#FFC832"):
    if arka and os.path.exists(arka):
        im = Image.open(arka).convert("RGB")
        s = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1))
        im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
        im = im.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.35))
    else:
        im = Image.new("RGB", (W, H), "#0d0d0f")
    d = ImageDraw.Draw(im)
    y = 330
    if ust:
        f = font("Oswald.ttf", 64); u = tr_upper(ust); w = d.textlength(u, font=f)
        d.text(((W - w) / 2, y), u, font=f, fill="#e9e4da"); y += 110
    f = sigdir(d, tr_upper(ana), "Anton-Regular.ttf", W - 240, 150); a = tr_upper(ana)
    bb = d.textbbox((0, 0), a, font=f); d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), a, font=f, fill=renk)
    y += (bb[3] - bb[1]) + 50
    if alt:
        f = sigdir(d, alt, "Oswald.ttf", W - 300, 58); w = d.textlength(alt, font=f)
        d.text(((W - w) / 2, y), alt, font=f, fill="#ffffff")
    f = font("Oswald.ttf", 40); d.text((W - 360, H - 80), "@Belgesellerim", font=f, fill="#bbbbbb")
    im.save(yol, quality=93)


def kart_video(resim, sure_s, cikis, muzik):
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", resim, "-i", muzik, "-t", f"{sure_s:.2f}",
         "-vf", f"scale={W}:{H},zoompan=z='1.0+0.04*on/{int(sure_s*FPS)}':d={int(sure_s*FPS)}:s={W}x{H}:fps={FPS},fade=t=in:st=0:d=0.3,fade=t=out:st={sure_s-0.3:.2f}:d=0.3",
         "-af", f"volume=0.5,afade=t=in:d=0.3,afade=t=out:st={sure_s-0.4:.2f}:d=0.4", "-shortest", *ENC, cikis])


def bolum_video(mp4, kes, baslik, no, cikis):
    """Dikey Short'u ortada, arkasında kendi bulanık kopyası; solda bölüm numarası ve başlık."""
    yazi = os.path.join(os.path.dirname(cikis), f"yazi{no}.png")
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font("Anton-Regular.ttf", 170); d.text((90, 300), f"#{no}", font=f, fill="#FFC832")
    satir, cur = [], ""
    for k in baslik.split():
        if len(cur + " " + k) > 18:
            satir.append(cur.strip()); cur = k
        else:
            cur += " " + k
    satir.append(cur.strip())
    f2 = font("Oswald.ttf", 54)
    for i, s in enumerate(satir[:5]):
        d.text((95, 540 + i * 70), s, font=f2, fill="#ffffff")
    d.text((W - 380, H - 80), "@Belgesellerim", font=font("Oswald.ttf", 40), fill="#cccccc")
    im.save(yazi)
    fg_w = int(H * 9 / 16)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-i", yazi, "-t", f"{kes:.2f}", "-filter_complex",
         f"[0:v]split=2[a][b];[a]scale={W}:-2,crop={W}:{H},boxblur=30:2,eq=brightness=-0.25[bg];"
         f"[b]scale={fg_w}:{H}[fg];[bg][fg]overlay=(W-w)/2:0[v1];[v1][1:v]overlay=0:0,fade=t=in:st=0:d=0.25,fade=t=out:st={kes-0.3:.2f}:d=0.3[v]",
         "-map", "[v]", "-map", "0:a", "-af", f"afade=t=out:st={kes-0.4:.2f}:d=0.4", *ENC, cikis])


def zaman_str(t):
    t = int(t); return f"{t // 60}:{t % 60:02d}" if t < 3600 else f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cikis"); ap.add_argument("isler", nargs="+")
    ap.add_argument("--baslik", default="Bu Haftanın En Tuhaf Savaş Hikâyeleri")
    ap.add_argument("--tarih", default="")
    a = ap.parse_args()
    tmp = os.path.splitext(a.cikis)[0] + "_tmp"; os.makedirs(tmp, exist_ok=True)
    muzik = os.path.join(tmp, "m.wav")
    run([sys.executable, os.path.join(BURADA, "muzik.py"), "20", muzik, "--duygu", "epik", "--tohum", os.path.basename(a.cikis)])
    parcalar, bolumler, t, ilk_kare = [], [], 0.0, None
    # giriş
    bolum_listesi = []
    for yol in a.isler:
        v = oku(os.path.join(yol, "video.json")); z = oku(os.path.join(yol, "zaman.json"))
        ad = os.path.basename(os.path.normpath(yol))
        mp4 = os.path.join(KOK, "v", ad + ".mp4")
        if not os.path.exists(mp4):   # ör. iş "1904-maratonu" → video "2026-11-07-1904-maratonu.mp4"
            import glob
            aday = [x for x in glob.glob(os.path.join(KOK, "v", f"*{ad}.mp4")) if "onizleme" not in x]
            mp4 = aday[0] if aday else mp4
        if not os.path.exists(mp4):
            print("ATLANDI (mp4 yok):", mp4); continue
        tempo = float(v.get("tempo", 1.0))
        kes = z["sahneler"][-1]["s"] / tempo if len(z["sahneler"]) > 2 else sure(mp4)
        kes = min(kes + 0.2, sure(mp4))
        baslik = v["seo"]["baslik"].replace("#shorts", "").strip()
        bolum_listesi.append((yol, v, mp4, kes, baslik))
    if not bolum_listesi:
        raise SystemExit("derlenecek video yok")
    arka0 = os.path.join(tmp, "arka0.jpg")
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "3", "-i", bolum_listesi[0][2], "-frames:v", "1", arka0])
    kart_resmi(os.path.join(tmp, "giris.jpg"), a.tarih or "bu hafta", a.baslik, f"{len(bolum_listesi)} gerçek hikâye · arşiv fotoğraflarıyla", arka0)
    kart_video(os.path.join(tmp, "giris.jpg"), 4.0, os.path.join(tmp, "p00.mp4"), muzik)
    parcalar.append(os.path.join(tmp, "p00.mp4")); bolumler.append(("0:00", "Giriş")); t = 4.0
    for i, (yol, v, mp4, kes, baslik) in enumerate(bolum_listesi, 1):
        cik = os.path.join(tmp, f"p{i:02d}.mp4")
        bolum_video(mp4, kes, baslik, i, cik)
        bolumler.append((zaman_str(t), baslik)); t += sure(cik); parcalar.append(cik)
    # kapanış (uç ekran öğeleri için 15 sn)
    kart_resmi(os.path.join(tmp, "son.jpg"), "her akşam yeni bir hikâye", "Belgesellerim", "Savaş tarihinin tuhaf ve gerçek hikâyeleri için abone ol", arka0)
    kart_video(os.path.join(tmp, "son.jpg"), 15.0, os.path.join(tmp, "p99.mp4"), muzik)
    bolumler.append((zaman_str(t), "Kapanış")); parcalar.append(os.path.join(tmp, "p99.mp4"))
    lst = os.path.join(tmp, "l.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parcalar))
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", a.cikis])
    kok = os.path.splitext(a.cikis)[0]
    open(kok + "-bolumler.txt", "w", encoding="utf-8").write("\n".join(f"{z} {b}" for z, b in bolumler) + "\n")
    # küçük resim: 3 kare kolaj + başlık
    kap = Image.new("RGB", (1280, 720), "#0d0d0f")
    for j, (yol, v, mp4, kes, baslik) in enumerate(bolum_listesi[:3]):
        fr = os.path.join(tmp, f"kp{j}.jpg")
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{min(8, kes/2):.1f}", "-i", mp4, "-frames:v", "1", "-vf", "scale=427:-2", fr])
        k = Image.open(fr); k = k.crop((0, (k.height - 720) // 2, 427, (k.height - 720) // 2 + 720)) if k.height > 720 else k
        kap.paste(k, (j * 427, 0))
    kap = kap.point(lambda v: int(v * 0.55)); d = ImageDraw.Draw(kap)
    ust = tr_upper(a.baslik)
    f = sigdir(d, ust, "Anton-Regular.ttf", 1180, 96)
    w = d.textlength(ust, font=f)
    d.rectangle((0, 470, 1280, 640), fill=(0, 0, 0))
    d.text(((1280 - w) / 2, 495), ust, font=f, fill="#FFC832")
    kap.save(kok + "-kapak.jpg", quality=92)
    print("TAMAM", a.cikis, zaman_str(sure(a.cikis)), f"{os.path.getsize(a.cikis)/1e6:.1f} MB", len(bolum_listesi), "bölüm")


if __name__ == "__main__":
    main()
