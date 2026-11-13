# Editör kontrolü (seslendirmeden ÖNCE zorunlu)

Bu kontrolü metni yazan oturum değil, **bağımsız bir alt ajan (Agent aracı)** yapar; böylece yazar kendi metnini notlandırmamış olur.
Alt ajana yalnızca video.json'daki sahne metinlerini (sırayla, numaralı), kaynak notlarını ve bu dosyayı ver. Görevi: aşağıdaki listeye göre her sahneyi değerlendirip **GEÇTİ** ya da **DÜZELT** demek ve her sorun için sahne numarası + neden + önerilen yeni cümle yazmak.

## 0. Yazmadan önce: önce hikâye, sonra sahne (Kadir Bey 12 Kasım 2026)
Metin doğrudan sahne sahne yazılmaz. Önce 3–4 cümlelik düz bir **olay özeti** yazılır: kim, nerede, ne oldu, neden önemliydi, nasıl bitti. Sahneler bu özetin sırasını izler; özette olmayan bir olay sahnelere girmez. Her cümlenin **öznesi ve fiili açık** olur; iki ismi yan yana koyup anlamı dinleyiciye bırakan sıkıştırılmış ifadeler yazılmaz (Kötü: "Seyit'in topunda mermi vinci vurulur." → kim neyi vurdu belli değil. İyi: "Düşman ateşi, topun mermi kaldırma vincini bozar.").

## Kontrol listesi (bir madde bile tutmazsa DÜZELT)
1. **Tek başına anlaşılırlık:** Her cümle, konuyu ilk kez duyan biri tarafından tek seferde anlaşılıyor mu? Bağlamı verilmemiş eylem/kişi/nesne var mı? (Kötü: "Paşa yatağına girer." → neden, nerede belli değil.)
2. **Açılış:** İlk cümle merak uyandırıyor VE tek başına anlam taşıyor mu? Başlıktaki anahtar kelime ilk 2 cümlede geçiyor mu?
3. **Akış:** Sahneler arasında mantık atlaması, zaman karışıklığı, "bu/o" ile neyin kastedildiği belirsiz yer var mı?
4. **Sayma ve listeler:** Geri sayım/sıralama kullanıldıysa sayı ile cümle karışıyor mu? (Kötü: "Üç kez emir gelir. Üç: …")
5. **Doğal Türkçe:** Yüksek sesle okununca yapay, çeviri kokan ya da anlamı bozuk cümle var mı? (Kötü: "Savaşların unutulmuş inatları için bu kanalda kal.") Devrik/eksik cümle, yanlış ek, yanlış kelime seçimi?
6. **Kapanış:** Kanal vaadi doğal ve tek cümle mi? Yorum sorusu bugünkü konuya mı dönüyor? "Yarın: …" ayrı bir cümle mi ve tek başına anlaşılıyor mu?
7. **Doğruluk:** Her rakam, tarih, isim ve alıntı verilen kaynaklarla uyumlu mu? Kaynakta olmayan ayrıntı, abartı ya da kesinmiş gibi sunulan tartışmalı bilgi var mı? Doğrudan alıntı ("…" dedi) kaynakta gerçekten öyle mi?
8. **Seslendirme:** ElevenLabs'in yanlış okuyabileceği kısaltma, rakam (yıllar hariç), parantez, simge var mı? Yabancı isimler Türkçe okunuşa uygun mu?
9. **Süre:** 40–50 kelime arası mı (25–35 sn)? İlk cümle rakamlı şok iddia mı, tarih/yerle mi açılıyor (açılıyorsa DÜZELT)?
10. **Saygı ve uygunluk:** Kan/vahşet ayrıntısı, aşağılayıcı ifade, siyasi taraf tutma var mı? Türk/Osmanlı kahramanı küçümser gibi duran bir açı var mı?
11. **Çift anlam:** Bir cümle iki farklı şekilde anlaşılabiliyor mu? Özellikle isim tamlamaları ve yüklem: "mermi vinci vurulur" hem "vinç vuruldu" hem "mermi vinci vurdu" diye okunabilir → DÜZELT. Her sahneyi yüksek sesle, önceki ve sonraki cümleyle birlikte oku.
12. **Neden-sonuç:** Her olayın nedeni ya da sonucu söyleniyor mu? Dinleyici "bu neden önemli?" diye sormak zorunda kalıyor mu?

## Akış
- DÜZELT → yazar önerileri uygular (ya da daha iyisini yazar) → alt ajana yeniden gönderir. En fazla 3 tur.
- 3 turda GEÇTİ alamazsa: videoyu YAYINLAMA, DUR ve Kadir Bey'e sorunlu sahneleri bildir.
- GEÇTİ alınca sonucu iş klasörüne `editor.txt` olarak kaydet (tur sayısı + son karar), sonra seslendirmeye geç.

## Geri anlatım testi (editör GEÇTİ dedikten sonra, zorunlu)
Editörden bağımsız, **ikinci bir alt ajana** (Agent aracı) yalnızca sahne metinlerini ver. Kaynak, konu adı ya da başlık verme. Ondan iki şey iste:
1. Hikâyeyi kendi cümleleriyle 3 cümlede anlatması.
2. "Takıldığım, iki kez okumak zorunda kaldığım ya da anlamadığım cümleler" listesi (yoksa "yok").
Onun özeti senin olay özetinle aynı değilse ya da takıldığı bir cümle varsa, o cümleleri düzelt ve teste yeniden gönder (en fazla 2 tur). Test geçmeden seslendirme yapılmaz. Sonucu `editor.txt`'ye "Geri anlatım: geçti (n. tur)" olarak ekle.

## Seslendirmeden sonra ikinci kontrol
- zaman.json'daki kelimeleri birleştirip metinle karşılaştır: eksik/fazla kelime, yanlış okunan isim şüphesi varsa (eşleşmeyen kelimeler) düzelt ve yeniden seslendir.
