<#
.SYNOPSIS
Builds the Contract Intelligence container image, pushes it to Azure Container Registry, and deploys the Container App wired up to existing Azure OpenAI and PostgreSQL resources by reading their settings from a .env file.

.DESCRIPTION
- Reads required configuration values (OpenAI + PostgreSQL) from the supplied .env file so the hosted app behaves the same as the local dev experience.
- Ensures the resource group, Container Apps environment, and Azure Container Registry exist (creating them if needed).
- Builds the Dockerfile in the repo root and pushes the image into the registry.
- Configures Container App secrets/env vars so sensitive values stay encrypted, while non-secret settings are injected as regular env vars.
- Works entirely through Azure CLI so azd is not required.

.EXAMPLE
pwsh ./scripts/deploy-containerapp.ps1 `
  -SubscriptionId "00000000-0000-0000-0000-000000000000" `
  -ResourceGroup "ci-app-rg" `
  -Location "eastus2" `
  -ContainerAppEnvironment "ci-app-env" `
  -ContainerAppName "ci-app" `
  -AcrName "ciappacr001" `
  -ImageRepository "contract-intelligence/backend" `
  -EnvFile "../.env"
#>
param(
    [string]$SubscriptionId,
    [string]$EnvFile = "$PSScriptRoot/../.env",
    [string]$ResourceGroup = "ci-app-rg",
    [string]$Location = "eastus2",
    [string]$ContainerAppEnvironment = "ci-app-env",
    [string]$ContainerAppName = "ci-app",
    [string]$AcrName = "ciappacr001",
    [string]$ImageRepository = "contract-intelligence/backend",
    [switch]$UseLocalDockerBuild
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Invoke-AzCli {
    param([string[]]$Arguments)
    # Redirect stderr to $null so that az CLI warnings (e.g. "Preview versions
    # allowed") are silently discarded and don't trigger terminating errors.
    $result = $(az @Arguments 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "Azure CLI command failed (exit $LASTEXITCODE): az $($Arguments -join ' ')"
    }
    return $result
}

function Invoke-AzCliJson {
    param([string[]]$Arguments)
    $json = Invoke-AzCli -Arguments $Arguments
    if ($json -is [System.Array]) {
        $json = [string]::Join([Environment]::NewLine, $json)
    }
    if ([string]::IsNullOrWhiteSpace($json)) {
        return $null
    }
    $trimmed = $json.Trim()
    $startIndex = $trimmed.IndexOfAny(@('{', '['))
    if ($startIndex -ge 0) {
        $trimmed = $trimmed.Substring($startIndex)
    }
    return $trimmed | ConvertFrom-Json
}

function Invoke-LocalCommand {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter()][string[]]$Arguments
    )
    $output = $(& $Executable @Arguments 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed (exit $LASTEXITCODE): $Executable $($Arguments -join ' ')"
    }
    return $output
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
    throw "Cannot find .env file at '$EnvFile'"
}

$rawEnv = Get-Content -LiteralPath $EnvFile | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
$envMap = @{}
foreach ($line in $rawEnv) {
    $trimmed = $line.Trim()
    if ($trimmed.StartsWith('#')) { continue }
    $separatorIndex = $trimmed.IndexOf('=')
    if ($separatorIndex -lt 1) { continue }
    $key = $trimmed.Substring(0, $separatorIndex).Trim()
    $value = $trimmed.Substring($separatorIndex + 1).Trim().Trim('"')
    if (-not [string]::IsNullOrWhiteSpace($key)) {
        $envMap[$key] = $value
    }
}

$requiredKeys = @(
    'AZURE_OPENAI_API_KEY',
    'AZURE_OPENAI_ENDPOINT',
    'AZURE_OPENAI_DEPLOYMENT_NAME',
    'EMBEDDING_DEPLOYMENT_NAME',
    'POSTGRES_HOST',
    'POSTGRES_DATABASE',
    'POSTGRES_USER',
    'POSTGRES_ADMIN_PASSWORD'
)
foreach ($key in $requiredKeys) {
    if (-not $envMap.ContainsKey($key) -or [string]::IsNullOrWhiteSpace($envMap[$key])) {
        throw "Missing required '$key' entry in $EnvFile"
    }
}

if (-not $SubscriptionId) {
    $SubscriptionId = (Invoke-AzCli @('account', 'show', '--query', 'id', '-o', 'tsv')).Trim()
}
Invoke-AzCli @('account', 'set', '--subscription', $SubscriptionId) | Out-Null

Write-Host "Ensuring Azure CLI Container Apps extension is available..."
Invoke-AzCli @('extension', 'add', '--name', 'containerapp', '--upgrade') | Out-Null

Write-Host "Ensuring resource group '$ResourceGroup' exists..."
Invoke-AzCli @('group', 'create', '--name', $ResourceGroup, '--location', $Location, '--only-show-errors') | Out-Null

Write-Host "Ensuring Azure Container Registry '$AcrName' exists..."
try {
    $acr = Invoke-AzCliJson @('acr', 'show', '--name', $AcrName, '--resource-group', $ResourceGroup, '--only-show-errors', '-o', 'json')
} catch {
    $acr = $null
}
if (-not $acr) {
    $acr = Invoke-AzCliJson @('acr', 'create', '--name', $AcrName, '--resource-group', $ResourceGroup, '--location', $Location, '--sku', 'Basic', '--admin-enabled', 'true', '--only-show-errors', '-o', 'json')
}
$acrLoginServer = $acr.loginServer

$timestamp = Get-Date -Format 'yyyyMMddHHmmss'
$imageTag = "$acrLoginServer/${ImageRepository}:$timestamp"

if ($UseLocalDockerBuild) {
    Write-Host "Building image '$imageTag' locally with Docker..."
    Invoke-AzCli @('acr', 'login', '--name', $AcrName) | Out-Null
    Invoke-LocalCommand -Executable 'docker' -Arguments @('build', '--file', 'Dockerfile', '--tag', $imageTag, '.') | Out-Null
    Write-Host "Pushing '$imageTag' to $acrLoginServer via docker push..."
    Invoke-LocalCommand -Executable 'docker' -Arguments @('push', $imageTag) | Out-Null
} else {
    Write-Host "Building and pushing image '$imageTag' via ACR build (this can take several minutes)..."
    Invoke-AzCli @('acr', 'build', '--registry', $AcrName, '--image', "${ImageRepository}:$timestamp", '--file', 'Dockerfile', '.') | Out-Null
}

Write-Host "Ensuring Container Apps environment '$ContainerAppEnvironment' exists..."
try {
    $cae = Invoke-AzCliJson @('containerapp', 'env', 'show', '--name', $ContainerAppEnvironment, '--resource-group', $ResourceGroup, '--only-show-errors', '-o', 'json')
} catch {
    $cae = $null
}
if (-not $cae) {
    $cae = Invoke-AzCliJson @('containerapp', 'env', 'create', '--name', $ContainerAppEnvironment, '--resource-group', $ResourceGroup, '--location', $Location, '--only-show-errors', '-o', 'json')
}

$acrCredentials = Invoke-AzCliJson @('acr', 'credential', 'show', '--name', $AcrName, '--resource-group', $ResourceGroup, '--only-show-errors', '-o', 'json')
$acrUserName = $acrCredentials.username
$acrPassword = $acrCredentials.passwords[0].value

$secretArgs = @(
    "openai-key=$($envMap['AZURE_OPENAI_API_KEY'])",
    "postgres-password=$($envMap['POSTGRES_ADMIN_PASSWORD'])"
)

$envVarArgs = @(
    "AZURE_OPENAI_API_KEY=secretref:openai-key",
    "AZURE_OPENAI_ENDPOINT=$($envMap['AZURE_OPENAI_ENDPOINT'])",
    "AZURE_OPENAI_DEPLOYMENT_NAME=$($envMap['AZURE_OPENAI_DEPLOYMENT_NAME'])",
    "EMBEDDING_DEPLOYMENT_NAME=$($envMap['EMBEDDING_DEPLOYMENT_NAME'])",
    "POSTGRES_HOST=$($envMap['POSTGRES_HOST'])",
    "POSTGRES_DATABASE=$($envMap['POSTGRES_DATABASE'])",
    "POSTGRES_USER=$($envMap['POSTGRES_USER'])",
    "POSTGRES_ADMIN_PASSWORD=secretref:postgres-password"
)

if ($envMap.ContainsKey('AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME')) { $envVarArgs += "AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME=$($envMap['AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME'])" }
# agent-framework rc1 looks for AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
if ($envMap.ContainsKey('AZURE_OPENAI_DEPLOYMENT_NAME')) { $envVarArgs += "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=$($envMap['AZURE_OPENAI_DEPLOYMENT_NAME'])" }
# Auth settings (pass through if present)
if ($envMap.ContainsKey('DISABLE_AUTH')) { $envVarArgs += "DISABLE_AUTH=$($envMap['DISABLE_AUTH'])" }
if ($envMap.ContainsKey('AAD_API_APP_ID')) { $envVarArgs += "AAD_API_APP_ID=$($envMap['AAD_API_APP_ID'])" }
if ($envMap.ContainsKey('AAD_API_AUDIENCE')) { $envVarArgs += "AAD_API_AUDIENCE=$($envMap['AAD_API_AUDIENCE'])" }
if ($envMap.ContainsKey('AAD_API_TENANT_ID')) { $envVarArgs += "AAD_API_TENANT_ID=$($envMap['AAD_API_TENANT_ID'])" }
if ($envMap.ContainsKey('AAD_FRONTEND_CLIENT_ID')) { $envVarArgs += "AAD_FRONTEND_CLIENT_ID=$($envMap['AAD_FRONTEND_CLIENT_ID'])" }
if ($envMap.ContainsKey('AAD_FRONTEND_TENANT_ID')) { $envVarArgs += "AAD_FRONTEND_TENANT_ID=$($envMap['AAD_FRONTEND_TENANT_ID'])" }

function Set-ContainerApp {
    param([bool]$IsCreate)
    if ($IsCreate) {
        $baseArgs = @(
            'containerapp', 'create',
            '--name', $ContainerAppName,
            '--resource-group', $ResourceGroup,
            '--environment', $ContainerAppEnvironment,
            '--image', $imageTag,
            '--cpu', '2',
            '--memory', '4Gi',
            '--min-replicas', '1',
            '--max-replicas', '3',
            '--ingress', 'external',
            '--target-port', '8000',
            '--registry-server', $acrLoginServer,
            '--registry-username', $acrUserName,
            '--registry-password', $acrPassword,
            '--secrets'
        ) + $secretArgs + @('--env-vars') + $envVarArgs
    } else {
        $baseArgs = @(
            'containerapp', 'update',
            '--name', $ContainerAppName,
            '--resource-group', $ResourceGroup,
            '--image', $imageTag,
            '--cpu', '2',
            '--memory', '4Gi',
            '--min-replicas', '1',
            '--max-replicas', '3',
            '--set-env-vars'
        ) + $envVarArgs
    }

    Invoke-AzCli -Arguments $baseArgs | Out-Null
}

try {
    Invoke-AzCli @('containerapp', 'show', '--name', $ContainerAppName, '--resource-group', $ResourceGroup, '--only-show-errors') | Out-Null
    $exists = $true
} catch {
    $exists = $false
}

if ($exists) {
    Write-Host "Updating secrets for existing Container App '$ContainerAppName'..."
    $secretCommand = @('containerapp', 'secret', 'set', '--name', $ContainerAppName, '--resource-group', $ResourceGroup, '--secrets') + $secretArgs
    Invoke-AzCli -Arguments $secretCommand | Out-Null
    Write-Host "Updating Container App '$ContainerAppName' with new image and settings..."
    Set-ContainerApp -IsCreate:$false
} else {
    Write-Host "Creating Container App '$ContainerAppName'..."
    Set-ContainerApp -IsCreate:$true
}

$fqdnRaw = Invoke-AzCli @('containerapp', 'show', '--name', $ContainerAppName, '--resource-group', $ResourceGroup, '--query', 'properties.configuration.ingress.fqdn', '-o', 'tsv')
if ($fqdnRaw -is [System.Array]) {
    $fqdnRaw = $fqdnRaw[-1]
}
$fqdn = $fqdnRaw.Trim()
Write-Host "Deployment completed. App URL: https://$fqdn" -ForegroundColor Green
