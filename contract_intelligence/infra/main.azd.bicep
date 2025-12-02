// Main infrastructure template for Contract Intelligence
// Deploys: Container Apps, PostgreSQL, Azure OpenAI (conditional), Container Registry, Managed Identity
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment (used for resource naming)')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string = 'eastus2'

@description('Base name for all resources')
param baseName string = 'ci'

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Principal type: User or ServicePrincipal')
param principalType string = 'User'

// Existing Resource Parameters
@description('Existing Azure OpenAI endpoint (if reusing)')
param existingOpenAiEndpoint string = ''

@description('Existing Azure OpenAI chat deployment name')
param existingOpenAiDeploymentName string = ''

@description('Existing Azure OpenAI embedding deployment name')
param existingOpenAiEmbeddingDeploymentName string = ''

@description('Existing Azure OpenAI resource ID (required when the account lives in another resource group or subscription)')
param existingOpenAiResourceId string = ''

@description('Existing PostgreSQL host (if reusing)')
param existingPostgresHost string = ''

@description('Existing PostgreSQL database name')
param existingPostgresDatabase string = ''

@description('Existing PostgreSQL username')
param existingPostgresUser string = ''

@secure()
@description('Existing PostgreSQL password')
param existingPostgresPassword string = ''

// New Resource Parameters
@secure()
@description('PostgreSQL admin password (required if NOT using existing)')
param postgresAdminPassword string = ''

@description('PostgreSQL database name')
param postgresDatabaseName string = 'cipgraph'

// Azure AD Authentication
@description('Azure AD Frontend Client ID')
param aadFrontendClientId string = ''

@description('Azure AD Frontend Tenant ID')
param aadFrontendTenantId string = ''

@description('Azure AD API Tenant ID')
param aadApiTenantId string = ''

@description('Azure AD API App ID')
param aadApiAppId string = ''

@description('Azure AD API Audience')
param aadApiAudience string = ''

@description('Disable authentication')
param disableAuth string = 'false'

// Container image name (populated by azd deploy)
param backendImageName string = ''

var tags = {
  'azd-env-name': environmentName
  Application: 'Contract-Intelligence'
}

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var prefix = '${baseName}-${resourceToken}'
var managedIdentityName = '${prefix}-identity'

// Determine if we're using existing resources
var useExistingOpenAI = !empty(existingOpenAiEndpoint)
var useExistingPostgres = !empty(existingPostgresHost)
var hasExistingOpenAiResourceId = !empty(existingOpenAiResourceId)
var existingOpenAiSegments = split(existingOpenAiResourceId, '/')
var existingOpenAiSubscriptionId = hasExistingOpenAiResourceId ? existingOpenAiSegments[2] : ''
var existingOpenAiResourceGroupName = hasExistingOpenAiResourceId ? existingOpenAiSegments[4] : ''
var existingOpenAiAccountName = hasExistingOpenAiResourceId ? existingOpenAiSegments[8] : ''
var deployOpenAiModule = !useExistingOpenAI || !hasExistingOpenAiResourceId
var cognitiveServicesOpenAIUserRoleId = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'

// ==================== RESOURCE GROUP ====================
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${prefix}-rg'
  location: location
  tags: tags
}

// ==================== MANAGED IDENTITY ====================
module managedIdentity 'modules/managed-identity.bicep' = {
  scope: rg
  name: 'managed-identity'
  params: {
    location: location
    baseName: prefix
    tags: tags
  }
}

// ==================== AZURE OPENAI (conditional) ====================
module openai 'modules/openai.bicep' = if (deployOpenAiModule) {
  scope: rg
  name: 'openai'
  params: {
    location: location
    baseName: prefix
    tags: tags
    useExistingOpenAI: useExistingOpenAI
    existingOpenAiEndpoint: existingOpenAiEndpoint
    existingOpenAiDeploymentName: existingOpenAiDeploymentName
    existingOpenAiEmbeddingDeploymentName: existingOpenAiEmbeddingDeploymentName
    principalId: managedIdentity.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

// Role assignment path for cross-resource-group OpenAI reuse
module openaiExternalRole 'modules/openai-external-role.bicep' = if (useExistingOpenAI && hasExistingOpenAiResourceId) {
  scope: resourceGroup(existingOpenAiSubscriptionId, existingOpenAiResourceGroupName)
  name: 'openai-external-role'
  params: {
    accountName: existingOpenAiAccountName
    cognitiveServicesOpenAIUserRoleId: cognitiveServicesOpenAIUserRoleId
    principalId: managedIdentity.outputs.principalId
    principalType: 'ServicePrincipal'
    roleAssignmentName: guid(existingOpenAiResourceId, managedIdentityName, cognitiveServicesOpenAIUserRoleId)
  }
}

var resolvedOpenAiEndpoint = deployOpenAiModule ? openai.outputs.endpoint : existingOpenAiEndpoint
var resolvedOpenAiDeploymentName = deployOpenAiModule ? openai.outputs.chatDeploymentName : existingOpenAiDeploymentName
var resolvedOpenAiEmbeddingDeploymentName = deployOpenAiModule ? openai.outputs.embeddingDeploymentName : existingOpenAiEmbeddingDeploymentName

// ==================== POSTGRESQL (conditional) ====================
module postgres 'modules/postgres.bicep' = {
  scope: rg
  name: 'postgres'
  params: {
    location: location
    baseName: prefix
    tags: tags
    useExistingPostgres: useExistingPostgres
    existingPostgresHost: existingPostgresHost
    existingPostgresDatabase: existingPostgresDatabase
    existingPostgresUser: existingPostgresUser
    existingPostgresPassword: existingPostgresPassword
    postgresAdminPassword: postgresAdminPassword
    databaseName: postgresDatabaseName
    principalId: managedIdentity.outputs.principalId
    principalType: 'ServicePrincipal'
  }
}

// ==================== CONTAINER REGISTRY ====================
module containerRegistry 'modules/container-registry.bicep' = {
  scope: rg
  name: 'container-registry'
  params: {
    location: location
    baseName: prefix
    tags: tags
    principalId: managedIdentity.outputs.principalId
  }
}

// ==================== LOG ANALYTICS ====================
module logAnalytics 'modules/log-analytics.bicep' = {
  scope: rg
  name: 'log-analytics'
  params: {
    location: location
    baseName: prefix
    tags: tags
  }
}

// ==================== CONTAINER APPS ENVIRONMENT ====================
module containerAppsEnvironment 'modules/container-apps-environment.bicep' = {
  scope: rg
  name: 'container-apps-environment'
  params: {
    location: location
    baseName: prefix
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.workspaceId
  }
}

// ==================== APPLICATION (Container App) ====================
module application 'modules/application.bicep' = {
  scope: rg
  name: 'application'
  params: {
    location: location
    baseName: prefix
    tags: tags
    containerAppsEnvironmentId: containerAppsEnvironment.outputs.environmentId
    containerRegistryName: containerRegistry.outputs.name
    containerImageName: backendImageName
    userAssignedIdentityResourceId: managedIdentity.outputs.resourceId
    userAssignedIdentityClientId: managedIdentity.outputs.clientId
    openaiEndpoint: resolvedOpenAiEndpoint
    openaiDeploymentName: resolvedOpenAiDeploymentName
    openaiEmbeddingDeploymentName: resolvedOpenAiEmbeddingDeploymentName
    postgresHost: postgres.outputs.host
    postgresDatabase: postgres.outputs.databaseName
    postgresUser: postgres.outputs.username
    postgresPassword: postgres.outputs.password
    aadFrontendClientId: aadFrontendClientId
    aadFrontendTenantId: aadFrontendTenantId
    aadApiTenantId: aadApiTenantId
    aadApiAppId: aadApiAppId
    aadApiAudience: aadApiAudience
    disableAuth: disableAuth
  }
}

// ==================== OUTPUTS FOR AZD ====================
// These outputs are automatically set as environment variables by azd
output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_LOCATION string = location
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name

// Azure OpenAI
output AZURE_OPENAI_ENDPOINT string = resolvedOpenAiEndpoint
output AZURE_OPENAI_CHAT_DEPLOYMENT string = resolvedOpenAiDeploymentName
output AZURE_OPENAI_EMBEDDING_DEPLOYMENT string = resolvedOpenAiEmbeddingDeploymentName

// PostgreSQL
output POSTGRES_HOST string = postgres.outputs.host
output POSTGRES_DATABASE string = postgres.outputs.databaseName
output POSTGRES_USER string = postgres.outputs.username
@secure()
output POSTGRES_PASSWORD string = postgres.outputs.password

// Application
output APPLICATION_URL string = 'https://${application.outputs.fqdn}'
output APPLICATION_NAME string = application.outputs.name

// Managed Identity
output AZURE_CLIENT_ID string = managedIdentity.outputs.clientId
output MANAGED_IDENTITY_RESOURCE_ID string = managedIdentity.outputs.resourceId

// Azure AD
output AAD_FRONTEND_CLIENT_ID string = aadFrontendClientId
output AAD_FRONTEND_TENANT_ID string = aadFrontendTenantId
output AAD_API_TENANT_ID string = aadApiTenantId
output AAD_API_APP_ID string = aadApiAppId
output AAD_API_AUDIENCE string = aadApiAudience
output DISABLE_AUTH string = disableAuth
