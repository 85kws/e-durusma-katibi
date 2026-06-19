@echo off
chcp 65001 >nul
echo ==========================================================
echo  E-Durusma Katibi - GPU (NVIDIA) KURULUM
echo ==========================================================
echo.
echo ONEMLI: Bu PC'de NVIDIA ekran karti + GUNCEL surucu olmali.
echo.
echo 1) Python kutuphaneleri + CUDA kutuphaneleri kuruluyor...
python -m pip install -r requirements_gpu.txt
if errorlevel 1 ( echo HATA: Python kurulu mu? ^(python.org, Add to PATH^) & pause & exit /b 1 )
echo.
echo KURULUM BITTI.
echo Calistirmak icin: CALISTIR_GPU.bat
echo (Ilk calistirmada large-v3 modeli ~3GB iner - BIR KEZ internet gerekir.
echo  Sonra tamamen OFFLINE ve GPU'da INSTANT calisir.)
pause
