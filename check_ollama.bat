@echo off
setlocal enabledelayedexpansion

echo ==========================
echo RAG Application Launcher
echo ==========================
echo.

:: Set model variables
set "MODEL_NAME= llama3.2:1b"
set "APP_PATH=%dp0aAI-RAG-APP.exe"
set "OLLAMA_INSTALLER_PATH = %TEMP%\OllamaSetup.exe"
set "OLLAMA_INSTALLER_URL = https://ollama.com/download/windows/OllamaSetup.exe"

:: Check if OLLAMA in PATH Environment variables
where ollama > nul 2>nul
if %ERRORLEVEL% EQU 0(
    echo Ollama already in PATH.
    goto CheckModel
)

:: Check common install path
set "OLLAMA_EXE = %LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if exist "%OLLAMA_EXE" (
    echo ollama found in default location
    set "PATH = %LOCALAPPDATA%\Programs\Ollama;%PATH%"
    goto CheckModel
)

:: Ollama not found, install it
echo Ollama not found. Downloading and Installing...
powershell -Comand "Invoke-WebRequest -Uri '%OLLAMA_INSTALLER_URL%' -OutFile '%OLLAMA_INSTALLER_PATH%'"
start /wait "" "%OLLAMA_INSTALLER_PATH%"

set "PATH = %LOCALAPPDATA%\Programs\Ollama;%PATH%"


:CheckModel
:: Check if LLM is installed or not

ollama list | findstr /C:"%MODEL_NAME%" >nul
if %ERRORLEVEL% NEQ 0 (
    echo LLM Not found. Pulling LLM %MODEL_NAME%
    ollama pull %MODEL_NAME%
) else (
    echo LLM %MODEL_NAME% already exists
)

:: Start Ollama
start "" ollama serve
timeout /t 2>nul

:: Run the App
start "" "%APP_PATH%"


endlocal





