# ============================================================
#  Pierinelli - arranque local de Odoo (Windows / PowerShell)
#  Garantiza que wkhtmltopdf este en el PATH para que los PDF
#  (reportes, facturas, estados financieros) se generen bien.
# ============================================================

# wkhtmltopdf 0.12.6 (patched qt) - requerido por Odoo para PDF
$wk = "C:\Program Files\wkhtmltopdf\bin"
if ((Test-Path $wk) -and ($env:Path -notlike "*$wk*")) {
    $env:Path = "$wk;$env:Path"
}

# Verificacion rapida
$found = Get-Command wkhtmltopdf -ErrorAction SilentlyContinue
if ($found) {
    Write-Host ">>> wkhtmltopdf listo: $($found.Source)" -ForegroundColor Green
} else {
    Write-Host ">>> AVISO: wkhtmltopdf no encontrado. Instala con: winget install wkhtmltopdf.wkhtmltox" -ForegroundColor Yellow
}

Write-Host ">>> Iniciando Odoo en http://localhost:8069 (Ctrl+C para detener)" -ForegroundColor Cyan
& ".venv\Scripts\python.exe" "odoo\odoo-bin" -c "odoo.conf"
