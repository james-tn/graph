// Azure OpenAI with conditional deployment (use existing or create new)
param location string
param baseName string
param tags object = {}
param useExistingOpenAI bool
param existingOpenAiEndpoint string = ''
param existingOpenAiDeploymentName string = ''
param existingOpenAiEmbeddingDeploymentName string = ''
param principalId string
param principalType string = 'ServicePrincipal'

// Default deployment names if creating new
var defaultChatDeploymentName = 'gpt-4o'
var defaultEmbeddingDeploymentName = 'text-embedding-3-small'

// Extract resource name from endpoint if using existing
var existingResourceName = useExistingOpenAI ? split(split(existingOpenAiEndpoint, '//')[1], '.')[0] : ''

// Create new Azure OpenAI account (conditional)
resource openaiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = if (!useExistingOpenAI) {
  name: '${baseName}-openai'
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: '${baseName}-openai'
    publicNetworkAccess: 'Enabled'
  }
}

// Reference existing OpenAI account
resource existingOpenaiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = if (useExistingOpenAI) {
  name: existingResourceName
}

// Chat deployment (only if creating new)
resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = if (!useExistingOpenAI) {
  parent: openaiAccount
  name: defaultChatDeploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-08-06'
    }
  }
  sku: {
    name: 'Standard'
    capacity: 50
  }
}

// Embedding deployment (only if creating new)
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = if (!useExistingOpenAI) {
  parent: openaiAccount
  name: defaultEmbeddingDeploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-3-small'
      version: '1'
    }
  }
  sku: {
    name: 'Standard'
    capacity: 100
  }
  dependsOn: [chatDeployment]
}

// Assign Cognitive Services OpenAI User role to managed identity
var cognitiveServicesOpenAIUserRoleId = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'

// Role assignment for new OpenAI account
resource openaiRoleAssignmentNew 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!useExistingOpenAI) {
  scope: openaiAccount
  name: guid(openaiAccount.id, principalId, cognitiveServicesOpenAIUserRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesOpenAIUserRoleId)
    principalId: principalId
    principalType: principalType
  }
}

// Role assignment for existing OpenAI account
resource openaiRoleAssignmentExisting 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (useExistingOpenAI) {
  scope: existingOpenaiAccount
  name: guid(existingOpenaiAccount.id, principalId, cognitiveServicesOpenAIUserRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesOpenAIUserRoleId)
    principalId: principalId
    principalType: principalType
  }
}

output endpoint string = useExistingOpenAI ? existingOpenAiEndpoint : openaiAccount.properties.endpoint
output chatDeploymentName string = useExistingOpenAI ? existingOpenAiDeploymentName : chatDeployment.name
output embeddingDeploymentName string = useExistingOpenAI ? existingOpenAiEmbeddingDeploymentName : embeddingDeployment.name
output accountName string = useExistingOpenAI ? existingResourceName : openaiAccount.name
