"""Videoya özel fon müziği + geçiş sesleri (telifsiz, her videoda farklı).

python3 muzik.py SURE CIKIS.wav --duygu gerilim --tohum slug --kesmeler 2.1,4.8 --vurgular 21.3
duygular: gerilim, merak, epik, komik, huzun
"""
import argparse, hashlib, wave
import numpy as np

SR = 44100


def lp(x, a):  # tek kutuplu alçak geçiren
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y


def lp_hizli(x, k):
    # hareketli ortalama ile hızlı yumuşatma (uzun sinyaller için)
    k = max(1, int(k)); c = np.cumsum(np.insert(x, 0, 0.0))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate([y, np.full(k - 1, y[-1] if len(y) else 0)])


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def env_adsr(n, a=0.01, r=0.25):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-3))
    return e


OLCEK = {"minor": [0, 2, 3, 5, 7, 8, 10], "major": [0, 2, 4, 5, 7, 9, 11],
         "frig": [0, 1, 3, 5, 7, 8, 10], "penta": [0, 3, 5, 7, 10]}


def uret(sure, duygu, tohum):
    rng = np.random.default_rng(int(hashlib.md5(tohum.encode()).hexdigest()[:8], 16))
    n = int(SR * sure); t = np.arange(n) / SR
    y = np.zeros(n)
    kok = 55.0 * 2 ** (int(rng.integers(0, 12)) / 12)
    ayar = {
        "gerilim": dict(bpm=(70, 92), olcek="frig", dron=0.5, nabiz=0.35, tik=0.25, pluck=0.15, davul=0.2),
        "merak": dict(bpm=(88, 108), olcek="penta", dron=0.25, nabiz=0.1, tik=0.15, pluck=0.45, davul=0.25),
        "epik": dict(bpm=(80, 100), olcek="minor", dron=0.45, nabiz=0.3, tik=0.0, pluck=0.2, davul=0.6),
        "komik": dict(bpm=(110, 128), olcek="major", dron=0.1, nabiz=0.0, tik=0.2, pluck=0.6, davul=0.35),
        "huzun": dict(bpm=(64, 80), olcek="minor", dron=0.4, nabiz=0.0, tik=0.0, pluck=0.35, davul=0.0),
    }[duygu]
    bpm = float(rng.integers(*ayar["bpm"])); vur = 60 / bpm
    olc = OLCEK[ayar["olcek"]]
    # akor ilerleyişi (derece listesi), 2 ölçüde bir değişir
    prog = [list(rng.choice([0, 0, 3, 5, 4, 6], 4))]
    prog = [int(x) % len(olc) for x in prog[0]]
    bar = vur * 4
    # 1) dron / pad
    if ayar["dron"]:
        for k, d in enumerate(prog):
            pass
        idx = ((t // (bar * 2)).astype(int)) % len(prog)
        f0 = kok * 2 ** (np.array([olc[d] for d in prog])[idx] / 12)
        ph = np.cumsum(f0) / SR
        pad = (2 * (ph % 1) - 1) * 0.5 + (2 * ((ph * 1.5) % 1) - 1) * 0.3 + (2 * ((ph * 2.003) % 1) - 1) * 0.25
        pad = lp_hizli(pad, 60)
        pad *= 0.6 + 0.4 * np.sin(2 * np.pi * t / (bar * 2))
        y += pad * ayar["dron"]
    # 2) bas nabzı (sekizlik)
    if ayar["nabiz"]:
        adim = vur / 2; m = ((t % adim) / adim)
        idx = ((t // (bar * 2)).astype(int)) % len(prog)
        f0 = kok * 2 ** (np.array([olc[d] for d in prog])[idx] / 12)
        y += np.sin(2 * np.pi * np.cumsum(f0) / SR) * np.exp(-m * 5) * ayar["nabiz"]
    # 3) pluck melodisi
    if ayar["pluck"]:
        adim = vur / (2 if rng.random() < 0.6 else 1)
        k = 0.0
        while k < sure - 0.3:
            if rng.random() < 0.72:
                der = int(rng.integers(0, len(olc))); okt = int(rng.choice([2, 3, 3, 4]))
                f = kok * okt * 2 ** (olc[der] / 12)
                L = int(SR * min(0.6, sure - k)); i0 = int(k * SR)
                tt = np.arange(L) / SR
                nota = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * env_adsr(L, 0.004, 0.18)
                y[i0:i0 + L] += nota[: n - i0] * ayar["pluck"] * 0.6
            k += adim
    # 4) tik-tak / hi-hat
    if ayar["tik"]:
        adim = vur / 2; m = (t % adim) / adim
        y += rng.standard_normal(n) * np.exp(-m * 40) * ayar["tik"] * 0.35
    # 5) davul (kick + snare)
    if ayar["davul"]:
        b = (t % vur) / vur
        kick = np.sin(2 * np.pi * (48 + 110 * np.exp(-b * 20)) * (t % vur)) * np.exp(-b * 8)
        y += kick * ayar["davul"]
        b2 = ((t + vur) % (vur * 2)) / (vur * 2)
        y += rng.standard_normal(n) * np.exp(-b2 * 26) * ayar["davul"] * 0.25
    y /= max(1e-6, np.max(np.abs(y)))
    f = SR // 2
    y[:f] *= np.linspace(0, 1, f); y[-SR:] *= np.linspace(1, 0, SR)
    return y * 0.8, bpm


def whoosh(rng, L=0.45):
    n = int(SR * L); x = rng.standard_normal(n)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    x = lp_hizli(x, 6) * e
    return x / max(1e-6, np.max(np.abs(x)))


def darbe(L=1.4):
    n = int(SR * L); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * (40 + 60 * np.exp(-t * 12)) * t) * np.exp(-t * 3.2)
    x += np.random.default_rng(1).standard_normal(n) * np.exp(-t * 18) * 0.4
    return x / np.max(np.abs(x))


def yaz_wav(yol, y):
    y = np.clip(y, -1, 1)
    with wave.open(yol, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("sure", type=float); ap.add_argument("cikis")
    ap.add_argument("--duygu", default="merak"); ap.add_argument("--tohum", default="x")
    ap.add_argument("--kesmeler", default=""); ap.add_argument("--vurgular", default="")
    ap.add_argument("--efekt_cikis", default="")
    a = ap.parse_args()
    m, bpm = uret(a.sure, a.duygu, a.tohum)
    yaz_wav(a.cikis, m)
    # efekt izi ayrı yazılır (kurgu.py ayrı seviyede karıştırır)
    if a.efekt_cikis:
        rng = np.random.default_rng(7)
        ef = np.zeros(int(SR * a.sure))
        for k in [float(x) for x in a.kesmeler.split(",") if x]:
            w = whoosh(rng, float(rng.uniform(0.3, 0.5))) * 0.55
            i0 = max(0, int((k - 0.18) * SR)); ef[i0:i0 + len(w)] += w[: len(ef) - i0]
        for k in [float(x) for x in a.vurgular.split(",") if x]:
            d = darbe() * 0.9; i0 = int(k * SR); ef[i0:i0 + len(d)] += d[: len(ef) - i0]
        yaz_wav(a.efekt_cikis, ef * 0.9)
    print("muzik", a.duygu, int(bpm))
