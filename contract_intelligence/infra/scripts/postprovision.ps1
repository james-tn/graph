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
$openaiEndpoint = azd env get-value AZURE_OPENAI_ENDPOINT 2>$null

Write-Host "✓ Infrastructure deployed successfully!" -ForegroundColor Green
Write-Host ""

# Display important information
Write-Host "📋 Deployment Summary:" -ForegroundColor Cyan
Write-Host "  Application URL: $applicationUrl" -ForegroundColor White
Write-Host "  Azure OpenAI: $openaiEndpoint" -ForegroundColor Gray
Write-Host "  PostgreSQL: $postgresHost" -ForegroundColor Gray
Write-Host ""

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
Write-Host ""

Write-Host "💡 Useful Commands:" -ForegroundColor Cyan
Write-Host "  - View logs: azd logs --follow" -ForegroundColor Gray
Write-Host "  - Redeploy: azd deploy" -ForegroundColor Gray
Write-Host "  - Update infra: azd provision" -ForegroundColor Gray
Write-Host "  - Delete all: azd down" -ForegroundColor Gray
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Deployment ready!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
