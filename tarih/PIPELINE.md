# Belgesellerim – günlük Shorts hattı (otomatik görev talimatı)

Kanal: **Belgesellerim** (@Belgesellerim, kanal kimliği UCaf-xHOxP5Zd4ce84l4tbBQ; eski adları PanEdit, Tuhaf Tarih). DİKKAT: aynı hesapta ayrı bir "PanEdit" (@panedit2026) kanalı var, ona YÜKLEME. Başka birinin "Tuhaf Tarih" (@TuhafTarih) kanalı var: videolarda, açıklamalarda ve etiketlerde "Tuhaf Tarih" adını KULLANMA.
Niş (Kadir Bey 7 Kasım 2026): **savaş tarihinin tuhaf, şaşırtıcı ve gerçek hikâyeleri** (~%70) + diğer tuhaf tarih konuları (~%30). 40–58 sn dikey Shorts. Amaç: ABONE kazanmak.
Sahip: Kadir Pars. Ses: ElevenLabs "Zangess" (voice_id t8fOU8zfPVWFYN34BllH, Kadir Bey 7 Kasım 2026'da seçti).
Depo: xoqxs/tuhaf-tarih (bu dosya `tarih/PIPELINE.md`). Rapor Türkçe ve kısa. Şifre yazma. WebFetch yerine WebSearch + uygulama içi tarayıcı (navigate + get_page_text).

## 0) Başlangıç
- `git clone`/`pull` depo → `/home/claude/tuhaf-tarih`. `pip install --break-system-packages -q pillow numpy fonttools` (eksikse).
- `tarih/gunluk.md`'de bugünün tarihli "yayınlandı" kaydı varsa DUR (mesaj gönderme). Seri sütunu "ÖZEL" ile başlayan satırlar (özel gün videoları) SAYILMAZ: o gün günlük video yine de üretilir ve yayınlanır.
- Son 15 günlük satırını oku: seri, başlık kalıbı, kanca türü, yapı, duygu. Yeni video bunların hiçbirini bir önceki videoyla aynı kullanmaz.

## 1) Konu seçimi ve SEO araştırması
- `tarih/konular.md`'yi oku. Önce "SIRADAKİ" satırındaki konu bugünün konusudur (dün izleyiciye duyuruldu, DEĞİŞTİRME). Yoksa kurallara göre seç.
- Ardından YARININ konusunu seç (farklı seri, oran kuralı) ve "SIRADAKİ" satırına yaz; bugünkü video sonunda bunu duyuracak.
- SEO (zorunlu): uygulama içi tarayıcıda youtube.com sekmesinde javascript_tool ile öneri al:
  `fetch('https://suggestqueries-clients6.youtube.com/complete/search?client=youtube&ds=yt&hl=tr&gl=tr&q='+encodeURIComponent(q)).then(r=>r.text())` (JSONP; `t.match(/\((.*)\)/s)[1]` → JSON, [1][i][0] öneri). Konunun 3–5 farklı yazımını dene (kişi adı, olay adı, "neden ...", "tarihin en ..."). En çok tamamlanan/aranan ifadeyi başlığın başına, 2–3 yan ifadeyi açıklamaya ve etiketlere koy.
- Araştır: WebSearch ile en az 2 bağımsız güvenilir kaynak (ansiklopedi, müze, üniversite, büyük haber kuruluşu, TDV İA). Her rakam/tarih/isim iki kaynakta tutmalı; tutmayan girmez. Tartışmalı konuyu tartışmalı diye anlat. Savaş konularında vahşet/kan ayrıntısı YOK.

## 2) Metin (video.json → `tarih/isler/<YYYY-AA-GG>-<slug>/video.json`)
Örnekler: `tarih/isler/2026-11-07-hiroo-onoda/video.json`, `tarih/isler/1904-maratonu/video.json`. Alanlar: slug, seri, seri_rozet ("<Seri kısa adı> #<n>", n = günlükte o serinin kaçıncı videosu), duygu (gerilim|merak|epik|komik|huzun), tempo (1.12–1.18), kapak (2 satır, ≤22 karakter/satır), vurgu_sahneleri, ses, sahneler[{metin, etiket?, gorseller[]}], seo{baslik, aciklama, etiketler, hashtagler, kaynaklar}.
- **85–105 kelime** (hedef 40–58 sn). 9–12 sahne, sahne başı 1–2 kısa cümle (≤12 kelime). 60 sn'yi aşarsa kısalt ve yeniden seslendir.
- **İlk cümle kancadır**, ilk saniyede başlar, merak boşluğu açar ve başlıktaki anahtar kelimeyi içerir. Kanca türünü dönüştür: (a) şaşırtıcı sonuç önce, (b) soru, (c) "herkes X sanır ama", (d) rakam şoku, (e) sahnenin ortasından başlama.
- **Yapı dönüşümü** (son 3 videodan farklı): ters köşe final · kronolojik gerilim · "3 tuhaf ayrıntı" geri sayımı · efsane mi gerçek mi · iki tarafın karşılaştırması.
- **ABONE KAZANDIRAN KAPANIŞ** (zorunlu sıra, son 2 sahne):
  1. Hikâyenin en şaşırtıcı anından hemen sonra tek cümlelik kanal vaadi (her videoda FARKLI ifade): ör. "Savaşların böyle unutulmuş hikâyeleri için takipte kal." / "Her akşam bir savaş sırrı: kanala katıl." "Abone ol" kelimesini her videoda kullanma.
  2. Son sahne = YARIN duyurusu + yorum sorusu: "Yarın: <SIRADAKİ konunun merak uyandıran tek cümlesi>." ve kısa, iki taraflı bir soru. Görseli kart: `{"kart": {"ust": "yarın", "ana": "<2–3 kelime>", "alt": "<kısa merak>"}}`.
  3. Mümkünse son cümle ilk cümleye bağlansın (video başa sarınca akış kopmasın).
- **Anlaşılırlık:** İzleyici her cümleyi tek seferde, önceki bilgiye ihtiyaç duymadan anlamalı. İlginç bir ayrıntıyı kısaltırken bağlamını atma (kötü: "Suzuki'nin listesi tuhaftı: Onoda, panda, Kar Adamı." iyi: "Suzuki dünyayı dolaşıp sırayla üç şey arıyordu: Onoda, bir panda ve Kar Adamı."). Metni bitirince her sahneyi "bunu ilk kez duyan biri anlar mı?" diye oku.
- **Fahrettin Paşa dersi (8 Kasım 2026):** (1) Açılış cümlesi tek başına anlaşılmalı: "Paşa yatağına girer." gibi bağlamsız cümle YOK → "Medine teslim ediliyor ama komutanı yatağından kalkmayı reddediyor." (2) Geri sayım kullanacaksan sayı ile cümle karışmasın: "Üç kez emir gelir. Üç: …" YANLIŞ → "İlk emir … İkinci emir … Sonuncusu padişahtan gelir." (3) Kanal vaadi doğal Türkçe olsun: "Savaşların unutulmuş inatları için bu kanalda kal." gibi yapay cümle YOK → "Böyle unutulmuş savaş hikâyeleri için takipte kal." (4) Son sahnede "Yarın: …" ile yorum sorusu ayrı cümleler olsun ve soru bugünkü konuya dönsün; ikisini tek nefeste karıştırma. (5) Metni bitirince yüksek sesle okur gibi baştan sona bir kez daha oku; anlamı bozuk, yarım ya da tuhaf duran her cümleyi yeniden yaz.
- Yasak: dolgu ("arkadaşlar", "bildiğiniz gibi"), abartı ("ŞOK"), uydurma diyalog, kanıtsız iddia, şiddet ayrıntısında sansasyon, "Tuhaf Tarih" adı.
- Yıllar rakamla yazılabilir; diğer sayıları yazıyla yaz ("otuz iki derece"). Yabancı isimleri bir kez okunuşuna dikkat ederek yaz. Kart metinlerinde özel simge (→, •) kullanma.

## 2b) EDİTÖR KONTROLÜ (zorunlu, seslendirmeden önce)
`tarih/editor.md`'yi uygula: metni Agent aracıyla bağımsız bir alt ajana kontrol ettir; GEÇTİ almadan seslendirmeye GEÇME (en fazla 3 tur, olmazsa DUR ve bildir). Sonucu iş klasörüne `editor.txt` olarak kaydet.

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
a) KANALA GEÇ: https://www.youtube.com/channel_switcher → "Belgesellerim" (@Belgesellerim) öğesine GERÇEK tıkla (@panedit2026 DEĞİL; öğeyi JS ile "@Belgesellerim" metninden bul, tp-yt-paper-icon-item.click() de çalışır), 10 sn bekle. https://studio.youtube.com aç: adres /channel/UCaf-xHOxP5Zd4ce84l4tbBQ olmalı; değilse bir kez daha dene, olmazsa (g) ve DUR. Başka kanala ASLA yükleme.
b) navigate https://studio.youtube.com/channel/UCaf-xHOxP5Zd4ce84l4tbBQ/videos/upload?d=ud , 4 sn bekle; javascript_tool: `const r=await fetch(RAW_URL);const b=await r.blob();const f=new File([b],'<dosya>.mp4',{type:'video/mp4'});const inp=document.querySelector('input[type=file]');const dt=new DataTransfer();dt.items.add(f);inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));` 8 sn bekle.
c) 'ytcp-uploads-dialog #textbox[contenteditable=true]' kutularından ilki başlık, ikincisi açıklama (el.click(); el.focus(); document.execCommand('selectAll'); document.execCommand('insertText',false,metin)); textContent ile DOĞRULA.
d) "Hayır, çocuklar için hazırlanmamış" (name=VIDEO_MADE_FOR_KIDS_NOT_MFK). "Daha fazla göster" → değiştirilmiş/sentetik içerik: arşiv fotoğrafı + anlatıcı sesi için "Hayır" (yapay zekâ ile gerçekçi görsel kullanıldıysa "Evet"); etiketler (8–12): etiket kutusunu JS ile focus et, `computer type` ile virgülle ayrılmış yaz, sonra Enter bas (Enter olmadan etiket oluşmaz; ytcp-chip sayısıyla doğrula); dil Türkçe; kategori: `#category ytcp-dropdown-trigger` tıkla → "Eğitim" öğesi. Oynatma listesi: serinin adı (yoksa oluştur, 2 cümlelik özgün açıklama).
e) #next-button 3 kez (2,5 sn arayla) → tp-yt-paper-radio-button[name=PUBLIC] → #done-button. "İçeriğinizi kontrol etmeye devam ediyoruz" penceresi çıkarsa "Yine de yayınla" DEME: "Geri dön", kontroller bitene kadar bekle ("Kontroller tamamlandı. Sorun bulunmadı."), sonra #done-button. Telif/kısıtlama uyarısı varsa YAYINLAMA, bildir. Video bağlantısını al, İçerik listesinde "Herkese açık" olduğunu doğrula.
f) Yükleme sırasında captcha, "kimliğinizi doğrulayın", kanal uyarısı, yükleme sınırı → (g), DUR, bildir.
g) NOT (7 Kasım 2026, Windows): studio.youtube.com kök adresi Studio'da en son açılan kanala gider; geri dönüşte doğrudan https://studio.youtube.com/channel/UCETn8pkFCvCHQKpBAKnGXJw aç, "Hata" (403) görürsen 15 sn bekleyip aynı adresi tekrar aç (genelde 2. denemede açılır). Kanal değiştirme sayfasında doğru öğeye tıklandığını onay işaretinden (zoom) kontrol et.
g) GERİ DÖN (ZORUNLU, hata/DUR'da da): channel_switcher → "Döviz Radar" (@dovizradar) GERÇEK tıkla, 10 sn; önce https://studio.youtube.com (kök adres; doğrudan kanal adresi ilk denemede "Hata" verebilir, 7 Kasım 2026), sonra adresin /channel/UCETn8pkFCvCHQKpBAKnGXJw olduğunu doğrula → başlık "Kanal kontrol paneli" olmalı, "Hata" olmamalı (olmazsa raporun en üstüne "⚠ Döviz Radar kanalına geri dönülemedi"). Sonra yalnızca kendi sekmelerini kapat.

## 8) SEO
- Başlık: 1. adımda bulunan en çok aranan ifade başta, 40–65 karakter + " #shorts". Kalıbı dönüştür: "<Ünlü isim> Neden <soru>?" · "<Aranan ifade>: <tuhaf ayrıntı>" · "<Sayı> Yıl/Dakika/Kişi …" · "Herkes X Sanıyor Ama …". Son 15 başlıktan farklı. BÜYÜK HARF bağırma, emoji yığını, yanıltıcı vaat YOK.
- Açıklama: o videoya özgü 2–3 cümle (ana anahtar kelime ilk cümlede, 1–2 yan ifade doğal biçimde) → "Seri: <seri adı> #<n> – tüm bölümler oynatma listesinde" → "Yarın: <SIRADAKİ>" → "Kaynaklar:" 2 kaynak adı → görsel atıfları (BY/BY-SA: "Görsel: <yazar>, <lisans>, Wikimedia Commons"; PD: "Görseller: Wikimedia Commons, kamu malı") → 3–5 hashtag (konuya göre değişir).
- Etiketler 8–12, konuya özgü (öneri listesinden gelen ifadeler öncelikli); kanal etiketi "belgesellerim" bir kez. Alakasız popüler etiket YOK.
- Oynatma listesi: serinin tam adı (konular.md başlığı, harf öneki olmadan). Yoksa yükleme ekranındaki oynatma listesi seçicisinde "Yeni oynatma listesi" ile oluştur (herkese açık). Liste açıklamasını ilk kez oluştururken 2 cümle yaz.

## 9) Kayıt ve rapor
- `tarih/gunluk.md`'ye satır: | tarih | seri (#n) | konu | başlık | kanca türü | yapı | duygu | font/palet | bağlantı | yayınlandı |. `konular.md`'de konuyu `[x] YYYY-AA-GG` yap, "SIRADAKİ" satırını yarının konusuyla güncelle. Commit + push.
- Rapor (SendUserMessage, en fazla 3 satır): "🎬 Yeni Short: <başlık> – <bağlantı>" + seri/konu + "Döviz Radar kanalına geri dönüldü ✓". Hata varsa ne olduğu ve Kadir Bey'in ne yapması gerektiği.

## 10) HAFTALIK DERLEME (yalnızca pazar görevi)
- Son 7 günün `gunluk.md` kayıtlarındaki "yayınlandı" Shorts'ları (en az 4; azsa DUR ve bildir). Daha önce bir derlemeye girenler tekrar girmez (günlükte "derleme" satırlarına bak).
- `python3 tarih/pipeline/derleme.py tarih/v/derleme-YYYY-AA-GG.mp4 tarih/isler/<iş1> ... --tarih "<gün ay yıl>" --baslik "<başlık>"` → mp4 + `-bolumler.txt` + `-kapak.jpg`. Başlığı her hafta farklı ve SEO odaklı yaz: haftanın en çok izlenen Short'unun anahtar kelimesi başta (ör. "Savaş Bittiği Halde 29 Yıl Savaşan Asker ve Haftanın Diğer Tuhaf Hikâyeleri"). ≤70 karakter.
- Kontrol: 4–5 kare (giriş, 2 bölüm, kapanış) + kapak Read ile; ffprobe 1920x1080, ses var; ≤ 150 MB (fazlaysa GitHub'a koyma, DUR ve bildir).
- Yükleme: normal video (Short DEĞİL). Başlık; açıklama = 2–3 cümle özet + boş satır + `-bolumler.txt` içeriği (0:00 ile başlar) + her bölümün Short bağlantısı (gunluk'ten) + kaynak/atıf satırı + 3–5 hashtag. Küçük resim: kapak jpg'si (fetch → File → DataTransfer, küçük resim alanının input[type=file]'ı). Oynatma listesi: "Haftalık Derlemeler". Çocuklar için değil, kategori Eğitim, dil Türkçe, etiketler 10–15. Telif kontrolünü bekle (7e), sonra herkese açık.
- Uç ekran (isteğe bağlı): "Uç ekran" adımında "Abone ol" + "En son yükleme" öğeleri eklenebiliyorsa ekle; olmazsa atla.
- Günlüğe satır: | tarih | DERLEME | <bölüm sayısı> bölüm: <iş adları> | başlık | – | – | – | – | bağlantı | yayınlandı |. Derleme mp4'ünü yayından sonra depodan sil (kapak ve bölümler.txt kalsın).

## 11) HAFTALIK VERİ KONTROLÜ (pazar görevi, derlemeden sonra)
- Studio → İçerik → Shorts listesinden son 14 günün Shorts'larının görüntüleme sayılarını oku (get_page_text). Varsa Analytics'te "Abone kazanma" sekmesinden video başına abone sayısına bak.
- `tarih/gunluk.md` sonuna "### Haftalık özet YYYY-AA-GG" başlığıyla: en iyi 3 ve en zayıf 3 video (görüntüleme), hangi seri/kanca/başlık kalıbının iyi gittiği, 2–3 maddelik karar (ör. "G serisi iki kat izlendi → önümüzdeki hafta 2 G videosu").
- Kararı `konular.md` başına "Bu haftanın ağırlığı:" satırı olarak yaz; günlük görev konu seçerken buna uyar (oran ve seri kurallarını bozmadan).
- Rapor: 3 satır özet + derleme bağlantısı.

- **10 Kasım 2026 notu:** ElevenLabs anahtarında `music_generation` ve `sound_generation` izni yok (401). `eleven_muzik`/`eleven_sfx` sessizce atlanır; müzik sentetik üretilir, efekt gerekiyorsa numpy ile `sfx_<ad>.mp3` olarak iş klasörüne yazılır. Özel gün videosu günlük videoyu ENGELLEMEZ (kullanıcı kararı): aynı gün 15:07 görevi SIRADAKİ konuyu yine yayınlar. Kapak yazısı görselle çakışırsa `kapak_y` (varsayılan 330) ile yukarı alınır.
