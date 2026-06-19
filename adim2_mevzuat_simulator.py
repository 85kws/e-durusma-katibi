"""
E-Duruşma Katibi — ADIM 2: UYAP Mevzuat Simülatörü (KÜTÜPHANE mantığı)
=====================================================================

Babanın isteği (2026-06-19):
  * ARAMA KUTUSU YOK. "borçlar kanunu" denince -> kanunun KODUNU listeden bul
    -> o kodun karşılığı mevzuatı DOĞRUDAN aç. Kütüphane gibi (raftan çek).
  * Şimdilik sadece SİMÜLE et — sanki ayrı bir .exe'ymiş gibi bağımsız pencere.
  * Görsel olarak: kanunu AÇ -> maddeyi KOPYALA. Böylece hakim açılan kanunda
    maddenin altına/üstüne kendi gözüyle bakar, kaçırdığı yer var mı görür ve
    "doğru yeri mi kesti" diye kopyalananı gözüyle doğrular.

Mimari rolü:
  Ana program (adim1) ileride şöyle yapacak:
    "borçlar kanunu madde 49 kopyala" -> ad_to_kod("borçlar kanunu")="6098"
    -> bu pencereyi (başlık: "UYAP Mevzuat Simulator") öne getir
    -> 6098'i ve madde 49'u seç, Kopyala'ya bas -> metin panoya gelir
    -> editöre yapıştırırken kullanıcı görür ve kesimi doğrular.

NOT: tkinter import'u ve tüm arayüz main() içindedir; böylece bu dosya GUI
     açmadan import edilebilir (ana program ad_to_kod/KUTUPHANE'yi alabilir).

UYARI: Madde metinleri TEMSİLİ/ÖRNEKtir, resmi metin değildir. Kanun KODLARI gerçektir.
"""

PENCERE_BASLIGI = "UYAP Mevzuat Simulator"
KONTROL_PORT = 50505   # ana program bu loopback portundan "şu maddeyi aç" der (SADECE 127.0.0.1)

# KÜTÜPHANE: kanun KODU -> {ad, maddeler}.  (kod gerçek, madde metni TEMSİLİ)
KUTUPHANE = {
    "6098": {
        "ad": "Türk Borçlar Kanunu",
        "maddeler": {
            "1":  "Sözleşme, tarafların iradelerini karşılıklı ve birbirine uygun olarak "
                  "açıklamalarıyla kurulur. İrade açıklaması açık veya örtülü olabilir. [TEMSİLİ]",
            "49": "Kusurlu ve hukuka aykırı bir fiille başkasına zarar veren, bu zararı "
                  "gidermekle yükümlüdür. [TEMSİLİ]",
            "112": "Borç hiç veya gereği gibi ifa edilmezse borçlu, kusuru olmadığını "
                   "ispat etmedikçe alacaklının bundan doğan zararını gidermekle yükümlüdür. [TEMSİLİ]",
        },
    },
    "5237": {
        "ad": "Türk Ceza Kanunu",
        "maddeler": {
            "1": "Ceza Kanununun amacı; kişi hak ve özgürlüklerini, kamu düzen ve "
                 "güvenliğini, hukuk devletini korumak, suç işlenmesini önlemektir. [TEMSİLİ]",
            "3": "Suç işleyen kişi hakkında işlenen fiilin ağırlığıyla orantılı ceza ve "
                 "güvenlik tedbirine hükmolunur; uygulamada ayrım yapılamaz. [TEMSİLİ]",
        },
    },
    "5271": {
        "ad": "Ceza Muhakemesi Kanunu",
        "maddeler": {
            "147": "İfade alınmasında kimlik sorulur, müdafi seçme hakkı ve susma hakkı "
                   "hatırlatılır, yüklenen suç anlatılır. [TEMSİLİ]",
        },
    },
    "6100": {
        "ad": "Hukuk Muhakemeleri Kanunu",
        "maddeler": {
            "119": "Dava dilekçesinde mahkeme adı, tarafların kimlik ve adresleri, konu, "
                   "açık talep sonucu ve deliller gösterilir. [TEMSİLİ]",
        },
    },
    "4721": {
        "ad": "Türk Medeni Kanunu",
        "maddeler": {
            "6": "Kanunda aksine hüküm olmadıkça, taraflardan her biri hakkını dayandırdığı "
                 "olguların varlığını ispatla yükümlüdür. [TEMSİLİ]",
        },
    },
    "2577": {
        "ad": "İdari Yargılama Usulü Kanunu",
        "maddeler": {
            "2": "İdari dava türleri iptal ve tam yargı davalarıdır. İşlemler yetki, şekil, "
                 "sebep, konu ve maksat yönlerinden hukuka aykırılık nedeniyle iptal edilebilir. [TEMSİLİ]",
        },
    },
}

# Sesli komut adını koda çeviren takma adlar (ileride ana program kullanacak).
ALIAS = {
    "borçlar": "6098", "borclar": "6098",
    "ceza kanunu": "5237", "tck": "5237",
    "ceza muhakemesi": "5271", "cmk": "5271",
    "hukuk muhakemeleri": "6100", "hmk": "6100",
    "medeni": "4721", "tmk": "4721",
    "idari yargılama": "2577", "iyuk": "2577",
}


def ad_to_kod(metin: str):
    """'borçlar kanunu' -> '6098'. Önce tam ad, sonra takma adlarda arar."""
    m = metin.lower()
    for kod, k in KUTUPHANE.items():
        if k["ad"].lower() in m or m in k["ad"].lower():
            return kod
    for alias, kod in ALIAS.items():
        if alias in m:
            return kod
    return None


def arayuz_kur(pencere):
    """Mevzuat arayüzünü verilen pencereye (Tk veya Toplevel) kurar.
    'ac(kod, madde)' fonksiyonu döndürür: kanunu+maddeyi seçer, kopyalar, öne getirir.
    Hem tek-exe (ana uygulama içinden Toplevel) hem standalone main() kullanır."""
    import tkinter as tk
    from tkinter import ttk

    state = {"kod": None, "madde": None}

    pencere.title(PENCERE_BASLIGI)      # SABİT başlık
    pencere.geometry("780x480")
    kok = pencere                        # aşağıdaki kod 'kok' adını kullanıyor

    def metni_goster(metin):
        metin_alani.config(state="normal")
        metin_alani.delete("1.0", tk.END)
        metin_alani.insert("1.0", metin)
        metin_alani.config(state="disabled")

    def kanun_secildi(event=None):
        secim = kanun_liste.curselection()
        if not secim:
            return
        state["kod"] = list(KUTUPHANE.keys())[secim[0]]
        state["madde"] = None
        kayit = KUTUPHANE[state["kod"]]
        madde_liste.delete(0, tk.END)
        for no in kayit["maddeler"]:
            madde_liste.insert(tk.END, f"Madde {no}")
        metni_goster("")
        durum.set(f"Açıldı: {kayit['ad']} ({state['kod']}) — maddeyi seçin")
        kopyala_btn.config(state="disabled")

    def madde_secildi(event=None):
        if not state["kod"]:
            return
        secim = madde_liste.curselection()
        if not secim:
            return
        no = list(KUTUPHANE[state["kod"]]["maddeler"].keys())[secim[0]]
        state["madde"] = no
        metin = KUTUPHANE[state["kod"]]["maddeler"][no]
        baslik = f"{KUTUPHANE[state['kod']]['ad']} ({state['kod']}) — Madde {no}\n" + "-" * 50 + "\n"
        metni_goster(baslik + metin)
        durum.set(f"Hazır: Madde {no} — 'Maddeyi Kopyala' ile panoya alın")
        kopyala_btn.config(state="normal")

    def maddeyi_kopyala():
        if not (state["kod"] and state["madde"]):
            return
        metin = KUTUPHANE[state["kod"]]["maddeler"][state["madde"]]
        kok.clipboard_clear()
        kok.clipboard_append(metin)
        kok.update()  # pano işlensin
        durum.set(f"✔ Kopyalandı (panoda): {KUTUPHANE[state['kod']]['ad']} Madde {state['madde']}"
                  f" — editöre yapıştırıp doğru yeri kestiğinizi görebilirsiniz")

    ttk.Label(kok, text="📚 Mevzuat Kütüphanesi (Simülasyon)   —   kanunu seç → maddeyi aç → kopyala",
              font=("Segoe UI", 11, "bold"), padding=8).pack(fill="x")

    govde = ttk.Frame(kok, padding=(10, 0, 10, 6))
    govde.pack(fill="both", expand=True)

    # Sol: kanun rafı (isimle doğrudan erişim — arama yok)
    sol = ttk.Frame(govde)
    sol.pack(side="left", fill="y")
    ttk.Label(sol, text="Kanunlar (raf):").pack(anchor="w")
    kanun_liste = tk.Listbox(sol, width=30, height=20, exportselection=False)
    kanun_liste.pack(fill="y", expand=True)
    for kod, k in KUTUPHANE.items():
        kanun_liste.insert(tk.END, f"{k['ad']} ({kod})")
    kanun_liste.bind("<<ListboxSelect>>", kanun_secildi)

    # Orta: seçili kanunun maddeleri
    orta = ttk.Frame(govde)
    orta.pack(side="left", fill="y", padx=10)
    ttk.Label(orta, text="Maddeler:").pack(anchor="w")
    madde_liste = tk.Listbox(orta, width=16, height=20, exportselection=False)
    madde_liste.pack(fill="y", expand=True)
    madde_liste.bind("<<ListboxSelect>>", madde_secildi)

    # Sağ: madde metni + kopyala
    sag = ttk.Frame(govde)
    sag.pack(side="left", fill="both", expand=True)
    ttk.Label(sag, text="Madde metni (altına/üstüne bakabilirsiniz):").pack(anchor="w")
    metin_alani = tk.Text(sag, wrap="word", state="disabled")
    metin_alani.pack(fill="both", expand=True)
    kopyala_btn = ttk.Button(sag, text="📋 Maddeyi Kopyala", command=maddeyi_kopyala, state="disabled")
    kopyala_btn.pack(anchor="e", pady=6)

    # Alt: durum çubuğu
    durum = tk.StringVar(value="Bir kanun seçin (örn: Türk Borçlar Kanunu).")
    ttk.Label(kok, textvariable=durum, relief="sunken", anchor="w", padding=4).pack(fill="x")

    # --- "şu maddeyi aç" görsel navigasyon (ana uygulama içinden veya loopback çağırır) ---
    def disaridan_ac(kod, madde):
        """Kanunu+maddeyi seç, kopyala, pencereyi öne getir (hakim açılan maddeyi görür)."""
        kodlar = list(KUTUPHANE.keys())
        if kod not in kodlar:
            return
        i = kodlar.index(kod)
        kanun_liste.selection_clear(0, tk.END)
        kanun_liste.selection_set(i)
        kanun_liste.see(i)
        kanun_secildi()
        maddeler = list(KUTUPHANE[kod]["maddeler"].keys())
        if madde not in maddeler:
            return
        j = maddeler.index(madde)
        madde_liste.selection_clear(0, tk.END)
        madde_liste.selection_set(j)
        madde_liste.see(j)
        madde_secildi()
        maddeyi_kopyala()
        # Görsel: pencereyi öne getir
        try:
            kok.deiconify(); kok.lift()
            kok.attributes("-topmost", True)
            kok.after(900, lambda: kok.attributes("-topmost", False))
            kok.focus_force()
        except Exception:
            pass

    return disaridan_ac


def main():
    """Standalone (2 ayrı .exe modu): kendi penceresi + 127.0.0.1 loopback kontrol sunucusu."""
    import socket
    import threading
    import tkinter as tk

    kok = tk.Tk()
    ac = arayuz_kur(kok)

    def kontrol_sunucusu():
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            srv.bind(("127.0.0.1", KONTROL_PORT))
            srv.listen(5)
        except Exception:
            return
        while True:
            try:
                conn, _ = srv.accept()
                veri = conn.recv(256).decode("utf-8", "ignore")
                conn.close()
                if veri.startswith("AC|"):
                    parc = veri.split("|")
                    if len(parc) >= 3:
                        kok.after(0, lambda k=parc[1], m=parc[2]: ac(k, m))
            except Exception:
                continue

    threading.Thread(target=kontrol_sunucusu, daemon=True).start()
    kok.mainloop()


if __name__ == "__main__":
    main()
