"""Ortak yardımcılar: Türkçe büyük harf, ffmpeg çağrısı, video başına tohum ve stil seçimi."""
import hashlib, json, os, random, subprocess

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tarih/
FONT_DIR = os.path.join(KOK, "fonts")
W, H, FPS = 1080, 1920, 30


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def run(args, **kw):
    return subprocess.run(args, check=True, **kw)


def sure(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return float(out)


def rng_for(slug, extra=""):
    """Her video kendi slug'ından tohum alır: aynı video yeniden üretilirse aynı görünür,
    farklı videolar farklı görünür."""
    h = int(hashlib.md5((slug + extra).encode()).hexdigest()[:12], 16)
    return random.Random(h)


# --- Stil havuzu: her video bu havuzdan farklı bir birleşim alır ---------------------------
FONTLAR = [
    {"ad": "Anton", "dosya": "Anton-Regular.ttf", "boy": 112, "buyuk": True},
    {"ad": "Bebas Neue", "dosya": "BebasNeue-Regular.ttf", "boy": 136, "buyuk": True},
    {"ad": "Archivo Black", "dosya": "ArchivoBlack-Regular.ttf", "boy": 98, "buyuk": False},
]
# vurgu: konuşulan kelimenin rengi; etiket: üst etiket kutusu rengi (ASS için &HBBGGRR)
PALETLER = [
    {"ad": "altin", "vurgu": "#FFC832", "etiket": "#C8102E"},
    {"ad": "zehir", "vurgu": "#9BFF3C", "etiket": "#1B1B1B"},
    {"ad": "buz", "vurgu": "#56D8FF", "etiket": "#0B3D91"},
    {"ad": "kor", "vurgu": "#FF7A1A", "etiket": "#2B2B2B"},
    {"ad": "pembe", "vurgu": "#FF4FA3", "etiket": "#3A0CA3"},
    {"ad": "sari", "vurgu": "#FFE600", "etiket": "#111111"},
]
RENK_TONU = ["sepya", "soguk", "sicak", "solgun", "kontrast", "dogal"]
ALTYAZI_KONUM = [560, 640, 720]   # alttan boşluk (px): Shorts arayüzünün üstünde kalır
KELIME_GRUBU = [2, 3, 3, 4]


def stil_sec(slug, gecmis=None):
    """gecmis: son videoların stil listesi (gunluk'ten). Son 3 videoyla aynı font+palet
    birleşimini vermemeye çalışır."""
    r = rng_for(slug, "stil")
    gecmis = gecmis or []
    for _ in range(40):
        s = {
            "font": r.choice(FONTLAR)["ad"],
            "palet": r.choice(PALETLER)["ad"],
            "ton": r.choice(RENK_TONU),
            "konum": r.choice(ALTYAZI_KONUM),
            "grup": r.choice(KELIME_GRUBU),
            "ilerleme": r.random() < 0.6,     # alttaki ilerleme çubuğu
            "tanecik": r.random() < 0.7,      # film greni
            "vinyet": r.random() < 0.8,
        }
        # bir önceki videoyla aynı font yok; son 3 videoyla aynı palet ve renk tonu yok
        if (not gecmis or gecmis[-1].get("font") != s["font"]) and \
           all(g.get("palet") != s["palet"] and g.get("ton") != s["ton"] for g in gecmis[-3:]):
            return s
    return s


def font_bilgi(ad):
    return next(f for f in FONTLAR if f["ad"] == ad)


def palet_bilgi(ad):
    return next(p for p in PALETLER if p["ad"] == ad)


def ass_renk(hexrgb, alfa="00"):
    h = hexrgb.lstrip("#")
    return f"&H{alfa}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def oku(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def yaz(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
