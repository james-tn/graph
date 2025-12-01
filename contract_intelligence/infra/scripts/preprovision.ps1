#!/usr/bin/env pwsh
# Pre-provision hook for Contract Intelligence deployment
# Runs before azd provision to set up prerequisites

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Contract Intelligence - Pre-provision" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptRoot = Split-Path -Parent $PSCommandPath

# Step 1: Validate Azure CLI
Write-Host "✓ Checking Azure CLI..." -ForegroundColor Green
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "  Azure CLI version: $($azVersion.'azure-cli')" -ForegroundColor Gray
} catch {
    Write-Host "✗ Azure CLI not found. Please install: https://aka.ms/azure-cli" -ForegroundColor Red
    exit 1
}

# Step 2: Check Azure login
Write-Host "✓ Checking Azure login..." -ForegroundColor Green
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "  Subscription: $($account.name)" -ForegroundColor Gray
    Write-Host "  Tenant: $($account.tenantId)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Not logged in to Azure. Please run: az login" -ForegroundColor Red
    exit 1
}

# Step 3: Reuse existing AAD apps from OpenAIWorkshop
Write-Host "✓ Configuring Azure AD authentication..." -ForegroundColor Green

# Get existing AAD configuration from OpenAIWorkshop environment
$workshopEnvPath = "$HOME\.azure\ci-dev\.env"
if (Test-Path $workshopEnvPath) {
    Write-Host "  Found Existing AAD configuration, reusing..." -ForegroundColor Gray
    
    # Read AAD values from OpenAIWorkshop
    $workshopEnv = Get-Content $workshopEnvPath | Where-Object { $_ -match '=' } | ForEach-Object {
        $parts = $_ -split '=', 2
        @{
            Key = $parts[0].Trim()
            Value = $parts[1].Trim('"')
        }
    } | Group-Object Key | ForEach-Object { $_.Group[0] }
    
    $aadValues = @{}
    foreach ($item in $workshopEnv) {
        $aadValues[$item.Key] = $item.Value
    }
    
    # Set AAD environment variables for azd
    if ($aadValues['AAD_FRONTEND_CLIENT_ID']) {
        azd env set AAD_FRONTEND_CLIENT_ID $aadValues['AAD_FRONTEND_CLIENT_ID']
        Write-Host "  - Frontend Client ID: $($aadValues['AAD_FRONTEND_CLIENT_ID'])" -ForegroundColor Gray
    }
    
    if ($aadValues['AAD_TENANT_ID']) {
        azd env set AAD_TENANT_ID $aadValues['AAD_TENANT_ID']
        Write-Host "  - Tenant ID: $($aadValues['AAD_TENANT_ID'])" -ForegroundColor Gray
    }
    
    if ($aadValues['AAD_API_APP_ID']) {
        azd env set AAD_API_APP_ID $aadValues['AAD_API_APP_ID']
        Write-Host "  - API App ID: $($aadValues['AAD_API_APP_ID'])" -ForegroundColor Gray
    }
    
    if ($aadValues['AAD_API_AUDIENCE']) {
        azd env set AAD_API_AUDIENCE $aadValues['AAD_API_AUDIENCE']
        Write-Host "  - API Audience: $($aadValues['AAD_API_AUDIENCE'])" -ForegroundColor Gray
    }
    
    # Set DISABLE_AUTH to false (enable authentication)
    azd env set DISABLE_AUTH "false"
    Write-Host "  - Authentication: ENABLED" -ForegroundColor Green
} else {
    Write-Host "  OpenAIWorkshop AAD config not found. Authentication will be DISABLED." -ForegroundColor Yellow
    Write-Host "  To enable auth, set AAD_* variables manually or deploy OpenAIWorkshop first." -ForegroundColor Yellow
    azd env set DISABLE_AUTH "true"
}

# Step 4: Check for existing resources to reuse
Write-Host ""
Write-Host "✓ Checking for existing Azure resources..." -ForegroundColor Green

# Check if user wants to reuse existing OpenAI
$existingOpenAiEndpoint = azd env get-value EXISTING_OPENAI_ENDPOINT 2>$null
if ($existingOpenAiEndpoint) {
    Write-Host "  - Will REUSE existing Azure OpenAI: $existingOpenAiEndpoint" -ForegroundColor Cyan
} else {
    Write-Host "  - Will CREATE new Azure OpenAI account" -ForegroundColor Gray
}

# Check if user wants to reuse existing PostgreSQL
$existingPostgresHost = azd env get-value EXISTING_POSTGRES_HOST 2>$null
if ($existingPostgresHost) {
    Write-Host "  - Will REUSE existing PostgreSQL: $existingPostgresHost" -ForegroundColor Cyan
} else {
    Write-Host "  - Will CREATE new PostgreSQL Flexible Server" -ForegroundColor Gray
    
    # Ensure postgres password is set
    $postgresPassword = azd env get-value POSTGRES_ADMIN_PASSWORD 2>$null
    if (-not $postgresPassword) {
        Write-Host ""
        Write-Host "⚠️  PostgreSQL admin password not set!" -ForegroundColor Yellow
        Write-Host "   Please set it now (minimum 8 characters, must contain uppercase, lowercase, and numbers):" -ForegroundColor Yellow
        $securePassword = Read-Host "   Enter PostgreSQL password" -AsSecureString
        $postgresPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))
        
        azd env set POSTGRES_ADMIN_PASSWORD $postgresPassword --secret
        Write-Host "   ✓ Password saved" -ForegroundColor Green
    } else {
        Write-Host "  - PostgreSQL password: SET" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Pre-provision complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Run 'azd provision' to deploy infrastructure" -ForegroundColor Cyan
Write-Host ""
