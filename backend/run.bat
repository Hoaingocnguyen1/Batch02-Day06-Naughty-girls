@echo off
echo ===================================================
echo [STARTING] Khoi dong FastAPI Backend tren Localhost
echo ===================================================
echo.
echo [1/2] Dang kiem tra va cai dat dependencies...
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Loi khi cai dat requirements!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Dang khoi chay uvicorn dev server...
echo.
echo Địa chỉ Backend: http://127.0.0.1:8000
echo Doc API: http://127.0.0.1:8000/docs
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Uvicorn khong the khoi chay!
    pause
    exit /b %ERRORLEVEL%
)

pause
