@echo off
chcp 65001 >nul
title The Incredible Adventures of Van Helsing - Turkce Yama Kurulumu
color 0A

echo =====================================================================
echo      The Incredible Adventures of Van Helsing - Turkce Yama
echo                     Gelistirici: sqtbey
echo =====================================================================
echo.

set "SOURCE_DIR=%~dp0"
set "GAME_DIR="

:: 1. Eger yama oyun klasoru icindeyse tespit et
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
    echo [HATA] Oyun klasoru otomatik tespit edilemedi!
    echo Lutfen bu klasordeki dosyalari oyunun kurulu oldugu ana dizine kopyalayin.
    echo.
    pause
    exit /b 1
)

echo [BILGI] Oyun dizini tespit edildi:
echo "%GAME_DIR%"
echo.

set "STRINGS_DIR=%GAME_DIR%\Strings"
set "VIDEOS_DIR=%GAME_DIR%\Videos\ENG"

if not exist "%STRINGS_DIR%" (
    echo [HATA] Strings klasoru bulunamadi!
    pause
    exit /b 1
)

:: Yedekleme
if not exist "%STRINGS_DIR%\Files.N2PK.original_backup" (
    echo [BILGI] Orijinal dil paketi yedekleniyor...
    copy "%STRINGS_DIR%\Files.N2PK" "%STRINGS_DIR%\Files.N2PK.original_backup" >nul
    echo [BASARILI] Orijinal dil paketi yedeklendi.
)

:: N2PK Kopyalama
echo [BILGI] Turkce dil paketi yukleniyor...
copy /Y "%SOURCE_DIR%Files.N2PK" "%STRINGS_DIR%\Files.N2PK" >nul

:: Video Altyazilari
if exist "%SOURCE_DIR%Videos\ENG" (
    echo [BILGI] Video altyazilari yukleniyor...
    if not exist "%VIDEOS_DIR%\intro.srt.original_backup" (
        if exist "%VIDEOS_DIR%\intro.srt" copy "%VIDEOS_DIR%\intro.srt" "%VIDEOS_DIR%\intro.srt.original_backup" >nul
        if exist "%VIDEOS_DIR%\chapter1_vege.srt" copy "%VIDEOS_DIR%\chapter1_vege.srt" "%VIDEOS_DIR%\chapter1_vege.srt.original_backup" >nul
        if exist "%VIDEOS_DIR%\outro.srt" copy "%VIDEOS_DIR%\outro.srt" "%VIDEOS_DIR%\outro.srt.original_backup" >nul
    )
    copy /Y "%SOURCE_DIR%Videos\ENG\*.srt" "%VIDEOS_DIR%\" >nul
)

echo.
echo =====================================================================
echo               [BASARILI] TURKCE YAMA KURULDU!
echo =====================================================================
echo.
echo - Tum gorevler, diyaloglar ve aciklamalar Turkcelestirildi.
echo - Ozel isimler ve esya adlari orijinal birakildi.
echo - Oyunu Steam uzerinden baslatip hemen oynayabilirsiniz.
echo.
pause
