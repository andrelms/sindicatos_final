@echo off
echo Instalando dependencias minimas...
pip install flask jinja2 werkzeug

echo.
echo Iniciando o servidor...
python test_app.py