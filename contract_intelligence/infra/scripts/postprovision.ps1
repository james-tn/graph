#!/usr/bin/env pwsh
# Post-provision hook for Contract Intelligence deployment
# Runs after azd provision completes

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Contract Intelligence - Post-provision" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Get deployment outputs
$applicationUrl = azd env get-value APPLICATION_URL 2>$null
$postgresHost = azd env get-value POSTGRES_HOST 2>$null
$postgresDatabase = azd env get-value POSTGRES_DATABASE 2>$null
$postgresUser = azd env get-value POSTGRES_USER 2>$null
$postgresPassword = azd env get-value POSTGRES_PASSWORD 2>$null
$openaiEndpoint = azd env get-value AZURE_OPENAI_ENDPOINT 2>$null

Write-Host "✓ Infrastructure deployed successfully!" -ForegroundColor Green
Write-Host ""

# Display important information
Write-Host "📋 Deployment Summary:" -ForegroundColor Cyan
Write-Host "  Application URL: $applicationUrl" -ForegroundColor White
Write-Host "  Azure OpenAI: $openaiEndpoint" -ForegroundColor Gray
Write-Host "  PostgreSQL: $postgresHost" -ForegroundColor Gray
Write-Host ""

# ---------------------------------------------------------------------------
# Run forward-only schema migrations.
# Idempotent (each .sql uses IF NOT EXISTS guards) so it's safe to re-run.
# Skip silently if psql isn't available locally — the deployer can run it
# manually or the migration can be applied from inside the container.
# ---------------------------------------------------------------------------
$migrationsDir = Join-Path $PSScriptRoot "..\..\data_ingestion\migrations"
$migrationsDir = (Resolve-Path $migrationsDir -ErrorAction SilentlyContinue)
$psql = Get-Command psql -ErrorAction SilentlyContinue
if ($migrationsDir -and $psql -and $postgresHost -and $postgresDatabase -and $postgresUser -and $postgresPassword) {
    Write-Host "🗄  Applying schema migrations to $postgresHost ..." -ForegroundColor Cyan
    $env:PGPASSWORD = $postgresPassword
    $migrations = Get-ChildItem -Path $migrationsDir -Filter "*.sql" | Sort-Object Name
    foreach ($m in $migrations) {
        Write-Host "    -> $($m.Name)" -ForegroundColor Gray
        & psql `
            "host=$postgresHost dbname=$postgresDatabase user=$postgresUser sslmode=require" `
            -v ON_ERROR_STOP=1 `
            -f $m.FullName
        if ($LASTEXITCODE -ne 0) {
            Write-Host "    ✗ Migration $($m.Name) failed (exit $LASTEXITCODE)" -ForegroundColor Red
            $env:PGPASSWORD = $null
            exit $LASTEXITCODE
        }
    }
    $env:PGPASSWORD = $null
    Write-Host "    ✓ All migrations applied" -ForegroundColor Green
    Write-Host ""
} elseif ($migrationsDir) {
    Write-Host "ℹ Skipping schema migrations (psql not available or DB info missing)." -ForegroundColor Yellow
    Write-Host "    Run manually:" -ForegroundColor Yellow
    Write-Host "      psql -h $postgresHost -d $postgresDatabase -U $postgresUser -f data_ingestion/migrations/0001_add_ml_link_columns.sql" -ForegroundColor Gray
    Write-Host ""
}

# Remind about data setup
$useExistingPostgres = azd env get-value EXISTING_POSTGRES_HOST 2>$null
if (-not $useExistingPostgres) {
    Write-Host "⚠️  Database Setup Required:" -ForegroundColor Yellow
    Write-Host "  Your NEW PostgreSQL database is empty." -ForegroundColor Yellow
    Write-Host "  Before using the application, you need to:" -ForegroundColor Yellow
    Write-Host "  1. Run data ingestion: python scripts/run_ingestion.py" -ForegroundColor White
    Write-Host "  2. Index GraphRAG data: graphrag index --root graphrag_config" -ForegroundColor White
    Write-Host ""
}

Write-Host "📦 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Build and deploy container: azd deploy" -ForegroundColor White
Write-Host "  2. Access the application: $applicationUrl" -ForegroundColor White
Write-Host "  3. (Optional) Train ML hierarchy linker: python scripts/train_hierarchy_linker.py --bootstrap" -ForegroundColor White
Write-Host "  4. (Optional) Schedule nightly retrain: see scripts/retrain_from_reviews.py" -ForegroundColor White
Write-Host ""

Write-Host "💡 Useful Commands:" -ForegroundColor Cyan
Write-Host "  - View logs: azd logs --follow" -ForegroundColor Gray
Write-Host "  - Redeploy: azd deploy" -ForegroundColor Gray
Write-Host "  - Update infra: azd provision" -ForegroundColor Gray
Write-Host "  - Toggle ML shadow mode: azd env set hierarchyLinkerShadowMode true; azd provision" -ForegroundColor Gray
Write-Host "  - Delete all: azd down" -ForegroundColor Gray
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Deployment ready!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
