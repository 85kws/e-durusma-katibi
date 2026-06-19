"""
E-Duruşma Katibi — ADIM 3 + 5: Sesli komutlar
=============================================
İki yetenek:
  * PENCERE GEÇİŞİ: "Word'e geç", "UYAP'a geç", "mevzuata geç" -> ilgili pencereyi öne getir.
  * MEVZUAT ÇEKME : "borçlar kanunu madde 49 getir/kopyala/yapıştır" ->
      simülatör penceresine o maddeyi açtır (görsel), panoya kopyalat, öne getir;
      sonra editöre dönüp Ctrl+V ile yapıştır. Hakim açılanı gözüyle doğrular.

TASARIM:
  * komut_coz(metin) SAFtır (sadece re + adim2 verisi). Windows kütüphaneleri
    (pygetwindow / pynput / pyperclip / socket) yalnızca eylem fonksiyonlarının
    İÇİNDE import edilir -> bu modül her yerde import edilip test edilebilir.
  * İki süreç (ana program <-> simülatör) "ayrı .exe" gibi davranır; haberleşme
    SADECE 127.0.0.1 (loopback) üzerinden -> internet KULLANILMAZ.
  * Simülatör çalışmıyorsa mevzuat yine yedek olarak kendi verimizden yapıştırılır.
"""

import re
import sys
import subprocess
from adim2_mevzuat_simulator import KUTUPHANE, ad_to_kod, PENCERE_BASLIGI, KONTROL_PORT

SIM_BASLIK = PENCERE_BASLIGI  # "UYAP Mevzuat Simulator"

# Enter'a basılacak sesli komutlar.
KOMUTLAR_ENTER = {"yeni paragraf", "yeni satır", "yeni satir", "alt satır", "alt satir"}

# "Geri al" — son yazılanı geri alır (Ctrl+Z). Tam eşleşme (cümle ortasında tetiklenmez).
KOMUTLAR_GERIAL = {"geri al", "geri", "sil", "bunu sil", "onu sil", "yok sil",
                   "son yazdığını sil", "son yazdigini sil", "iptal", "iptal et"}

# "Kelime sil" — son kelimeyi siler (Ctrl+Backspace).
KOMUTLAR_KELIMESIL = {"kelime sil", "kelimeyi sil", "son kelimeyi sil", "son kelime sil"}

# Pencere geçişi: sesli anahtar -> pencere başlığında aranacak metin.
# SIRA önemli: "mevzuat" "uyap"tan ÖNCE (uyap mevzuat -> simülatör penceresi).
PENCERE_HEDEF = [
    ("mevzuat", SIM_BASLIK),
    ("word", "Word"),
    ("uyap", "UYAP"),
    ("not defteri", "Not Defteri"),
    ("notepad", "Notepad"),
    ("gedit", "gedit"),          # Ubuntu metin editörü
    ("writer", "Writer"),        # LibreOffice Writer
    ("tarayıcı", "Chrome"),
    ("tarayici", "Chrome"),
]

# Mevzuat çekmeyi TETİKLEYEN eylem kelimeleri. Bunlar yoksa cümle normal yazılır
# (örn. "Türk Ceza Kanunu madde 3 gereğince..." -> komut DEĞİL, düz metin).
MEVZUAT_AKSIYON = ("kopyala", "getir", "yapıştır", "yapistir", "ekle")


# Yazım düzeltme sözlüğü: ses tanıyıcının sık karıştırdığı kelimeler.
# Buraya "yanlış": "doğru" ekleyerek genişletebilirsin. Tam kelime, büyük/küçük korunur.
DUZELTMELER = {
    "back": "bacak",
    "berat": "beraat",
    "beratine": "beraatine",
    "tahliyesine": "tahliyesine",
}


def yazim_duzelt(metin: str) -> str:
    """Metindeki bilinen yanlış kelimeleri düzeltir (büyük/küçük harfi korur)."""
    def repl(m):
        kelime = m.group(0)
        dogru = DUZELTMELER.get(kelime.lower())
        if not dogru:
            return kelime
        return dogru.capitalize() if kelime[:1].isupper() else dogru
    return re.sub(r"[A-Za-zÇĞİıÖŞÜçğöşü]+", repl, metin)


def komut_coz(metin: str):
    """metin -> (tip, veri). tip: 'enter' | 'pencere' | 'mevzuat' | None."""
    s = metin.lower().strip(" .,!?;:\n\t")

    # 1) Enter komutları
    if s in KOMUTLAR_ENTER:
        return ("enter", None)

    # 1b) Geri al / sil komutları (tam eşleşme — düz metni bozmaz)
    if s in KOMUTLAR_GERIAL:
        return ("geri_al", None)
    if s in KOMUTLAR_KELIMESIL:
        return ("kelime_sil", None)

    # 2) Mevzuat çekme (en spesifik): kanun adı + "madde N" + eylem kelimesi
    kod = ad_to_kod(s)
    m = re.search(r"madde\s*(\d+)", s)
    if kod and m:
        madde = m.group(1)
        if madde in KUTUPHANE.get(kod, {}).get("maddeler", {}) and any(a in s for a in MEVZUAT_AKSIYON):
            return ("mevzuat", (kod, madde))

    # 3) Pencere geçişi: "... geç" + bilinen hedef
    if "geç" in s or "gec" in s:
        for anahtar, baslik in PENCERE_HEDEF:
            if anahtar in s:
                return ("pencere", baslik)

    return (None, None)


# ----------------------------- EYLEMLER (Windows) ----------------------------
def _ctrl_v():
    """Aktif pencereye Ctrl+V (Windows: pynput, Linux: xdotool)."""
    if sys.platform.startswith("win"):
        from pynput.keyboard import Key, Controller
        kb = Controller()
        kb.press(Key.ctrl); kb.press("v"); kb.release("v"); kb.release(Key.ctrl)
    else:
        subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+v"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)


def enter_gonder():
    """Aktif pencereye Enter (Windows: pynput, Linux: xdotool)."""
    if sys.platform.startswith("win"):
        from pynput.keyboard import Key, Controller
        kb = Controller()
        kb.press(Key.enter); kb.release(Key.enter)
    else:
        subprocess.run(["xdotool", "key", "--clearmodifiers", "Return"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)


def geri_al():
    """Son yazılanı geri al (Ctrl+Z)."""
    if sys.platform.startswith("win"):
        from pynput.keyboard import Key, Controller
        kb = Controller()
        kb.press(Key.ctrl); kb.press("z"); kb.release("z"); kb.release(Key.ctrl)
    else:
        subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+z"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)


def kelime_sil():
    """Son kelimeyi sil (Ctrl+Backspace)."""
    if sys.platform.startswith("win"):
        from pynput.keyboard import Key, Controller
        kb = Controller()
        kb.press(Key.ctrl); kb.press(Key.backspace); kb.release(Key.backspace); kb.release(Key.ctrl)
    else:
        subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+BackSpace"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)


def yapistir_metin(metin: str):
    """Metni panoya koy, Ctrl+V ile yapıştır, eski pano içeriğini geri koy."""
    import time
    import pyperclip
    eski = ""
    try:
        eski = pyperclip.paste()
    except Exception:
        eski = ""
    pyperclip.copy(metin)
    time.sleep(0.05)
    _ctrl_v()
    time.sleep(0.05)
    try:
        pyperclip.copy(eski)
    except Exception:
        pass


def pencereye_gec(baslik_parcasi: str) -> bool:
    """Başlığında 'baslik_parcasi' geçen pencereyi öne getirir (Windows + Linux)."""
    parca = (baslik_parcasi or "").strip()
    if not parca:
        return False
    if sys.platform.startswith("win"):
        return _gec_windows(parca)
    return _gec_linux(parca)


def _gec_windows(parca: str) -> bool:
    try:
        import pygetwindow as gw
        pencereler = gw.getAllWindows()
    except Exception:
        return False
    for w in pencereler:
        t = (w.title or "").strip()
        if t and parca.lower() in t.lower():
            try:
                if getattr(w, "isMinimized", False):
                    w.restore()
                w.activate()
                return True
            except Exception:
                try:
                    w.minimize(); w.restore(); return True
                except Exception:
                    return False
    return False


def _gec_linux(parca: str) -> bool:
    # wmctrl -a: başlığında 'parca' geçen pencereyi etkinleştirir (substring eşleşme).
    try:
        subprocess.run(["wmctrl", "-a", parca], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        return True
    except Exception:
        return False


def _aktif_pencere_basligi():
    if sys.platform.startswith("win"):
        try:
            import pygetwindow as gw
            w = gw.getActiveWindow()
            return w.title if w else None
        except Exception:
            return None
    # Linux: xdotool ile aktif pencere başlığı
    try:
        out = subprocess.run(["xdotool", "getactivewindow", "getwindowname"],
                             capture_output=True, text=True, timeout=2)
        t = out.stdout.strip()
        return t or None
    except Exception:
        return None


def _simulatore_gonder(kod: str, madde: str) -> bool:
    """Simülatöre (loopback) 'şu maddeyi aç+kopyala' der. Çalışmıyorsa False."""
    import socket
    try:
        with socket.create_connection(("127.0.0.1", KONTROL_PORT), timeout=0.6) as s:
            s.sendall(f"AC|{kod}|{madde}".encode("utf-8"))
        return True
    except Exception:
        return False


def mevzuat_getir(kod: str, madde: str) -> bool:
    """Tam akış: simülatörde aç -> kopyala -> editöre dön -> yapıştır."""
    import time
    editor = _aktif_pencere_basligi()            # hakimin yazdığı editör penceresi
    gonderildi = _simulatore_gonder(kod, madde)  # simülatör açar, kopyalar, öne gelir

    if not gonderildi:
        # Yedek: simülatör kontrol portu yok -> kendi verimizi panoya koy + pencereyi öne getir
        try:
            import pyperclip
            pyperclip.copy(KUTUPHANE[kod]["maddeler"][madde])
        except Exception:
            pass
        pencereye_gec(SIM_BASLIK)

    time.sleep(0.9)                              # hakim açılan maddeyi görsün/incelesin
    if editor:
        pencereye_gec(editor)
        time.sleep(0.3)
    _ctrl_v()                                    # editöre yapıştır
    return True
