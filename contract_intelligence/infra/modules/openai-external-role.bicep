// Assigns Cognitive Services OpenAI User role to an existing Azure OpenAI account in this resource group
// targetScope is resource group because the OpenAI account lives here
targetScope = 'resourceGroup'

param accountName string
param cognitiveServicesOpenAIUserRoleId string
param principalId string
param principalType string
param roleAssignmentName string

resource existingOpenaiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: accountName
}

resource openaiRoleAssignmentExternal 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: existingOpenaiAccount
  name: roleAssignmentName
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesOpenAIUserRoleId)
    principalId: principalId
    principalType: principalType
  }
}
