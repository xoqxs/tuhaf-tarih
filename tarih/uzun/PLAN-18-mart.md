# Uzun belgesel #1 – 18 Mart 1915 (plan, 17 Kasım 2026; Kadir Bey "Olur plan çıkar")

Durum: PLAN (Kadir Bey'in konu/uzunluk/gün onayı bekleniyor). Günlük Shorts görevi bundan etkilenmez.

## Neden bu konu
- 14 günün en iyileri Türk kahramanı/ünlü isim videoları (Seyit 1.282). Nusret ve Seyit Shorts'ları hazır "giriş kapısı".
- Rakipler (TRT, İletişim Başkanlığı, Kings and Generals) genel anlatım yapıyor; bizim açımız: "Dünyanın en güçlü donanması neden geçemedi?" sorusunu 5 az bilinen ayrıntıyla, hikâye gibi anlatmak.

## Format
- 16:9, 1920x1080, 9–11 dk, ~1.300–1.500 kelime seslendirme (Zangess, eleven_v3), 5 bölüm + bölüm zaman damgaları.
- Millî kahramanlar yalnızca olumlu ve saygılı. Belgeye dayanmayan sahne yok; "anlatılana göre" gereken yerlerde kaynak açıklamada.

## Akış
0. Kanca (0:00–0:40): 18 Mart sabahı Boğaz'a giren dev filo; günün sonunda 3 zırhlı batık. "Nasıl?"
1. Neden Çanakkale? (≈1,5 dk): İstanbul hedefi, Rusya'ya yol, Şubat–Mart bombardımanları.
2. Görünmez duvar (≈2 dk): mayın hatları, tabyalar, mayın tarama girişimlerinin başarısızlığı.
3. Nusret'in sabahı (≈2 dk): 8 Mart, Erenköy Koyu, 26 mayın, bulunamayışları (harita animasyonu).
4. 18 Mart, saat saat (≈3 dk): Bouvet, Irresistible, Ocean; ağır hasar alanlar; kıyı topçusunun payı; Seyit Onbaşı'nın mermi taşıması (olumlu, saygılı).
5. Sonuç (≈1 dk): filo çekilir, kara savaşına geçiş (25 Nisan) → bir sonraki uzun belgeselin kancası; abone çağrısı yalnızca sonda.

## Üretim (mevcut boru hattı + eklenecekler)
- Metin: bölüm bölüm yaz → her bölüm editör + geri anlatım (tarih/editor.md) → tam metin bir kez daha.
- Görsel: Wikimedia kamu malı 1915 fotoğrafları (AWM/IWM arşivleri, lisans kontrolü), harita.py ile 3–4 harita (Boğaz, mayın hatları, Erenköy, filo hattı), 8–12 Wan klibi (bayrak/yazı/anakronizm kontrolü), bilgi kartları.
- Ses: tarih-ses.yml uzun metin için bölüm bölüm (ElevenLabs kredisi ≈ 13–15 bin karakter; bakiye okunamadığı için önce Kadir Bey kontrol eder).
- Kurgu: YENİ `tarih/pipeline/uzun.py` (kurgu.py'nin yatay sürümü; derleme.py'deki 1920x1080 yapısı temel) – bölüm başlık kartları, alt yazı, müzik ducking, chapters.txt.
- Kontrol: her bölümden 3 kare + kapak Read; ffprobe; ≤150 MB.

## YouTube
- Başlık adayları (≤70): "18 Mart 1915: Dünyanın En Güçlü Donanması Neden Geçemedi?" / "Çanakkale Geçilmez: 18 Mart'ı Değiştiren 5 Az Bilinen Olay".
- Kapak: dev zırhlı + duman + büyük "GEÇEMEDİ" yazısı (özel küçük resim hesap doğrulaması ister; yoksa en iyi kare).
- Açıklama: soru ilk satırda, bölüm zaman damgaları, kaynaklar, "yapay zekâ ile canlandırılmış sahneler" notu; değiştirilmiş içerik: Evet; oynatma listesi "Uzun Belgeseller".
- Shorts köprüsü: Nusret, Seyit ve yeni 1–2 kesitin "İlgili video" alanına bu belgesel; sabit yorum.
- Yayın: cumartesi 20:00 (pazar derlemesiyle çakışmasın).

## Takvim (onay sonrası)
- Gün 1: kaynaklar + bölüm metinleri + editör/geri anlatım.
- Gün 2: ses + görseller/haritalar + uzun.py.
- Gün 3: kurgu, kare kontrolü, düzeltme.
- Gün 4 (cumartesi): yükleme, planlama, Shorts bağlantıları.

## Ölçüm (yayından 7 gün sonra, pazar veri kontrolüne eklenir)
- Ortalama izlenme süresi/yüzdesi, kazanılan abone, Shorts'tan gelen trafik. Hedef: ≥%35 ortalama izlenme, ≥10 abone.
- Tutarsa: haftada 1 uzun belgesel (sıradaki: 25 Nisan çıkarması / Sarıkamış / Kut'ül-Amare).
