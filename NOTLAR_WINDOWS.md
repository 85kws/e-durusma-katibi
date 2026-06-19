# E-Duruşma Katibi — Kullanım (Windows)

Sesle dikte: konuştuğun, o an açık olan yazı programına (Word/UYAP/Not Defteri — fark etmez) yazılır.
**Tek uygulama** — mevzuat penceresi de içinden açılır. Model gömülü → **tamamen offline** (internet gerekmez).

> 🔒 Açılışta **şifre** sorar. Varsayılan: **1234**.

## ÇALIŞTIRMA
1. `E-DurusmaKatibi` klasörünü Masaüstüne kopyala.
2. İçindeki **`E-DurusmaKatibi.exe`**'ye çift tıkla. (İlk açılış biraz yavaş — kendini açıyor, normal.)
3. Şifre: **1234**.
4. **Mikrofon** listesinden cihazını seç → **🎤 Mikrofon Testi** → "✅ ÇALIŞIYOR" görmelisin (konuş).
5. **Word** (veya başka editör) aç, içine tıkla.
6. **▶ Başlat** → "Model hazır" → "Dinleniyor". Konuş, kısa dur → Word'e yazılır.
7. Mevzuat için: **📚 Mevzuat penceresini aç** (aynı uygulama içinde açılır).

## SESLİ KOMUTLAR
| Söyle | Sonuç |
|---|---|
| (normal konuş) | Word'e yazılır (noktalama + büyük harf otomatik) |
| **yeni paragraf** | Alt satıra geçer |
| **geri al** / **sil** | Son yazılanı geri alır (Ctrl+Z) |
| **kelime sil** | Son kelimeyi siler |
| **Word'e geç** / **UYAP'a geç** / **mevzuata geç** | O pencere öne gelir |
| **borçlar kanunu madde 49 getir** | Mevzuat penceresi maddeyi açar, sonra Word'e **yapıştırır** |
| **türk ceza kanunu madde 3 kopyala** | TCK md.3 çekilir, yapıştırılır |

> "getir/kopyala/yapıştır" demezsen mevzuat komutu çalışmaz, düz yazılır.
> "sil"/"geri al" yalnız tek başına söylenince komuttur (cümle ortasında yazıyı bozmaz).

## GÜVENLİK (Bakanlık'a anlatırken)
- ✅ "Ses ve metin **diske kaydedilmez, internete gönderilmez**, her şey bellekte işlenir, model cihazda gömülü."
- ❌ "RAM'i sıfırlıyoruz virüs okuyamaz" DEME (teknik ispatı yok).

## NOTLAR / SINIRLAR
- Model **medium** (güçlü PC için). Çok yavaşsa: bizde `MODEL_BOYUTU="small"` yapıp yeniden derleriz.
- Gürültüde Silero VAD devrede; yine de çok gürültülü ortamda hata artabilir.
- Antivirüs ilk seferde uyarabilir (klavye kullanır) → izin ver; ileride imzalama (code signing).
- Mevzuat metinleri şimdilik TEMSİLİ örnek; gerçek metin entegrasyonu sonraki etap.
- Henüz yok: "orayı sil" (imleç içi bağlamsal düzeltme), F3 şablonlar — sonraki etaplar.
