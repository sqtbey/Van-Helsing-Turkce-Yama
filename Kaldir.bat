@echo off
chcp 65001 >nul
title The Incredible Adventures of Van Helsing - Turkce Yama Kaldirici
color 0C

echo =====================================================================
echo      The Incredible Adventures of Van Helsing - Yama Kaldirici
echo =====================================================================
echo.

set "SOURCE_DIR=%~dp0"
set "GAME_DIR="

if exist "%SOURCE_DIR%VanHelsing_x64.exe" (
    set "GAME_DIR=%SOURCE_DIR%"
) else if exist "%SOURCE_DIR%..\VanHelsing_x64.exe" (
    pushd "%SOURCE_DIR%.."
    set "GAME_DIR=%CD%"
    popd
) else if exist "C:\Program Files (x86)\Steam\steamapps\common\The Incredible Adventures of Van Helsing\VanHelsing_x64.exe" (
    set "GAME_DIR=C:\Program Files (x86)\Steam\steamapps\common\The Incredible Adventures of Van Helsing"
)

if "%GAME_DIR%"=="" (
    echo [HATA] Oyun klasoru bulunamadi!
    pause
    exit /b 1
)

set "STRINGS_DIR=%GAME_DIR%\Strings"
set "VIDEOS_DIR=%GAME_DIR%\Videos\ENG"

if exist "%STRINGS_DIR%\Files.N2PK.original_backup" (
    echo [BILGI] Orijinal dil paketi geri yukleniyor...
    copy /Y "%STRINGS_DIR%\Files.N2PK.original_backup" "%STRINGS_DIR%\Files.N2PK" >nul
    echo [BASARILI] Orijinal Files.N2PK geri yuklendi.
) else (
    echo [UYARI] Orijinal yedek bulunamadi. Steam uzerinden dosya dogrulama yapabilirsiniz.
)

if exist "%VIDEOS_DIR%\intro.srt.original_backup" (
    echo [BILGI] Orijinal video altyazilari geri yukleniyor...
    copy /Y "%VIDEOS_DIR%\intro.srt.original_backup" "%VIDEOS_DIR%\intro.srt" >nul
    copy /Y "%VIDEOS_DIR%\chapter1_vege.srt.original_backup" "%VIDEOS_DIR%\chapter1_vege.srt" >nul
    copy /Y "%VIDEOS_DIR%\outro.srt.original_backup" "%VIDEOS_DIR%\outro.srt" >nul
    echo [BASARILI] Orijinal video altyazilari geri yuklendi.
)

echo.
echo =====================================================================
echo               [BASARILI] YAMA KALDIRILDI!
echo =====================================================================
echo.
pause
