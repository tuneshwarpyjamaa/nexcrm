Write-Host "Running Database Migrations..." -ForegroundColor Cyan
cd backend
alembic upgrade head
if ($LASTEXITCODE -eq 0) {
    Write-Host "Migrations completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Migrations failed!" -ForegroundColor Red
}
