@echo off
title RescuEU - Sistema SAMU
echo ===================================================
echo   Iniciando o Sistema RescuEU (Bauru-SP)
echo ===================================================

if not exist venv (
    echo [1/3] Criando ambiente virtual Python...
    python -m venv venv
)

echo [2/3] Ativando ambiente virtual e verificando dependencias...
call .\venv\Scripts\activate
pip install -r requirements.txt

echo [3/3] Executando a aplicacao web...
python -m streamlit run src/app.py

pause