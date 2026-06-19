# E-Duruşma Katibi — WINDOWS (babanın PC'si) — KURULUM ve EXE

Sesle dikte: konuşulan, o an açık olan yazı programına (Word/UYAP/Not Defteri — fark etmez) yazılır.
Tek pencere arayüz: **mikrofon seç → mikrofon testi → Başlat**.

> 🔒 Program açılışta **şifre** sorar. Varsayılan: **1234**. Değiştirmek için `e_durusma_katibi.py` içinde `SIFRE = "1234"` satırını düzenle (exe yapmadan önce).

---

## YOL 1 — EXE YAP (masaüstünden çift tıkla çalışan)
> Exe yalnızca **Windows'ta** üretilebilir (Linux'ta üretilemez). Adımlar:

1. **Python 3.11** kur: https://www.python.org/downloads/release/python-3119/
   → Kurulumda **"Add Python to PATH"** işaretle (şart).
2. Bu `windows` klasörünü bilgisayara kopyala (örn. Masaüstü\windows).
3. Klasörde **`YAP_EXE.bat`** dosyasına çift tıkla. (Kütüphaneleri kurar + exe'leri üretir, birkaç dk.)
4. Bitince `dist` klasöründe iki dosya olur:
   - `E-DurusmaKatibi.exe`  → ana uygulama
   - `UYAP_Mevzuat.exe`     → mevzuat penceresi
5. **İkisini de Masaüstüne kopyala.** Çift tıkla → çalışır.
   (İlk açılışta yapay zeka modeli ~484MB iner; bir kez internet gerekir, sonrası offline.)

## YOL 2 — Exe yapmadan hızlı dene
1–2. aynı (Python kur + klasörü kopyala).
3. **`kur.bat`** çift tıkla (kütüphaneler).
4. **`calistir.bat`** çift tıkla → uygulama açılır.

---

## UYGULAMAYI KULLANMA
1. (İstersen) `UYAP_Mevzuat.exe`'yi aç — mevzuat penceresi.
2. **Word** (veya Not Defteri) aç, içine tıkla.
3. `E-DurusmaKatibi.exe`'yi aç:
   - **Mikrofon** listesinden cihazını seç.
   - **🎤 Mikrofon Testi (2 sn)** → "✅ Mikrofon ÇALIŞIYOR" görmelisin (konuş).
   - **▶ Başlat** → "Model hazır" sonra "Dinleniyor". Konuş, kısa dur → Word'e yazılır.

## SESLİ KOMUTLAR
| Söyle | Sonuç |
|---|---|
| (normal konuş) | Word'e yazılır (noktalama + büyük harf otomatik) |
| **yeni paragraf** | Alt satıra geçer |
| **Word'e geç** / **UYAP'a geç** / **mevzuata geç** | O pencere öne gelir |
| **borçlar kanunu madde 49 getir** | Mevzuat penceresi maddeyi açar+kopyalar, öne gelir, sonra Word'e **yapıştırır** |
| **türk ceza kanunu madde 3 kopyala** | TCK md.3 çekilir, yapıştırılır |

> "getir/kopyala/yapıştır" demezsen komut sayılmaz, düz yazılır.

## GÜVENLİK (Bakanlık'a anlatırken)
- ✅ "Ses ve metin **diske kaydedilmez, internete gönderilmez**, her şey bellekte işlenir."
- ✅ İki program arası bağlantı yalnız **127.0.0.1** (kendi bilgisayar, internet değil).
- ❌ "RAM'i sıfırlıyoruz virüs okuyamaz" DEME (teknik ispatı yok).

## SINIRLAR / NOTLAR
- Eski i3 PC'de cümle başına ~1-3 sn.
- Antivirüs ilk seferde uyarabilir (klavye kullanır) → izin ver; ileride imzalama (code signing).
- Exe ilk açılışı yavaş (kendini açar) — normal.
- Mevzuat penceresindeki kanun metinleri şimdilik TEMSİLİ örnek; gerçek metin entegrasyonu sonraki etap.
- Henüz yok: "orayı sil" düzeltme, F3 şablonlar — sonraki etaplar.
