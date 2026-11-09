"""Seslendirme + kelime zamanlaması.

Kullanım:  python3 ses.py IS_KLASORU [eleven|azure|tahmini]
Çıktı:     IS_KLASORU/ses.wav  ve  IS_KLASORU/zaman.json

eleven  : ElevenLabs /with-timestamps (ELEVENLABS_API_KEY ortam değişkeni). Kelime zamanları gerçek.
          Bulut oturumundan ElevenLabs'e erişilemez; bu mod GitHub Actions'ta (tarih-ses.yml) çalışır.
azure   : Yedek. Sahne sahne Azure TTS (AZURE_TTS_KEY, AZURE_TTS_REGION); kelime zamanı sahne içinde
          harf sayısına göre dağıtılır.
tahmini : Ses yok (sessiz), süre metinden tahmin edilir. Yalnızca görsel önizleme için.
"""
import base64, difflib, json, os, re, subprocess, sys, urllib.request, wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import oku, yaz, run, sure

ETIKET = re.compile(r"^\[[^\]]*\]$")  # eleven v3 ses etiketleri: [fısıltı] vb. altyazıya girmez


def kelimeler_ve_ofset(metin):
    return [(m.group(), m.start(), m.end()) for m in re.finditer(r"\S+", metin)]


def birlesik_metin(is_):
    parcalar, sinirlar, pos = [], [], 0
    for sh in is_["sahneler"]:
        t = sh["metin"].strip()
        sinirlar.append((pos, pos + len(t)))
        parcalar.append(t)
        pos += len(t) + 1
    return " ".join(parcalar), sinirlar


def sahne_no(ofset, sinirlar):
    for i, (a, b) in enumerate(sinirlar):
        if ofset < b + 1:
            return i
    return len(sinirlar) - 1


def zaman_kur(metin, sinirlar, kelime_zamanlari, toplam):
    """kelime_zamanlari: [(kelime, ofset, s, e)] -> zaman.json yapısı"""
    kel = []
    for w, of, s, e in kelime_zamanlari:
        if ETIKET.match(w):
            continue
        kel.append({"w": w, "s": round(s, 3), "e": round(e, 3), "sahne": sahne_no(of, sinirlar)})
    n = len(sinirlar)
    bas = []
    for i in range(n):
        ks = [k for k in kel if k["sahne"] == i]
        bas.append(ks[0]["s"] if ks else (bas[-1] if bas else 0.0))
    bas[0] = 0.0
    sahneler = [{"s": round(bas[i], 3), "e": round(bas[i + 1] if i + 1 < n else toplam, 3)} for i in range(n)]
    return {"kelimeler": kel, "sahneler": sahneler, "sure": round(toplam, 3)}


# ---------------------------------------------------------------- ElevenLabs
def eleven(is_, klasor):
    key = os.environ["ELEVENLABS_API_KEY"]
    cfg = is_.get("ses", {})
    voice = cfg.get("voice_id", "t8fOU8zfPVWFYN34BllH")  # Zangess (Kadir Bey 7 Kasım 2026)
    metin, sinirlar = birlesik_metin(is_)
    ayar = {"stability": cfg.get("stability", 0.42), "similarity_boost": 0.8,
            "style": cfg.get("style", 0.35), "use_speaker_boost": True, "speed": cfg.get("speed", 1.06)}
    son_hata = None
    for model in [cfg.get("model", "eleven_v3"), "eleven_multilingual_v2"]:
        govde = {"text": metin, "model_id": model, "voice_settings": ayar, "language_code": "tr"}
        if model == "eleven_v3":
            govde["voice_settings"] = {k: v for k, v in ayar.items() if k in ("stability", "similarity_boost", "style", "use_speaker_boost")}
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",
            data=json.dumps(govde).encode(), headers={"xi-api-key": key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                cevap = json.load(r)
            break
        except urllib.error.HTTPError as e:
            son_hata = f"{model}: {e.code} {e.read()[:300]!r}"
            print("ElevenLabs hata", son_hata)
    else:
        raise SystemExit("ElevenLabs başarısız: " + str(son_hata))
    mp3 = os.path.join(klasor, "ses_ham.mp3")
    open(mp3, "wb").write(base64.b64decode(cevap["audio_base64"]))
    al = cevap.get("alignment") or cevap.get("normalized_alignment")
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    a_str = "".join(chars)
    # metin ofseti -> hizalama indeksi (model metni birebir döndürmeyebilir)
    sm = difflib.SequenceMatcher(None, metin, a_str, autojunk=False)
    harita = {}
    for blok in sm.get_matching_blocks():
        for k in range(blok.size):
            harita[blok.a + k] = blok.b + k
    def t_bul(i, yon):
        while 0 <= i < len(metin):
            if i in harita:
                return harita[i]
            i += yon
        return None
    kz = []
    for w, a, b in kelimeler_ve_ofset(metin):
        ia, ib = t_bul(a, 1), t_bul(b - 1, -1)
        if ia is None or ib is None or ib < ia:
            continue
        kz.append((w, a, st[ia], en[ib]))
    wav = os.path.join(klasor, "ses.wav")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ar", "44100", "-ac", "1", wav])
    z = zaman_kur(metin, sinirlar, kz, sure(wav))
    z["saglayici"] = f"elevenlabs:{voice}"
    return z


# ---------------------------------------------------------------- Azure (yedek)
def azure(is_, klasor):
    import html
    key, reg = os.environ["AZURE_TTS_KEY"], os.environ.get("AZURE_TTS_REGION", "eastus")
    ses_adi = is_.get("ses", {}).get("azure", "tr-TR-AhmetNeural")
    metin, sinirlar = birlesik_metin(is_)
    parcalar, kz, t0 = [], [], 0.0
    for i, sh in enumerate(is_["sahneler"]):
        ssml = (f"<speak version='1.0' xml:lang='tr-TR'><voice name='{ses_adi}'><prosody rate='+12%'>"
                f"{html.escape(sh['metin'])}</prosody></voice></speak>")
        mp3 = os.path.join(klasor, f"az{i}.mp3")
        r = subprocess.run(["curl", "-s", "-m", "40", "-o", mp3, "-w", "%{http_code}", "-X", "POST",
                            f"https://{reg}.tts.speech.microsoft.com/cognitiveservices/v1",
                            "-H", f"Ocp-Apim-Subscription-Key: {key}", "-H", "Content-Type: application/ssml+xml",
                            "-H", "X-Microsoft-OutputFormat: audio-24khz-96kbitrate-mono-mp3", "-H", "User-Agent: tarih",
                            "--data-binary", ssml], capture_output=True, text=True)
        assert r.stdout == "200", r.stdout
        w = os.path.join(klasor, f"az{i}.wav")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af",
             "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.12",
             "-ar", "44100", "-ac", "1", w])
        d = sure(w)
        parcalar.append(w)
        ws = kelimeler_ve_ofset(sh["metin"].strip())
        toplam_harf = sum(len(x[0]) + 1 for x in ws)
        t, of0 = t0, sinirlar[i][0]
        for kel, a, b in ws:
            dd = (d - 0.12) * (len(kel) + 1) / toplam_harf
            kz.append((kel, of0 + a, t, t + dd * 0.92))
            t += dd
        t0 += d
    lst = os.path.join(klasor, "az.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parcalar))
    wav = os.path.join(klasor, "ses.wav")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", wav])
    z = zaman_kur(metin, sinirlar, kz, sure(wav))
    z["saglayici"] = f"azure:{ses_adi}"
    return z


# ---------------------------------------------------------------- tahmini (önizleme)
def tahmini(is_, klasor, hiz=15.5):
    metin, sinirlar = birlesik_metin(is_)
    kz, t = [], 0.15
    for w, a, b in kelimeler_ve_ofset(metin):
        d = (len(w) + 1) / hiz
        kz.append((w, a, t, t + d * 0.9))
        t += d + (0.32 if w[-1] in ".!?" else 0.14 if w[-1] in ",;:" else 0)
    t += 0.4
    wav = os.path.join(klasor, "ses.wav")
    with wave.open(wav, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
        f.writeframes(b"\x00\x00" * int(44100 * t))
    z = zaman_kur(metin, sinirlar, kz, t)
    z["saglayici"] = "tahmini"
    return z


def ozet(is_):
    import hashlib
    metin, _ = birlesik_metin(is_)
    ek = json.dumps([is_.get("ses", {}), is_.get("eleven_muzik"), is_.get("eleven_sfx")], sort_keys=True, ensure_ascii=False)
    return hashlib.md5((metin + ek).encode()).hexdigest()


def _eleven_post(yol, govde, cikis, zaman_asimi=300):
    req = urllib.request.Request("https://api.elevenlabs.io" + yol, data=json.dumps(govde).encode(),
                                 headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=zaman_asimi) as r:
        veri = r.read()
    if len(veri) < 2000:
        raise RuntimeError("yanıt çok kısa: %r" % veri[:200])
    open(cikis, "wb").write(veri)


def ekstra(is_, klasor):
    """video.json'da istenirse ElevenLabs ile müzik (muzik_el.mp3) ve ses efektleri (sfx_<ad>.mp3) üretir.
    Plan/izin yetmezse ya da hata olursa atlar; kurgu.py sentetik müziğe döner."""
    sonuc = {"muzik": False, "sfx": [], "hata": []}
    mz = is_.get("eleven_muzik")
    if mz:
        cik = os.path.join(klasor, "muzik_el.mp3")
        govdeler = [{"prompt": mz["prompt"], "music_length_ms": int(mz.get("sure_ms", 60000)), "model_id": "music_v1", "force_instrumental": True},
                    {"prompt": mz["prompt"], "music_length_ms": int(mz.get("sure_ms", 60000))}]
        for g in govdeler:
            try:
                _eleven_post("/v1/music", g, cik); sonuc["muzik"] = True; break
            except urllib.error.HTTPError as e:
                sonuc["hata"].append(f"muzik {e.code} {e.read()[:200]!r}")
            except Exception as e:
                sonuc["hata"].append(f"muzik {e!r}")
    for sx in is_.get("eleven_sfx", []):
        cik = os.path.join(klasor, f"sfx_{sx['ad']}.mp3")
        try:
            _eleven_post("/v1/sound-generation", {"text": sx["text"], "duration_seconds": float(sx.get("sure", 4)),
                                                  "prompt_influence": float(sx.get("etki", 0.4))}, cik, 120)
            sonuc["sfx"].append(sx["ad"])
        except urllib.error.HTTPError as e:
            sonuc["hata"].append(f"sfx {sx['ad']} {e.code} {e.read()[:200]!r}")
        except Exception as e:
            sonuc["hata"].append(f"sfx {sx['ad']} {e!r}")
    print("ekstra:", sonuc)
    return sonuc


if __name__ == "__main__":
    klasor = sys.argv[1]
    mod = sys.argv[2] if len(sys.argv) > 2 else "eleven"
    is_ = oku(os.path.join(klasor, "video.json"))
    if mod == "kontrol":   # ses güncel mi? (iş akışı gereksiz yere kredi harcamasın)
        zp = os.path.join(klasor, "zaman.json")
        guncel = os.path.exists(zp) and os.path.exists(os.path.join(klasor, "ses_ham.mp3")) and oku(zp).get("ozet") == ozet(is_)
        print("guncel" if guncel else "yenile"); sys.exit(0)
    z = {"eleven": eleven, "azure": azure, "tahmini": tahmini}[mod](is_, klasor)
    z["ozet"] = ozet(is_)
    if mod == "eleven" and (is_.get("eleven_muzik") or is_.get("eleven_sfx")):
        z["ekstra"] = ekstra(is_, klasor)
    yaz(os.path.join(klasor, "zaman.json"), z)
    print(z["saglayici"], "süre", z["sure"], "sahneler", [round(s["e"] - s["s"], 1) for s in z["sahneler"]])
