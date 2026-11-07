# Belgesellerim – otomatik YouTube Shorts hattı

Belgesellerim (@Belgesellerim) kanalı için savaş tarihinin tuhaf ve gerçek hikâyeleri (Shorts + haftalık derleme).

- `tarih/PIPELINE.md` – günlük görevin adım adım talimatı (konu, doğrulama, metin, görsel, ses, kurgu, SEO, yükleme)
- `tarih/konular.md` – seri bazlı konu havuzu (tekrar yok)
- `tarih/pipeline/` – `ses.py` (ElevenLabs / yedekler), `kurgu.py` (kurgu motoru), `kare.py`, `muzik.py`, `wm.py` (Wikimedia arşivi)
- `.github/workflows/tarih-ses.yml` – ElevenLabs seslendirmesi (secret: `ELEVENLABS_API_KEY`)
- `tarih/v/` – yüklenecek videolar · `tarih/gunluk.md` – yayın günlüğü

Fontlar: Google Fonts (SIL Open Font License). Görseller: Wikimedia Commons (kamu malı / CC lisanslı, atıflar `atif.json`).
