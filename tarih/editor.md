# Editör kontrolü (seslendirmeden ÖNCE zorunlu)

Bu kontrolü metni yazan oturum değil, **bağımsız bir alt ajan (Agent aracı)** yapar; böylece yazar kendi metnini notlandırmamış olur.
Alt ajana yalnızca video.json'daki sahne metinlerini (sırayla, numaralı), kaynak notlarını ve bu dosyayı ver. Görevi: aşağıdaki listeye göre her sahneyi değerlendirip **GEÇTİ** ya da **DÜZELT** demek ve her sorun için sahne numarası + neden + önerilen yeni cümle yazmak.

## Kontrol listesi (bir madde bile tutmazsa DÜZELT)
1. **Tek başına anlaşılırlık:** Her cümle, konuyu ilk kez duyan biri tarafından tek seferde anlaşılıyor mu? Bağlamı verilmemiş eylem/kişi/nesne var mı? (Kötü: "Paşa yatağına girer." → neden, nerede belli değil.)
2. **Açılış:** İlk cümle merak uyandırıyor VE tek başına anlam taşıyor mu? Başlıktaki anahtar kelime ilk 2 cümlede geçiyor mu?
3. **Akış:** Sahneler arasında mantık atlaması, zaman karışıklığı, "bu/o" ile neyin kastedildiği belirsiz yer var mı?
4. **Sayma ve listeler:** Geri sayım/sıralama kullanıldıysa sayı ile cümle karışıyor mu? (Kötü: "Üç kez emir gelir. Üç: …")
5. **Doğal Türkçe:** Yüksek sesle okununca yapay, çeviri kokan ya da anlamı bozuk cümle var mı? (Kötü: "Savaşların unutulmuş inatları için bu kanalda kal.") Devrik/eksik cümle, yanlış ek, yanlış kelime seçimi?
6. **Kapanış:** Kanal vaadi doğal ve tek cümle mi? Yorum sorusu bugünkü konuya mı dönüyor? "Yarın: …" ayrı bir cümle mi ve tek başına anlaşılıyor mu?
7. **Doğruluk:** Her rakam, tarih, isim ve alıntı verilen kaynaklarla uyumlu mu? Kaynakta olmayan ayrıntı, abartı ya da kesinmiş gibi sunulan tartışmalı bilgi var mı? Doğrudan alıntı ("…" dedi) kaynakta gerçekten öyle mi?
8. **Seslendirme:** ElevenLabs'in yanlış okuyabileceği kısaltma, rakam (yıllar hariç), parantez, simge var mı? Yabancı isimler Türkçe okunuşa uygun mu?
9. **Süre:** 85–105 kelime arası mı?
10. **Saygı ve uygunluk:** Kan/vahşet ayrıntısı, aşağılayıcı ifade, siyasi taraf tutma var mı?

## Akış
- DÜZELT → yazar önerileri uygular (ya da daha iyisini yazar) → alt ajana yeniden gönderir. En fazla 3 tur.
- 3 turda GEÇTİ alamazsa: videoyu YAYINLAMA, DUR ve Kadir Bey'e sorunlu sahneleri bildir.
- GEÇTİ alınca sonucu iş klasörüne `editor.txt` olarak kaydet (tur sayısı + son karar), sonra seslendirmeye geç.

## Seslendirmeden sonra ikinci kontrol
- zaman.json'daki kelimeleri birleştirip metinle karşılaştır: eksik/fazla kelime, yanlış okunan isim şüphesi varsa (eşleşmeyen kelimeler) düzelt ve yeniden seslendir.
