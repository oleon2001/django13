# Script PowerShell para iniciar el sistema GPS en Windows
# Ejecutar con: powershell -ExecutionPolicy Bypass -File start_gps_windows.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    INICIANDO SISTEMA GPS SKYGUARD" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan

# Obtener la ruta actual
$projectPath = "C:\Users\oswaldo\Desktop\django13"
Set-Location $projectPath

# Función para abrir nueva ventana de PowerShell
function Start-NewPowerShell {
    param(
        [string]$Title,
        [string]$Command
    )
    
    $psCommand = @"
cd '$projectPath'
`$host.UI.RawUI.WindowTitle = '$Title'
Write-Host '======================================' -ForegroundColor Cyan
Write-Host '  $Title' -ForegroundColor Yellow
Write-Host '======================================' -ForegroundColor Cyan
$Command
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $psCommand
}

Write-Host "`n[1/5] Verificando entorno virtual..." -ForegroundColor Green
if (Test-Path ".\venv\Scripts\activate.ps1") {
    Write-Host "✓ Entorno virtual encontrado" -ForegroundColor Green
} else {
    Write-Host "✗ Entorno virtual no encontrado. Creándolo..." -ForegroundColor Red
    python -m venv venv
}

Write-Host "`n[2/5] Registrando dispositivo PC..." -ForegroundColor Green
& ".\venv\Scripts\python.exe" register_pc_device.py

Write-Host "`n[3/5] Iniciando servicios..." -ForegroundColor Green

# Backend Django
Write-Host "  → Iniciando Backend Django..." -ForegroundColor Cyan
Start-NewPowerShell -Title "Django Backend" -Command ".\venv\Scripts\activate; python manage.py runserver"
Start-Sleep -Seconds 3

# Servidor GPS Django
Write-Host "  → Iniciando Servidor GPS Django..." -ForegroundColor Cyan
Start-NewPowerShell -Title "GPS Server (Django)" -Command ".\venv\Scripts\activate; python start_django_gps_server.py"
Start-Sleep -Seconds 3

# Simulador GPS
Write-Host "  → Iniciando Simulador GPS..." -ForegroundColor Cyan
Start-NewPowerShell -Title "GPS Simulator" -Command ".\venv\Scripts\activate; python pc_gps_simulator.py"
Start-Sleep -Seconds 2

# Frontend React
Write-Host "  → Iniciando Frontend React..." -ForegroundColor Cyan
Start-NewPowerShell -Title "React Frontend" -Command "cd frontend; npm start"

Write-Host "`n[4/5] Esperando que los servicios estén listos..." -ForegroundColor Green
Start-Sleep -Seconds 10

Write-Host "`n[5/5] Verificando dispositivo en BD..." -ForegroundColor Green
& ".\venv\Scripts\python.exe" check_pc_device.py

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✓ SISTEMA INICIADO CORRECTAMENTE" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`nURLs disponibles:" -ForegroundColor Yellow
Write-Host "  • Frontend: " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host "  • Dashboard: " -NoNewline; Write-Host "http://localhost:3000/dashboard" -ForegroundColor Cyan
Write-Host "  • Backend API: " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "  • Django Admin: " -NoNewline; Write-Host "http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host "`nPara detener todos los servicios:" -ForegroundColor Yellow
Write-Host "  Cierra todas las ventanas de PowerShell" -ForegroundColor White
Write-Host "`n"

# Mantener esta ventana abierta
Read-Host "Presiona Enter para salir" 