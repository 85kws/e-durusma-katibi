# E-Duruşma Katibi

Sesle dikte eden, %100 offline Windows masaüstü asistanı (hakim/avukat için).
Konuşulan metin, o an açık olan yazı programına (Word/UYAP/Not Defteri) yazılır.
Sesli komutlar: pencere geçişi + mevzuat çekme. Açılış şifresi (varsayılan `1234`).

## Hazır EXE indirme (bulut build)
Bu repo'ya her push'ta GitHub Actions **Windows runner**'da exe üretir.
1. **Actions** sekmesi → en son `build-exe` çalışması.
2. Altta **Artifacts** → `E-DurusmaKatibi-Windows` (zip) indir.
3. Zip içinde: `E-DurusmaKatibi.exe`, `UYAP_Mevzuat.exe`, `NOTLAR_WINDOWS.md`.
4. İkisini Masaüstüne çıkar, çift tıkla. (İlk açılışta model ~484MB iner, bir kez internet.)

Detaylı kullanım: `NOTLAR_WINDOWS.md`.

## Dosyalar
- `e_durusma_katibi.py` — ana uygulama (GUI: mikrofon seç + test + dikte)
- `adim2_mevzuat_simulator.py` — mevzuat penceresi (kütüphane simülatörü)
- `komutlar.py` — sesli komut çözümleme + pencere/mevzuat eylemleri
