# E-Duruşma Katibi — GPU (NVIDIA) Sürümü

En zeki + instant + tam offline. **Şart: NVIDIA ekran kartı + güncel sürücü.**
Model: **Whisper large-v3** (piyasanın en doğrusu), GPU'da çok hızlı çalışır.

## KURULUM (bir kez, NVIDIA'lı PC'de)
1. **Python 3.11** kur (python.org → "Add to PATH").
2. Bu klasörü PC'ye kopyala.
3. **KUR_GPU.bat** çift tık. (Kütüphaneler + CUDA kurulur.)

## ÇALIŞTIRMA
- **CALISTIR_GPU.bat** çift tık. Şifre **1234**.
- İlk açılışta **large-v3 ~3GB iner (BİR KEZ internet)**. Sonra tamamen offline + GPU'da instant.
- Durumda **"Model hazır (GPU ⚡)"** yazmalı.
  - "Model hazır (CPU)" yazıyorsa → NVIDIA sürücü/CUDA eksik (GPU bulunamadı), CPU'da yavaş çalışır.

## NEDEN KAYNAKTAN (exe değil)?
GPU + CUDA'yı tek .exe'ye paketlemek çok kırılgan + ~4.5GB olur (yavaş indirme).
Kaynaktan çalıştırma GPU'da en güvenilir ve modeli bir kez indirir.
Yine de tek-exe istersen yapılır (riskli).

## Kullanım / komutlar
- Mikrofon seç → 🎤 Test → editör aç → ▶ Başlat → konuş.
- Komutlar: "yeni paragraf", "geri al"/"sil", "kelime sil", "Word'e geç",
  "borçlar kanunu madde 49 getir". (Detay: ana NOTLAR.)

## Gizlilik
Ses/metin diske yazılmaz, internete gönderilmez (model bir kez indikten sonra). Tam offline.
