"""
E-Duruşma Katibi — ANA UYGULAMA (tek pencere arayüz)
====================================================
Tek tıkla açılır. İçinde:
  * Mikrofon (girdi cihazı) SEÇME listesi
  * 🎤 MİKROFON TESTİ (2 sn dinler, ses geliyor mu gösterir)
  * ▶ Başlat / ⏸ Durdur — sesli dikteyi açar/kapatır
  * 📚 Mevzuat penceresini aç
  * Durum + son tanınan metin

Dikte: konuşulan -> faster-whisper (lokal, offline) -> aktif editöre Ctrl+V ile yazılır.
Sesli komutlar komutlar.py'de (yeni paragraf / pencere geçişi / mevzuat çekme).

GÜVENLİK: ses ve metin diske yazılmaz, ağa gönderilmez (her şey RAM'de).
"""

import sys
import os
import time
import queue
import threading
import subprocess

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

import komutlar

# --- Ses / model ayarları ---
ORNEKLEME = 16000
KANAL = 1
BLOK = 0.10
SESSIZLIK_ESIGI = 0.020       # bu RMS altı = sessizlik (mikrofona göre ayarlanır)
SESSIZLIK_SURESI = 0.70       # konuşma sonrası bu kadar sn sessizlik = cümle bitti
MAX_SUR = 6.0                 # EN GEÇ bu kadar saniyede işle (uzun birikmeyi önler)
DIL = "tr"
# Model: doğruluk/gürültü ↔ hız dengesi. medium (güçlü PC için) — small'dan daha doğru, gürültüde iyi.
MODEL_BOYUTU = "medium"
HUKUKI_PROMPT = ("Hukuki dikte. Terimler: beraat, beraatine, sanık, müşteki, "
                 "davacı vekili, davalı, Cumhuriyet Savcısı, gereği düşünüldü, "
                 "tahliye, mahkumiyet, tazminat.")

# Programı açış şifresi (baban değiştirebilir). 3 yanlışta program kapanır.
SIFRE = "1234"


def _model_kaynagi():
    """exe (frozen) ise içine gömülü 'model' klasörü; değilse boyut adı (indirir)."""
    if getattr(sys, "frozen", False):
        taban = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        gomulu = os.path.join(taban, "model")
        if os.path.isdir(gomulu):
            return gomulu
    return MODEL_BOYUTU


def input_cihazlari():
    """Girdi (mikrofon) cihazlarının listesi: [(index, isim), ...]."""
    liste = []
    try:
        for i, d in enumerate(sd.query_devices()):
            if d.get("max_input_channels", 0) > 0:
                liste.append((i, d["name"]))
    except Exception:
        pass
    return liste


def _cihaz_default_sr(device):
    """Cihazın desteklediği örnekleme hızı (16kHz açılmazsa kullanılır)."""
    try:
        info = sd.query_devices(device, "input")
        return int(info.get("default_samplerate", 44100)) or 44100
    except Exception:
        return 44100


def _resample16k(ses, sr):
    """Sesi 16kHz'e indir (Whisper 16kHz ister)."""
    if sr == ORNEKLEME:
        return ses
    n = int(len(ses) * ORNEKLEME / sr)
    if n <= 1:
        return ses
    return np.interp(np.linspace(0, len(ses), n, endpoint=False),
                     np.arange(len(ses)), ses).astype(np.float32)


def mikrofon_test(device=None, sure=2.0):
    """Seçili mikrofondan kaydeder, ses seviyesini (RMS) döndürür. 16kHz olmazsa cihaz hızını dener."""
    son = None
    for sr in (ORNEKLEME, _cihaz_default_sr(device)):
        try:
            kayit = sd.rec(int(sure * sr), samplerate=sr, channels=1,
                           dtype="float32", device=device)
            sd.wait()
            return float(np.sqrt(np.mean(np.square(kayit))))
        except Exception as e:
            son = e
            continue
    raise RuntimeError(f"mikrofon açılamadı: {son}")


class DikteMotoru:
    """Mikrofonu dinler, cümleleri deşifre eder, komut/yazma yapar."""

    def __init__(self, on_durum=None, on_metin=None):
        self.on_durum = on_durum or (lambda s: None)
        self.on_metin = on_metin or (lambda t: None)
        self.model = None
        self._calisiyor = False
        self._kuyruk = queue.Queue()
        self._stream = None
        self.sr = ORNEKLEME

    def model_yukle(self):
        if self.model is None:
            self.on_durum("Model yükleniyor... (ilk sefer biraz sürer)")
            self.model = WhisperModel(MODEL_BOYUTU, device="cpu", compute_type="int8")
            self.on_durum("Model hazır.")

    def baslat(self, device=None):
        self.model_yukle()
        self._calisiyor = True
        self._kuyruk = queue.Queue()
        threading.Thread(target=self._dongu, daemon=True).start()
        son = None
        for sr in (ORNEKLEME, _cihaz_default_sr(device)):
            try:
                self.sr = sr
                self._stream = sd.InputStream(samplerate=sr, channels=KANAL, dtype="float32",
                                              blocksize=int(sr * BLOK), device=device,
                                              callback=self._cb)
                self._stream.start()
                self.on_durum("Dinleniyor 🎙️ — konuşun")
                return
            except Exception as e:
                son = e
                continue
        self._calisiyor = False
        self.on_durum(f"❌ Mikrofon açılamadı: {son}")

    def durdur(self):
        self._calisiyor = False
        if self._stream:
            try:
                self._stream.stop(); self._stream.close()
            except Exception:
                pass
            self._stream = None
        self.on_durum("Durduruldu ⏸️")

    def _cb(self, indata, frames, t, status):
        if self._calisiyor:
            # Geri-basınç: işleme yetişemezse eski sesi düşür (sonsuz gecikmeyi önler).
            if self._kuyruk.qsize() < int(3 * MAX_SUR / BLOK):
                self._kuyruk.put(indata.copy())

    def _dongu(self):
        biriken, sessiz, konusuldu = [], 0, False
        gereken = max(1, int(SESSIZLIK_SURESI / BLOK))
        max_blok = max(gereken + 1, int(MAX_SUR / BLOK))
        while self._calisiyor:
            try:
                blok = self._kuyruk.get(timeout=0.5)
            except queue.Empty:
                continue
            seviye = float(np.sqrt(np.mean(np.square(blok))))
            if seviye >= SESSIZLIK_ESIGI:
                konusuldu = True; sessiz = 0; biriken.append(blok)
            elif konusuldu:
                sessiz += 1; biriken.append(blok)
            # İşle: yeterli sessizlik VEYA en fazla MAX_SUR doldu (uzun birikmeyi önler)
            if konusuldu and (sessiz >= gereken or len(biriken) >= max_blok):
                ses = np.concatenate(biriken).flatten().astype(np.float32)
                biriken, sessiz, konusuldu = [], 0, False
                self._isle(ses)
                del ses

    def _isle(self, ses):
        if self.sr != ORNEKLEME:
            ses = _resample16k(ses, self.sr)
        # vad_filter=True: Silero VAD ile gürültü/sessizlik elenir (gürültülü ortamda daha iyi).
        # condition_on_previous_text=False: tekrar/halüsinasyonu önler.
        segs, _ = self.model.transcribe(ses, language=DIL, beam_size=5,
                                        vad_filter=True, condition_on_previous_text=False,
                                        initial_prompt=HUKUKI_PROMPT)
        metin = "".join(s.text for s in segs).strip()
        if not metin:
            return
        tip, veri = komutlar.komut_coz(metin)
        if tip == "enter":
            komutlar.enter_gonder(); self.on_metin("↵ [yeni paragraf]")
        elif tip == "geri_al":
            komutlar.geri_al(); self.on_metin("↶ [geri al]")
        elif tip == "kelime_sil":
            komutlar.kelime_sil(); self.on_metin("⌫ [kelime sil]")
        elif tip == "pencere":
            ok = komutlar.pencereye_gec(veri)
            self.on_metin(f"🪟 [{veri}{'' if ok else ' — bulunamadı'}]")
        elif tip == "mevzuat":
            kod, madde = veri
            komutlar.mevzuat_getir(kod, madde)
            self.on_metin(f"📚 [{kod} madde {madde} yapıştırıldı]")
        else:
            komutlar.yapistir_metin(metin + " ")
            self.on_metin(metin)
        del metin


def mevzuat_penceresi_ac():
    """Mevzuat simülatörünü ayrı pencere/işlem olarak açar (Windows'ta ayrı .exe)."""
    try:
        if getattr(sys, "frozen", False):
            # exe halinde: yanındaki UYAP_Mevzuat.exe'yi çalıştır
            klasor = os.path.dirname(sys.executable)
            yol = os.path.join(klasor, "UYAP_Mevzuat.exe")
            subprocess.Popen([yol])
        else:
            klasor = os.path.dirname(os.path.abspath(__file__))
            subprocess.Popen([sys.executable,
                              os.path.join(klasor, "adim2_mevzuat_simulator.py")])
        return True
    except Exception:
        return False


# ------------------------------- ARAYÜZ -------------------------------------
def main():
    import tkinter as tk
    from tkinter import ttk, simpledialog, messagebox

    # --- Açılış şifresi (baban istedi) ---
    gecici = tk.Tk()
    gecici.withdraw()
    girildi = False
    for _ in range(3):
        girilen = simpledialog.askstring("E-Duruşma Katibi", "Şifre:", show="*", parent=gecici)
        if girilen is None:
            gecici.destroy(); return          # iptal -> kapan
        if girilen == SIFRE:
            girildi = True; break
        messagebox.showerror("E-Duruşma Katibi", "Yanlış şifre.", parent=gecici)
    gecici.destroy()
    if not girildi:
        return                                 # 3 yanlış -> kapan

    kok = tk.Tk()
    kok.title("E-Duruşma Katibi")
    kok.geometry("560x440")

    motor = DikteMotoru()

    ttk.Label(kok, text="E-Duruşma Katibi", font=("Segoe UI", 15, "bold"),
              padding=10).pack()

    # 1) Mikrofon seçimi
    cer = ttk.Frame(kok, padding=(14, 4)); cer.pack(fill="x")
    ttk.Label(cer, text="Mikrofon (girdi cihazı):").pack(anchor="w")
    cihazlar = input_cihazlari()
    secenekler = [f"{i}: {ad}" for i, ad in cihazlar] or ["(mikrofon bulunamadı)"]
    mic_var = tk.StringVar(value=secenekler[0])
    mic_combo = ttk.Combobox(cer, textvariable=mic_var, values=secenekler,
                             state="readonly", width=60)
    mic_combo.pack(fill="x", pady=4)

    def secili_device():
        try:
            return int(mic_var.get().split(":")[0])
        except Exception:
            return None

    # 2) Mikrofon testi
    test_frame = ttk.Frame(kok, padding=(14, 4)); test_frame.pack(fill="x")
    test_durum = tk.StringVar(value="")

    def mic_test_calistir():
        test_btn.config(state="disabled")
        test_durum.set("Konuşun... 2 saniye dinleniyor 🎤")
        def isle():
            try:
                seviye = mikrofon_test(secili_device(), 2.0)
                if seviye >= SESSIZLIK_ESIGI:
                    test_durum.set(f"✅ Mikrofon ÇALIŞIYOR (ses seviyesi: {seviye:.3f})")
                else:
                    test_durum.set(f"⚠️ Ses gelmedi (seviye {seviye:.3f}). "
                                   f"Mikrofonu/seçimi kontrol edin.")
            except Exception as e:
                test_durum.set(f"❌ Test hatası: {e}")
            finally:
                test_btn.config(state="normal")
        threading.Thread(target=isle, daemon=True).start()

    test_btn = ttk.Button(test_frame, text="🎤 Mikrofon Testi (2 sn)", command=mic_test_calistir)
    test_btn.pack(anchor="w")
    ttk.Label(test_frame, textvariable=test_durum, foreground="#555").pack(anchor="w", pady=2)

    # 3) Başlat / Durdur
    kontrol = ttk.Frame(kok, padding=(14, 8)); kontrol.pack(fill="x")
    durum_var = tk.StringVar(value="Hazır. Önce mikrofonu test edin, sonra Başlat.")
    calisiyor = {"v": False}

    def basla_dur():
        if not calisiyor["v"]:
            mic_combo.config(state="disabled")
            baslat_btn.config(text="⏸ Durdur")
            calisiyor["v"] = True
            dev = secili_device()
            threading.Thread(target=lambda: motor.baslat(dev), daemon=True).start()
        else:
            motor.durdur()
            calisiyor["v"] = False
            baslat_btn.config(text="▶ Başlat")
            mic_combo.config(state="readonly")

    baslat_btn = ttk.Button(kontrol, text="▶ Başlat", command=basla_dur)
    baslat_btn.pack(side="left")
    ttk.Button(kontrol, text="📚 Mevzuat penceresini aç",
               command=mevzuat_penceresi_ac).pack(side="left", padx=8)

    # 4) Durum + son metin
    alt = ttk.Frame(kok, padding=(14, 4)); alt.pack(fill="both", expand=True)
    motor.on_durum = lambda s: durum_var.set(s)
    ttk.Label(alt, textvariable=durum_var, foreground="#1a5").pack(anchor="w")
    ttk.Label(alt, text="Son işlenen:").pack(anchor="w", pady=(8, 0))
    son_metin = tk.StringVar(value="")
    motor.on_metin = lambda t: son_metin.set(t)
    ttk.Label(alt, textvariable=son_metin, wraplength=520, foreground="#333").pack(anchor="w")

    ttk.Label(kok, text="İpucu: Word/editör açıkken Başlat'a bas, oraya yazılır. "
                        "'yeni paragraf', 'borçlar kanunu madde 49 getir' deneyin.",
              foreground="#888", wraplength=540, padding=(14, 6)).pack(side="bottom", fill="x")

    def kapat():
        try:
            motor.durdur()
        except Exception:
            pass
        kok.destroy()
    kok.protocol("WM_DELETE_WINDOW", kapat)

    kok.mainloop()


if __name__ == "__main__":
    main()
