@echo off
chcp 65001 >nul
echo E-Durusma Katibi (GPU) baslatiliyor...
echo "Model hazir (GPU)" yazmali. CPU yaziyorsa NVIDIA surucu/CUDA eksik demektir.
python e_durusma_katibi.py
pause
