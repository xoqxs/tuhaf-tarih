# Tuhaf Tarih – günlük Shorts hattı (otomatik görev talimatı)

Kanal: PanEdit (@Belgesellerim, kanal kimliği UCaf-xHOxP5Zd4ce84l4tbBQ). Niş: **tarihin tuhaf ama gerçek olayları**, 35–55 sn dikey Shorts.
Sahip: Kadir Pars. Ses: ElevenLabs "Zangess" (voice_id t8fOU8zfPVWFYN34BllH, Kadir Bey 7 Kasım 2026'da seçti).
Depo: xoqxs/tuhaf-tarih (bu dosya `tarih/PIPELINE.md`). Rapor Türkçe ve kısa. Şifre yazma. WebFetch yerine WebSearch + uygulama içi tarayıcı (navigate + get_page_text).

## 0) Başlangıç
- `git clone`/`pull` depo → `/home/claude/tuhaf-tarih`. `pip install --break-system-packages -q pillow numpy fonttools` (eksikse).
- `tarih/gunluk.md`'de bugünün tarihli "yayınlandı" kaydı varsa DUR (mesaj gönderme).
- Son 15 günlük satırını oku: seri, başlık kalıbı, kanca türü, yapı, duygu. Yeni video bunların hiçbirini bir önceki videoyla aynı kullanmaz.

## 1) Konu seçimi
- `tarih/konular.md`'den seç (kurallar o dosyanın başında). Seri dönüşümü: aynı seri art arda gelmez; 7 günde bir seriden en fazla 2.
- Konu YouTube'da aranıyor mu? youtube.com arama kutusuna konunun Türkçe anahtar kelimesini yaz, öneri listesini oku (get_page_text). Önerilerdeki ifadeyi başlıkta kullan.
- Araştır: WebSearch ile en az 2 bağımsız güvenilir kaynak (ansiklopedi, müze, üniversite, büyük haber kuruluşu, TDV İA). Her rakam/tarih/isim iki kaynakta tutmalı; tutmayan girmez. Tartışmalı konuyu tartışmalı diye anlat.

## 2) Metin (video.json → `tarih/isler/<YYYY-AA-GG>-<slug>/video.json`)
Örnek: `tarih/isler/1904-maratonu/video.json`. Alanlar: slug, seri, duygu (gerilim|merak|epik|komik|huzun), kapak (2 satır, ≤22 karakter/satır), vurgu_sahneleri, ses, sahneler[{metin, etiket?, gorseller[]}], seo{baslik, aciklama, etiketler, hashtagler, kaynaklar}.
- Toplam 95–140 kelime (≈35–55 sn). 8–12 sahne, sahne başı 1–2 kısa cümle (≤12 kelime).
- **İlk cümle kancadır**, ilk saniyede başlar ve merak boşluğu açar. Kanca türünü dönüştür: (a) şaşırtıcı sonuç önce, (b) soru, (c) "herkes X sanır ama", (d) rakam şoku, (e) sahnenin ortasından başlama.
- **Yapı dönüşümü** (son 3 videodan farklı): ters köşe final · kronolojik gerilim · "3 tuhaf ayrıntı" geri sayımı · efsane mi gerçek mi · iki kişinin karşılaştırması.
- Son cümle: soru ya da sonraki merak (yorum çağrısı en fazla 1 kez; "abone ol" en fazla 1 kez, her videoda değil; aynı kapanış cümlesi tekrar YOK).
- Yasak: dolgu ("arkadaşlar", "bildiğiniz gibi"), abartı ("ŞOK"), uydurma diyalog, kanıtsız iddia, ölüm/şiddet ayrıntısında sansasyon.
- Yıllar rakamla yazılabilir; diğer sayıları yazıyla yaz ("otuz iki derece"). Yabancı isimleri bir kez okunuşuna dikkat ederek yaz.

## 3) Görseller
- Önce gerçek arşiv: `python3 tarih/pipeline/wm.py s "arama" 10` → `wm.py i "File:..." tarih/isler/<iş>/img/ad.jpg`. Yalnızca PD/CC0/CC BY/CC BY-SA (wm.py denetler). Atıflar `atif.json`'a yazılır; BY/BY-SA olanlar açıklamaya.
- Görüntü en fazla ~3 sn ekranda kalır (kurgu otomatik böler); sahne başına 1–3 görsel. Bir videoda aynı görsel en fazla 2 kez (ikincisi otomatik yakın plan olur). `kullanilan-gorseller.txt`'de olanı tekrar kullanma.
- Fotoğraf yoksa yazı kartı: `{"kart": {"ust": "...", "ana": "...", "alt": "..."}}` (ana ≤12 karakter). Videonun en fazla 1/3'ü kart olsun.
- Gerçek kişinin fotoğrafı yalnızca o kişi olduğu kaynakta açıkça yazıyorsa. Yapay zekâ görseli bu hatta yok; eklenirse YouTube'da "değiştirilmiş/sentetik içerik: Evet" seçilir.
- `duzen` isteğe bağlı (doldur|bulanik|cerceve|detay); yüzlü dikey fotoğrafta `odak` ver ([x,y], 0–1).

## 4) Seslendirme (ElevenLabs – GitHub Actions)
- Bulut oturumu ElevenLabs'e erişemez. video.json'u commit + push et → `tarih-ses.yml` iş akışı `ses_ham.mp3` + `zaman.json` üretip geri gönderir (~1–2 dk).
- 30 sn arayla `git pull`, en fazla 8 dk bekle; `zaman.json` içinde "elevenlabs" görünmeli. İş akışı hata verdiyse `gh run list` çalışmaz; GitHub sayfasını tarayıcıda aç (github.com/xoqxs/tuhaf-tarih/actions) ve hatayı oku → DUR ve bildir (ElevenLabs kotası/anahtarı olabilir). Yedek ses KULLANMA, kanalın sesi değişmesin.

## 5) Kurgu ve kontrol
- `python3 tarih/pipeline/kurgu.py tarih/isler/<iş> tarih/v/<iş>.mp4 --gecmis tarih/stiller.json` (stil her videoda farklı seçilir: font, renk paleti, renk tonu, altyazı konumu, hareket; son 3 videoyla aynı font+palet yok).
- Kontrol (ZORUNLU): 1, 4, 8, … saniyelerden kare al, temas sayfası yap ve Read ile bak: altyazı okunuyor ve taşmıyor, kapak 2 satır, yüz/konu kadrajda, kart yazıları sığıyor. Sorun varsa video.json'da düzen/odak/kart değiştir, yeniden üret.
- `ffmpeg -i ... -af silencedetect=noise=-38dB:d=0.6 -f null -` ile sessiz boşluk yok; süre 30–60 sn; ffprobe 1080x1920, ses var; ≤40 MB.
- Sesi dinleyemezsin: zaman.json'daki kelimelerin video.json metniyle uyuştuğunu kontrol et (kelime sayısı farkı ≤%5).

## 6) GitHub
- mp4'ü `tarih/v/` altına koy; iş klasörü (video.json, zaman.json, ses_ham.mp3, atif.json, img/) + stiller.json + kullanilan-gorseller.txt commit + push. Raw URL (https://raw.githubusercontent.com/xoqxs/tuhaf-tarih/main/tarih/v/<dosya>) curl ile 200.
- Depo küçük kalsın: yayından sonra 14 günden eski `tarih/v/*.mp4` ve iş klasörlerindeki `img/` silinir (video.json ve atif.json kalır).

## 7) YouTube yükleme (uygulama içi tarayıcı, kendi sekmen; Baby Collective görevindeki çalışan yöntem)
KANAL ÇAKIŞMASI: Aynı Google hesabında Döviz Radar (UCETn8pkFCvCHQKpBAKnGXJw) ve Baby Collective var; Döviz Radar görevleri Studio'da Döviz Radar'ın etkin olmasını bekler. Başlarken tabs_context'te studio.youtube.com sekmesi açıksa 10 dk bekle (en fazla 3 kez), hâlâ açıksa DUR ve bildir.
a) KANALA GEÇ: https://www.youtube.com/channel_switcher → "PanEdit" (@Belgesellerim) öğesine GERÇEK tıkla, 10 sn bekle. https://studio.youtube.com aç: adres /channel/UCaf-xHOxP5Zd4ce84l4tbBQ olmalı; değilse bir kez daha dene, olmazsa (g) ve DUR. Başka kanala ASLA yükleme.
b) navigate https://studio.youtube.com/channel/UCaf-xHOxP5Zd4ce84l4tbBQ/videos/upload?d=ud , 4 sn bekle; javascript_tool: `const r=await fetch(RAW_URL);const b=await r.blob();const f=new File([b],'<dosya>.mp4',{type:'video/mp4'});const inp=document.querySelector('input[type=file]');const dt=new DataTransfer();dt.items.add(f);inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));` 8 sn bekle.
c) 'ytcp-uploads-dialog #textbox[contenteditable=true]' kutularından ilki başlık, ikincisi açıklama (el.click(); el.focus(); document.execCommand('selectAll'); document.execCommand('insertText',false,metin)); textContent ile DOĞRULA.
d) "Hayır, çocuklar için hazırlanmamış" (name=VIDEO_MADE_FOR_KIDS_NOT_MFK). "Daha fazla göster" → değiştirilmiş/sentetik içerik: arşiv fotoğrafı + anlatıcı sesi için "Hayır" (yapay zekâ ile gerçekçi görsel kullanıldıysa "Evet"); etiketler (8–12); dil Türkçe; kategori Eğitim. Oynatma listesi: serinin adı (yoksa oluştur, 2 cümlelik özgün açıklama).
e) #next-button 3 kez (2,5 sn arayla) → tp-yt-paper-radio-button[name=PUBLIC] → #done-button. Telif/kısıtlama uyarısı varsa YAYINLAMA, bildir. Video bağlantısını al, İçerik listesinde "Herkese açık" olduğunu doğrula.
f) Yükleme sırasında captcha, "kimliğinizi doğrulayın", kanal uyarısı, yükleme sınırı → (g), DUR, bildir.
g) GERİ DÖN (ZORUNLU, hata/DUR'da da): channel_switcher → "Döviz Radar" (@dovizradar) GERÇEK tıkla, 10 sn; https://studio.youtube.com/channel/UCETn8pkFCvCHQKpBAKnGXJw → başlık "Kanal kontrol paneli" olmalı, "Hata" olmamalı (olmazsa raporun en üstüne "⚠ Döviz Radar kanalına geri dönülemedi"). Sonra yalnızca kendi sekmelerini kapat.

## 8) SEO
- Başlık: aranan ifade başta, 40–65 karakter + " #shorts". Kalıbı dönüştür (soru · "X: Y" · rakamlı · "Herkes X sanıyor ama"); son 15 başlıktan farklı. BÜYÜK HARF bağırma, emoji yığını, yanıltıcı vaat YOK.
- Açıklama: o videoya özgü 2–3 cümle (ana anahtar kelime ilk cümlede) → "Kaynaklar:" 2 kaynak adı → BY/BY-SA görsel atıfları ("Görsel: <yazar>, <lisans>, Wikimedia Commons"; PD için "Görseller: Wikimedia Commons, kamu malı") → 3–5 hashtag (konuya göre değişir; #shorts dahil değil, başlıkta var).
- Etiketler 8–12, konuya özgü; kanal etiketi "tuhaf tarih" bir kez. Alakasız popüler etiket YOK.

## 9) Kayıt ve rapor
- `tarih/gunluk.md`'ye satır: | tarih | seri | konu | başlık | kanca türü | yapı | duygu | font/palet | bağlantı | yayınlandı |. `konular.md`'de konuyu [x] yap. Commit + push.
- Rapor (SendUserMessage, en fazla 3 satır): "📜 Yeni Short: <başlık> – <bağlantı>" + seri/konu + "Döviz Radar kanalına geri dönüldü ✓". Hata varsa ne olduğu ve Kadir Bey'in ne yapması gerektiği.
