# ============================================================
#  Pierinelli - arranque local de Odoo (Windows / PowerShell)
#  Garantiza que wkhtmltopdf este en el PATH para que los PDF
#  (reportes, facturas, estados financieros) se generen bien.
# ============================================================

# wkhtmltopdf 0.12.6 (patched qt) - requerido por Odoo para PDF.
# Se buscan varias rutas: la instalacion en E: (disco de desarrollo) primero,
# y la ruta por defecto de winget en C: como alternativa.
$rutasWk = @(
    "E:\DevTools\wkhtmltopdf\bin",
    "C:\Program Files\wkhtmltopdf\bin"
)
foreach ($wk in $rutasWk) {
    if ((Test-Path "$wk\wkhtmltopdf.exe") -and ($env:Path -notlike "*$wk*")) {
        $env:Path = "$wk;$env:Path"
        break
    }
}

# Verificacion rapida
$found = Get-Command wkhtmltopdf -ErrorAction SilentlyContinue
if ($found) {
    Write-Host ">>> wkhtmltopdf listo: $($found.Source)" -ForegroundColor Green
} else {
    Write-Host ">>> AVISO: wkhtmltopdf no encontrado. Descarga 0.12.6-1 msvc2015-win64 de" -ForegroundColor Yellow
    Write-Host "    github.com/wkhtmltopdf/packaging/releases/tag/0.12.6-1" -ForegroundColor Yellow
    Write-Host "    e instala con:  .\wkhtmltox.exe /S /D=E:\DevTools\wkhtmltopdf" -ForegroundColor Yellow
}

Write-Host ">>> Iniciando Odoo en http://localhost:8069 (Ctrl+C para detener)" -ForegroundColor Cyan
& ".venv\Scripts\python.exe" "odoo\odoo-bin" -c "odoo.conf"
