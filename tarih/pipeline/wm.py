"""Wikimedia Commons'tan lisansı uygun arşiv görseli bulur ve indirir.

python3 wm.py s "arama" [adet]             -> dosya adları (+ lisans), son kullanılanlar işaretli
python3 wm.py i "File:..." img/ad.jpg      -> lisans bilgisini yazar, indirir, kullanılanlara ekler
Yalnızca: Public domain, CC0, CC BY, CC BY-SA. BY/BY-SA ise açıklamaya atıf yazılır (atif.json'a eklenir).
"""
import datetime, json, os, re, subprocess, sys, time, urllib.parse

UA = "TuhafTarihBot/1.0 (YouTube egitim kanali; iletisim github.com/xoqxs)"
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(KOK, "kullanilan-gorseller.txt")
UYGUN = re.compile(r"^(public domain|pd|cc0|cc[- ]by(-sa)?([- ][0-9.]+)?|cc by(-sa)? [0-9.]+)", re.I)


def api(params):
    u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json"})
    for k in range(8):
        out = subprocess.run(["curl", "-s", "-m", "25", "-A", UA, u], capture_output=True, text=True).stdout
        try:
            return json.loads(out)
        except Exception:
            time.sleep(8 + k * 5)
    raise SystemExit("wikimedia erişilemedi / hız sınırı")


def bilgi(baslik):
    p = api({"action": "query", "titles": baslik, "prop": "imageinfo", "iiprop": "url|extmetadata|size"})["query"]["pages"]
    ii = list(p.values())[0]["imageinfo"][0]; m = ii["extmetadata"]
    g = lambda k: re.sub("<[^>]+>", "", m.get(k, {}).get("value", "") or "").strip()
    return {"lisans": g("LicenseShortName"), "yazar": g("Artist")[:90], "tarih": g("DateTimeOriginal")[:40],
            "w": ii.get("width"), "h": ii.get("height"), "aciklama": g("ImageDescription")[:160]}


def kullanilanlar():
    if not os.path.exists(LOG):
        return []
    return [l.split("\t", 1)[1].strip() for l in open(LOG, encoding="utf-8") if "\t" in l][-400:]


if __name__ == "__main__":
    if sys.argv[1] == "s":
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        r = api({"action": "query", "list": "search", "srnamespace": 6, "srlimit": n, "srsearch": sys.argv[2]})
        u = set(kullanilanlar())
        for x in r["query"]["search"]:
            t = x["title"]
            if not re.search(r"\.(jpe?g|png|tiff?)$", t, re.I):
                continue
            print(("[KULLANILDI] " if t in u else "") + t)
    else:
        baslik, hedef = sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else None)
        if baslik in kullanilanlar() and os.environ.get("TEKRAR") != "1":
            raise SystemExit("TEKRAR: bu görsel daha önce kullanıldı: " + baslik)
        b = bilgi(baslik)
        print(json.dumps(b, ensure_ascii=False))
        if not UYGUN.match(b["lisans"] or ""):
            raise SystemExit("LİSANS UYGUN DEĞİL: " + b["lisans"])
        if hedef:
            os.makedirs(os.path.dirname(os.path.abspath(hedef)), exist_ok=True)
            url = "https://commons.wikimedia.org/w/thumb.php?" + urllib.parse.urlencode({"w": 1600, "f": baslik.split(":", 1)[1]})
            subprocess.run(["curl", "-sL", "-m", "90", "-A", UA, "-o", hedef, url], check=True)
            kind = subprocess.run(["file", "-b", hedef], capture_output=True, text=True).stdout
            if "image" not in kind:
                os.remove(hedef); raise SystemExit("indirme başarısız (görsel değil): " + kind[:60])
            open(LOG, "a", encoding="utf-8").write(datetime.date.today().isoformat() + "\t" + baslik + "\n")
            atif = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(hedef))), "atif.json")
            liste = json.load(open(atif, encoding="utf-8")) if os.path.exists(atif) else []
            liste.append({"dosya": os.path.basename(hedef), "baslik": baslik, **b})
            json.dump(liste, open(atif, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
