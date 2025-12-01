// Contract Intelligence Application Container App
param location string
param baseName string
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

var appName = '${baseName}-app'

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: appName
  location: location
  tags: tags
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
              name: 'GRAPHRAG_API_KEY'
              value: '' // Will use managed identity
            }
            {
              name: 'GRAPHRAG_API_BASE'
              value: openaiEndpoint
            }
            {
              name: 'GRAPHRAG_API_VERSION'
              value: '2024-02-15-preview'
            }
            {
              name: 'GRAPHRAG_LLM_DEPLOYMENT_NAME'
              value: openaiDeploymentName
            }
            {
              name: 'GRAPHRAG_EMBEDDING_DEPLOYMENT_NAME'
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
