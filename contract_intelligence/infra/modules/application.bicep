// Contract Intelligence Application Container App
param location string
param name string
param tags object = {}
param containerAppsEnvironmentId string
param containerRegistryName string
param containerImageName string = ''
param userAssignedIdentityResourceId string
param userAssignedIdentityClientId string

// Azure OpenAI
param openaiEndpoint string
param openaiDeploymentName string
param openaiEmbeddingDeploymentName string

// PostgreSQL
param postgresHost string
param postgresDatabase string
param postgresUser string
@secure()
param postgresPassword string

// AAD Authentication
param aadFrontendClientId string
param aadFrontendTenantId string
param aadApiTenantId string
param aadApiAppId string
param aadApiAudience string
param disableAuth string

// ML hierarchy linker (Phase-1 ML-assisted parent matching)
@allowed([
  'auto'
  'on'
  'off'
])
param hierarchyLinkerEnabled string = 'auto'
param hierarchyLinkerAutoThreshold string = '0.85'
param hierarchyLinkerReviewThreshold string = '0.60'
@allowed([
  'true'
  'false'
])
param hierarchyLinkerShadowMode string = 'false'

var appName = name

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: appName
  location: location
  // azd locates the deploy target by the `azd-service-name` tag (matched
  // against services.<name> in azure.yaml). Without it, `azd deploy backend`
  // can't find the Container App and fails with
  // "parameter containerAppName cannot be empty".
  tags: union(tags, {
    'azd-service-name': 'backend'
  })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityResourceId}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: '${containerRegistryName}.azurecr.io'
          identity: userAssignedIdentityResourceId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: !empty(containerImageName) ? containerImageName : 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          env: [
            // Azure OpenAI
            {
              name: 'AZURE_OPENAI_API_KEY'
              value: '' // Will use managed identity
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openaiEndpoint
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT_NAME'
              value: openaiDeploymentName
            }
            {
              name: 'EMBEDDING_DEPLOYMENT_NAME'
              value: openaiEmbeddingDeploymentName
            }
            // PostgreSQL
            {
              name: 'POSTGRES_HOST'
              value: postgresHost
            }
            {
              name: 'POSTGRES_DATABASE'
              value: postgresDatabase
            }
            {
              name: 'POSTGRES_USER'
              value: postgresUser
            }
            {
              name: 'POSTGRES_ADMIN_PASSWORD'
              value: postgresPassword
            }
            // Azure Managed Identity
            {
              name: 'AZURE_CLIENT_ID'
              value: userAssignedIdentityClientId
            }
            {
              name: 'AZURE_USE_MANAGED_IDENTITY'
              value: 'true'
            }
            // Azure AD Authentication
            {
              name: 'AAD_FRONTEND_CLIENT_ID'
              value: aadFrontendClientId
            }
            {
              name: 'AAD_FRONTEND_TENANT_ID'
              value: aadFrontendTenantId
            }
            {
              name: 'AAD_API_TENANT_ID'
              value: aadApiTenantId
            }
            {
              name: 'AAD_API_APP_ID'
              value: aadApiAppId
            }
            {
              name: 'AAD_API_AUDIENCE'
              value: aadApiAudience
            }
            {
              name: 'DISABLE_AUTH'
              value: disableAuth
            }
            // ML hierarchy linker
            {
              name: 'HIERARCHY_LINKER_ENABLED'
              value: hierarchyLinkerEnabled
            }
            {
              name: 'HIERARCHY_LINKER_AUTO_THRESHOLD'
              value: hierarchyLinkerAutoThreshold
            }
            {
              name: 'HIERARCHY_LINKER_REVIEW_THRESHOLD'
              value: hierarchyLinkerReviewThreshold
            }
            {
              name: 'HIERARCHY_LINKER_SHADOW_MODE'
              value: hierarchyLinkerShadowMode
            }
          ]
          resources: {
            cpu: json('2.0')
            memory: '4Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output fqdn string = containerApp.properties.configuration.ingress.fqdn
output name string = containerApp.name
output url string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
