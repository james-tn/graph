// Container Apps Job for nightly hierarchy linker retraining.
//
// Runs `python scripts/retrain_from_reviews.py` against the same image as
// the main app, on a cron schedule (default: 03:17 UTC daily). The job
// inherits managed identity + Postgres + AAD env vars from the main app
// so that retrained model artifacts can be persisted (future: model registry).

@description('Azure region')
param location string

@description('Base name prefix used for all resources')
param baseName string

@description('Common tags to apply')
param tags object = {}

@description('Container Apps environment id')
param containerAppsEnvironmentId string

@description('Azure Container Registry name (used for the registry login)')
param containerRegistryName string

@description('Container image (full path), if empty the job is provisioned but inactive')
param containerImageName string = ''

@description('User-assigned managed identity resource id (for ACR pull + Postgres AAD)')
param userAssignedIdentityResourceId string

@description('User-assigned managed identity client id')
param userAssignedIdentityClientId string

@description('Cron expression (UTC). Default: 03:17 every day')
param cronExpression string = '17 3 * * *'

@description('Whether the schedule trigger is enabled')
param scheduleEnabled bool = true

// Postgres
param postgresHost string
param postgresDatabase string
param postgresUser string
@secure()
param postgresPassword string

// Hierarchy linker config (to keep retrains consistent with serving)
param hierarchyLinkerAutoThreshold string = '0.85'
param hierarchyLinkerReviewThreshold string = '0.60'

@description('Minimum reviewer-confirmed positives required before retraining proceeds')
param retrainMinPositives string = '50'

@description('Whether to skip the job entirely (e.g. when no model is set up yet)')
param enabled bool = true

var jobName = '${baseName}-retrain-job'

resource retrainJob 'Microsoft.App/jobs@2024-03-01' = if (enabled) {
  name: jobName
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
      triggerType: 'Schedule'
      replicaTimeout: 3600 // 1h
      replicaRetryLimit: 1
      scheduleTriggerConfig: {
        cronExpression: cronExpression
        parallelism: 1
        replicaCompletionCount: 1
      }
      registries: !empty(containerImageName) ? [
        {
          server: '${containerRegistryName}.azurecr.io'
          identity: userAssignedIdentityResourceId
        }
      ] : []
      secrets: [
        {
          name: 'postgres-password'
          value: postgresPassword
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'retrain'
          image: !empty(containerImageName) ? containerImageName : 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          command: !empty(containerImageName) ? [
            'python'
          ] : []
          args: !empty(containerImageName) ? [
            'scripts/retrain_from_reviews.py'
            '--min-real-positives'
            retrainMinPositives
          ] : []
          env: [
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
              secretRef: 'postgres-password'
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: userAssignedIdentityClientId
            }
            {
              name: 'AZURE_USE_MANAGED_IDENTITY'
              value: 'true'
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
              name: 'SCHEDULE_ENABLED'
              value: string(scheduleEnabled)
            }
          ]
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
        }
      ]
    }
  }
}

output jobName string = enabled ? retrainJob.name : ''
output jobId string = enabled ? retrainJob.id : ''
