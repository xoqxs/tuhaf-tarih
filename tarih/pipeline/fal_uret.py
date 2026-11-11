"""fal.ai ile görsel üretir ve fotoğraf canlandırır (GitHub Actions'ta çalışır; FAL_KEY secret).

python3 fal_uret.py KLASOR        -> KLASOR/gorsel.json'daki eksik öğeleri üretir
gorsel.json:
{"ogeler": [
  {"tur": "resim", "cikis": "img/c1.jpg", "prompt": "...", "boyut": "portrait_16_9"},
  {"tur": "klip",  "cikis": "klip/k1.mp4", "kaynak": "img/bulut1.jpg", "prompt": "...", "cozunurluk": "580p"}
]}
Çıkışı zaten olan öğe atlanır (kredi harcanmaz). Bütçe sınırı: çalışma başına en fazla 14 resim + 5 klip.
"""
import json, os, sys, urllib.request

import fal_client

RESIM_MODEL = "fal-ai/flux/schnell"
KLIP_MODEL = "fal-ai/wan/v2.2-a14b/image-to-video/turbo"
MAX_RESIM, MAX_KLIP = 14, 5


def indir(url, yol):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "belgesellerim/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r, open(yol, "wb") as f:
        f.write(r.read())


def main():
    k = sys.argv[1].rstrip("/")
    plan = json.load(open(os.path.join(k, "gorsel.json"), encoding="utf-8"))
    n_resim = n_klip = 0
    hata = 0
    # önce resimler (klipler üretilen resmi kaynak alabilir)
    for o in sorted(plan["ogeler"], key=lambda o: o["tur"] != "resim"):
        cikis = os.path.join(k, o["cikis"])
        if os.path.exists(cikis) and os.path.getsize(cikis) > 2000:
            continue
        try:
            if o["tur"] == "resim":
                if n_resim >= MAX_RESIM:
                    print("resim sınırı, atlandı:", o["cikis"]); continue
                r = fal_client.subscribe(RESIM_MODEL, arguments={
                    "prompt": o["prompt"], "image_size": o.get("boyut", "portrait_16_9"),
                    "num_inference_steps": 4, "num_images": 1, "output_format": "jpeg",
                    **({"seed": o["tohum"]} if "tohum" in o else {})})
                indir(r["images"][0]["url"], cikis); n_resim += 1
            elif o["tur"] == "klip":
                if n_klip >= MAX_KLIP:
                    print("klip sınırı, atlandı:", o["cikis"]); continue
                kaynak = os.path.join(k, o["kaynak"])
                url = fal_client.upload_file(kaynak)
                r = fal_client.subscribe(KLIP_MODEL, arguments={
                    "image_url": url, "prompt": o["prompt"],
                    "resolution": o.get("cozunurluk", "580p"), "aspect_ratio": o.get("oran", "9:16"),
                    **({"seed": o["tohum"]} if "tohum" in o else {})})
                indir(r["video"]["url"], cikis); n_klip += 1
            print("tamam:", o["cikis"], os.path.getsize(cikis))
        except Exception as e:   # bir öğe düşerse diğerleri sürsün; kurgu eksik klipte fotoğrafa döner
            hata += 1
            print(f"::warning::{o['cikis']} üretilemedi: {type(e).__name__}: {str(e)[:300]}")
    print(f"özet: {n_resim} resim, {n_klip} klip, {hata} hata")
    if hata and n_resim + n_klip == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
