"""Videoyu birleştirir: kareler -> kamera hareketli çekimler -> kelime kelime altyazı -> müzik/efekt -> mp4.

python3 kurgu.py IS_KLASORU CIKIS.mp4 [--gecmis gunluk_stilleri.json] [--hizli]
IS_KLASORU içinde: video.json, zaman.json, ses.wav, img/ (görseller)
"""
import argparse, math, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import (FONT_DIR, FPS, H, W, ass_renk, font_bilgi, oku, palet_bilgi, rng_for, run,
                   stil_sec, sure, tr_upper, yaz)
from kare import kare_foto, kare_kart
from PIL import Image

PY = sys.executable
BURADA = os.path.dirname(os.path.abspath(__file__))
MAX_CEKIM = 3.2   # bir görüntü en fazla bu kadar saniye ekranda kalır

HAREKET = {
    "yaklas": "z='1.0+0.10*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "uzaklas": "z='1.10-0.10*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "sola": "z='1.09':x='(iw-iw/zoom)*(1-on/{n})':y='ih/2-(ih/zoom/2)'",
    "saga": "z='1.09':x='(iw-iw/zoom)*on/{n}':y='ih/2-(ih/zoom/2)'",
    "yukari": "z='1.09':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{n})'",
    "asagi": "z='1.09':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{n}'",
    "vurus": "z='1.0+0.13*(1-exp(-on/6))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
}


def cekim_listesi(is_, zaman, r, klasor):
    atif = {}
    ap = os.path.join(klasor, "atif.json")
    if os.path.exists(ap):
        atif = {a["dosya"]: a for a in oku(ap)}
    def kucuk(dosya):  # Wikimedia aslı 900 px'ten darsa yakın plan bulanık olur
        a = atif.get(os.path.basename(dosya), {})
        return bool(a.get("w")) and min(a["w"], a.get("h") or a["w"]) < 900

    """Her sahneyi görüntü 3 saniyeyi geçmeyecek şekilde çekimlere böler."""
    cekimler = []
    hareketler = list(HAREKET)
    son_h = None
    for i, sh in enumerate(is_["sahneler"]):
        s, e = zaman["sahneler"][i]["s"], zaman["sahneler"][i]["e"]
        if i == len(is_["sahneler"]) - 1:
            e = zaman["sure"] + is_.get("kuyruk", 0.7)
        d = e - s
        gor = sh.get("gorseller") or []
        if not gor:
            raise SystemExit(f"sahne {i}: görsel yok")
        maxc = float(is_.get("max_cekim", MAX_CEKIM))
        k = len(gor) if any("klip" in g for g in gor) else max(len(gor), math.ceil(d / maxc))
        liste = []
        for j in range(k):
            g = dict(gor[j % len(gor)])
            if j >= len(gor) and "dosya" in g and kucuk(g["dosya"]):
                g.pop("duzen", None)   # düşük çözünürlüklü görsel: yakın plan yerine farklı düzen/hareket
                g["duzen"] = "bulanik" if gor[j % len(gor)].get("duzen") != "bulanik" else "cerceve"
            elif j >= len(gor) and "dosya" in g:
                g["duzen"] = "detay"
                o = g.get("odak", [0.5, 0.35])
                g["odak"] = [min(0.8, max(0.2, o[0] + r.uniform(-0.12, 0.12))), min(0.7, max(0.15, o[1] + r.uniform(-0.08, 0.08)))]
            liste.append(g)
        dj = d / k
        for j, g in enumerate(liste):
            if "dosya" in g and "duzen" not in g:
                with Image.open(os.path.join(klasor, g["dosya"])) as im:
                    yatay = im.width / im.height > 0.75
                g["duzen"] = r.choice(["bulanik", "cerceve", "doldur", "bulanik"]) if yatay else "doldur"
            h = g.get("hareket")
            if not h:
                secenek = [x for x in hareketler if x != son_h and (x != "vurus" or (i == 0 and j == 0) or r.random() < 0.3)]
                h = "vurus" if (i == 0 and j == 0) else r.choice(secenek)
            son_h = h
            cekimler.append({"sahne": i, "bas": s + j * dj, "sure": dj, "g": g, "hareket": h})
    return cekimler


def kareleri_hazirla(cekimler, stil, klasor):
    os.makedirs(os.path.join(klasor, "k"), exist_ok=True)
    for n, c in enumerate(cekimler):
        cik = os.path.join(klasor, "k", f"k{n:02d}.jpg")
        g = c["g"]
        if "klip" in g:      # hazır video klibi (ör. saat animasyonu): kare üretilmez
            continue
        if "kart" in g:
            kare_kart(g["kart"], stil, cik, tohum=n)
        else:
            kare_foto(os.path.join(klasor, g["dosya"]), g["duzen"], g.get("ton", stil["ton"]), cik,
                      tuple(g.get("odak", (0.5, 0.5))), tohum=n)
        c["kare"] = cik


def cekimleri_render(cekimler, klasor, hizli=False):
    parcalar = []
    for n, c in enumerate(cekimler):
        kare_sayisi = max(2, round(c["sure"] * FPS))
        c["kare_sayisi"] = kare_sayisi
        cik = os.path.join(klasor, f"c{n:02d}.mp4")
        if "klip" in c["g"]:
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(klasor, c["g"]["klip"]), "-an",
                 "-vf", f"scale={W}:{H},fps={FPS},tpad=stop_mode=clone:stop_duration=60,format=yuv420p",
                 "-frames:v", str(kare_sayisi), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS), cik])
            parcalar.append(cik)
            continue
        expr = HAREKET[c["hareket"]].format(n=kare_sayisi)
        olcek = "1188:2112" if hizli else "2376:4224"   # 2x büyütüp hareket ettirmek titremeyi önler
        vf = f"scale={olcek},zoompan={expr}:d={kare_sayisi}:s={W}x{H}:fps={FPS},format=yuv420p"
        cik = os.path.join(klasor, f"c{n:02d}.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", c["kare"], "-frames:v", str(kare_sayisi),
             "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", str(FPS), cik])
        parcalar.append(cik)
    lst = os.path.join(klasor, "c.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parcalar))
    v = os.path.join(klasor, "v.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", v])
    return v


# ------------------------------------------------------------------ altyazı (ASS)
def ass_zaman(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def temiz(w):
    w = w.replace("{", "").replace("}", "")
    return re.sub(r"[,.;:…\"“”]+$", "", w).lstrip("\"“")


def gruplar(kelimeler, boy):
    out, cur = [], []
    for k in kelimeler:
        cur.append(k)
        uzun = sum(len(x["w"]) for x in cur) > 16
        if len(cur) >= boy or k["w"][-1] in ".!?,;:" or uzun:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def altyazi_yaz(is_, zaman, stil, yol, toplam):
    f = font_bilgi(stil["font"]); p = palet_bilgi(stil["palet"])
    beyaz, vurgu, siyah = "&H00FFFFFF", ass_renk(p["vurgu"]), "&H00000000"
    boy = f["boy"]
    satirlar = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Alt,{f['ad']},{boy},{beyaz},{beyaz},{siyah},&H64000000,0,0,0,0,100,100,1,0,1,7,3,2,70,70,{stil['konum']},1",
        f"Style: Etiket,Oswald,66,{beyaz},{beyaz},{ass_renk(p['etiket'])},{ass_renk(p['etiket'])},1,0,0,0,100,100,2,0,3,16,0,8,80,80,250,1",
        f"Style: Kapak,{f['ad']},{int(boy * 1.3)},{beyaz},{beyaz},{siyah},&H80000000,0,0,0,0,100,100,1,0,1,9,4,8,60,60,{int(is_.get('kapak_y', 330))},1",
        f"Style: Rozet,Oswald,44,{beyaz},{beyaz},{siyah},&H50000000,1,0,0,0,100,100,1,0,3,10,0,7,60,60,150,1",
        f"Style: Imza,Oswald,40,&H55FFFFFF,&H55FFFFFF,&H80000000,&H00000000,1,0,0,0,100,100,1,0,1,2,0,9,60,60,158,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    buyuk = f["buyuk"]
    up = (lambda s: tr_upper(s)) if buyuk else (lambda s: s)
    # kelime kelime vurgulu altyazı
    for i in range(len(is_["sahneler"])):
        ks = [k for k in zaman["kelimeler"] if k["sahne"] == i]
        gs = gruplar(ks, stil["grup"])
        for gi, g in enumerate(gs):
            sonraki = gs[gi + 1][0]["s"] if gi + 1 < len(gs) else None
            if sonraki is None:
                sonraki_sahne = [k for k in zaman["kelimeler"] if k["sahne"] == i + 1]
                sonraki = sonraki_sahne[0]["s"] if sonraki_sahne else toplam
            bitis = min(sonraki, g[-1]["e"] + 0.6)
            for wi, k in enumerate(g):
                bas = g[0]["s"] if wi == 0 else k["s"]
                son = g[wi + 1]["s"] if wi + 1 < len(g) else bitis
                if son - bas < 0.02:
                    continue
                parca = []
                for wj, kk in enumerate(g):
                    w = up(temiz(kk["w"]))
                    if wj == wi:
                        parca.append(r"{\c" + vurgu + r"\fscx108\fscy108}" + w + r"{\c" + beyaz + r"\fscx100\fscy100}")
                    else:
                        parca.append(w)
                pop = r"{\fscx92\fscy92\t(0,90,\fscx100\fscy100)}" if wi == 0 else ""
                satirlar.append(f"Dialogue: 0,{ass_zaman(bas)},{ass_zaman(son)},Alt,,0,0,0,,{pop}{' '.join(parca)}")
    # sahne etiketleri (üstte küçük kutu: "ST. LOUIS · 1904")
    for i, sh in enumerate(is_["sahneler"]):
        if sh.get("etiket"):
            s, e = zaman["sahneler"][i]["s"], zaman["sahneler"][i]["e"]
            satirlar.append(f"Dialogue: 1,{ass_zaman(s + 0.1)},{ass_zaman(e)},Etiket,,0,0,0,,{{\\fad(150,150)}}{tr_upper(sh['etiket'])}")
    # seri rozeti (sol üst, tüm video) + kanal imzası (sağ üst): izleyici seriyi ve kanalı hatırlar
    if is_.get("seri_rozet"):
        satirlar.append(f"Dialogue: 1,{ass_zaman(0)},{ass_zaman(toplam)},Rozet,,0,0,0,,{{\\c{vurgu}}}{tr_upper(is_['seri_rozet'])}")
    satirlar.append(f"Dialogue: 1,{ass_zaman(0)},{ass_zaman(toplam)},Imza,,0,0,0,,{is_.get('imza', '@Belgesellerim')}")
    # kapak başlığı (ilk ~2,3 sn): Shorts kapak karesi olarak da iş görür
    if is_.get("kapak"):
        satir = [up(x) for x in is_["kapak"]]
        en_uzun = max(len(x) for x in satir)
        from PIL import ImageFont
        fnt = ImageFont.truetype(os.path.join(FONT_DIR, f["dosya"]), 100)
        gen = max(fnt.getlength(re.sub(r"\{[^}]*\}", "", x)) for x in satir) / 100
        a_, d_ = fnt.getmetrics()   # libass punto = satır yüksekliği; PIL punto = em
        kboy = int(min(boy * 1.6, 900 / max(gen, 1e-3) * (a_ + d_) / 100))
        satir[0] = r"{\fs" + str(kboy) + "}" + satir[0]
        if len(satir) > 1:
            satir[-1] = r"{\c" + vurgu + "}" + satir[-1]
        satirlar.append(f"Dialogue: 2,{ass_zaman(0)},{ass_zaman(is_.get('kapak_sure', 2.3))},Kapak,,0,0,0,,{{\\fad(0,250)}}" + r"\N".join(satir))
    open(yol, "w", encoding="utf-8").write("\n".join(satirlar) + "\n")


# ------------------------------------------------------------------ ana akış
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("klasor"); ap.add_argument("cikis")
    ap.add_argument("--gecmis", default=""); ap.add_argument("--hizli", action="store_true")
    a = ap.parse_args()
    k = a.klasor
    is_ = oku(os.path.join(k, "video.json")); zaman = oku(os.path.join(k, "zaman.json"))
    if os.path.exists(os.path.join(k, "ses_ham.mp3")):
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(k, "ses_ham.mp3"), "-ar", "44100", "-ac", "1", os.path.join(k, "ses.wav")])
    tempo = float(is_.get("tempo", 1.0))   # ElevenLabs v3 yavaş okursa sesi hızlandır (1.0–1.2)
    if tempo != 1.0:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(k, "ses.wav"), "-af", f"atempo={tempo}",
             "-ar", "44100", "-ac", "1", os.path.join(k, "ses_t.wav")])
        os.replace(os.path.join(k, "ses_t.wav"), os.path.join(k, "ses.wav"))
        for kk in zaman["kelimeler"]:
            kk["s"] /= tempo; kk["e"] /= tempo
        for ss in zaman["sahneler"]:
            ss["s"] /= tempo; ss["e"] /= tempo
        zaman["sure"] = sure(os.path.join(k, "ses.wav"))
    gecmis = oku(a.gecmis) if a.gecmis and os.path.exists(a.gecmis) else []
    stil = {**stil_sec(is_["slug"], gecmis), **is_.get("stil", {})}
    yaz(os.path.join(k, "stil.json"), stil)
    r = rng_for(is_["slug"], "kurgu")
    print("stil:", stil)

    cekimler = cekim_listesi(is_, zaman, r, k)
    kareleri_hazirla(cekimler, stil, k)
    v = cekimleri_render(cekimler, k, a.hizli)
    D = sure(v)

    ass = os.path.join(k, "alt.ass")
    altyazi_yaz(is_, zaman, stil, ass, D)

    # müzik + efekt
    kesmeler = ",".join(f"{zaman['sahneler'][i]['s']:.2f}" for i in range(1, len(is_["sahneler"])))
    vurgular = ",".join(f"{zaman['sahneler'][i]['s']:.2f}" for i in is_.get("vurgu_sahneleri", []))
    m, ef = os.path.join(k, "m.wav"), os.path.join(k, "ef.wav")
    run([PY, os.path.join(BURADA, "muzik.py"), f"{D:.2f}", m, "--duygu", is_.get("duygu", "merak"),
         "--tohum", is_["slug"], "--kesmeler", kesmeler, "--vurgular", vurgular, "--efekt_cikis", ef])
    ses = os.path.join(k, "ses.wav")
    mix = os.path.join(k, "mix.wav")
    mv = is_.get("muzik_seviye", 0.17)
    # ElevenLabs müziği varsa (muzik_el.mp3) sentetik müziğin yerine o kullanılır
    mel = os.path.join(k, "muzik_el.mp3")
    if os.path.exists(mel) and os.path.getsize(mel) > 20000:
        run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", mel, "-t", f"{D:.3f}", "-af",
             f"loudnorm=I=-18:TP=-2:LRA=11,afade=t=in:d=0.8,afade=t=out:st={max(0, D - 2.5):.2f}:d=2.5", "-ar", "44100", "-ac", "1", m])
        mv = is_.get("muzik_seviye_el", 0.42)
        print("müzik: ElevenLabs")
    ev = float(is_.get("efekt_seviye", 0.5))      # 0 → sahne geçişi sesleri kapalı (anma videoları)
    girdiler = ["-i", ses, "-i", m, "-i", ef]
    fc = ("[0:a]loudnorm=I=-14:TP=-1.5:LRA=9,apad,asplit=2[v][sc];"
          f"[1:a]volume={mv}[mm];[mm][sc]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=450[md];"
          f"[2:a]volume={ev}[e];")
    etiketler = "[v][md][e]"; n_in = 3
    tempo = float(is_.get("tempo", 1.0))
    for sx in is_.get("sfx", []):               # {"dosya","sahne","ofset","seviye","sure"}: ElevenLabs ses efektleri
        yol = os.path.join(k, sx["dosya"])
        if not os.path.exists(yol) or os.path.getsize(yol) < 2000:
            print("sfx yok, atlandı:", sx["dosya"]); continue
        bas = max(0.0, zaman["sahneler"][sx["sahne"]]["s"] + float(sx.get("ofset", 0)))
        sure_s = float(sx.get("sure", 4))
        girdiler += ["-i", yol]
        fc += (f"[{n_in}:a]aresample=44100,atrim=0:{sure_s},afade=t=in:d=0.15,afade=t=out:st={max(0.1, sure_s - 0.8):.2f}:d=0.8,"
               f"volume={sx.get('seviye', 0.5)},adelay={int(bas * 1000)}:all=1[s{n_in}];")
        etiketler += f"[s{n_in}]"; n_in += 1
    fc += f"{etiketler}amix=inputs={n_in}:duration=longest:normalize=0,alimiter=limit=0.95[a]"
    run(["ffmpeg", "-y", "-loglevel", "error", *girdiler, "-filter_complex", fc,
         "-map", "[a]", "-t", f"{D:.3f}", "-ar", "44100", mix])

    # son birleştirme: altyazı + vinyet + gren + ilerleme çubuğu
    p = palet_bilgi(stil["palet"])
    vf = []
    if stil.get("vinyet"):
        vf.append("vignette=PI/5")
    if stil.get("tanecik"):
        vf.append("noise=alls=4:allf=t")
    vf.append(f"ass={ass}:fontsdir={FONT_DIR}")
    if stil.get("ilerleme"):
        vf.append(f"drawbox=x=0:y=ih-12:w='iw*t/{D:.3f}':h=12:color={p['vurgu']}@0.95:t=fill")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", v, "-i", mix, "-vf", ",".join(vf),
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-maxrate", "9M", "-bufsize", "18M",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{D:.3f}", a.cikis])
    if a.gecmis:
        yaz(a.gecmis, (gecmis + [{"slug": is_["slug"], **stil}])[-12:])
    print("TAMAM", a.cikis, f"{D:.1f} sn", f"{len(cekimler)} çekim", f"{os.path.getsize(a.cikis) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
