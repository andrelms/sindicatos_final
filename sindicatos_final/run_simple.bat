@echo off
echo Iniciando Sistema de Automacao de Sindicatos...
echo.

REM Limpar caches Python que podem causar conflitos
echo Limpando cache...
del /s /q *.pyc >nul 2>&1
rmdir /s /q __pycache__ >nul 2>&1
rmdir /s /q app\__pycache__ >nul 2>&1
rmdir /s /q backend\__pycache__ >nul 2>&1

REM Remover ambiente virtual antigo se existir
if exist "venv" (
    echo Removendo ambiente virtual antigo...
    rmdir /s /q venv
)

REM Criar novo ambiente virtual
echo Criando novo ambiente virtual...
python -m venv venv
call venv\Scripts\activate

REM Instalar dependências mínimas
echo Instalando dependencias...
pip install flask==2.3.3
pip install flask-sqlalchemy==3.1.1
pip install python-dotenv==1.0.0
pip install werkzeug==2.3.7

REM Configurar variáveis
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1
set PYTHONPATH=.

REM Criar arquivo .env se não existir
if not exist ".env" (
    echo Criando arquivo .env...
    echo FLASK_APP=app.py > .env
    echo FLASK_ENV=development >> .env
    echo SECRET_KEY=dev >> .env
)

echo.
echo Servidor iniciando em http://localhost:5000
echo Pressione Ctrl+C para parar o servidor
echo.

python -c "from app import create_app; app = create_app(); app.run(debug=True, port=5000)"