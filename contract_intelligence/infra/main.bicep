@description('Azure region for all resources. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('Base name applied to networking resources (e.g., "contract-intel").')
param baseName string

@description('Environment suffix for resource names (e.g., "dev", "prod").')
param environmentName string

@description('Global tags propagated to all resources.')
param tags object = {}

@description('Globally unique PostgreSQL Flexible Server name.')
param serverName string = toLower('${baseName}-${environmentName}-pgflex')

@description('Administrator login name for PostgreSQL.')
param administratorLogin string = 'pgadmin'

@secure()
@description('Administrator password for PostgreSQL.')
param administratorPassword string

@description('Optional availability zone (1, 2, or 3).')
param availabilityZone string = '1'

@description('Enable Zone Redundant High Availability when true.')
param enableHighAvailability bool = true

@description('Storage size in GB (32 - 32768).')
param storageSizeGB int = 256

@description('Backup retention in days (7 - 35).')
param backupRetentionDays int = 14

@description('Logical database name to create after the server is provisioned.')
param databaseName string = 'cipgraph'

@description('List of PostgreSQL extensions to enable.')
param extensions array = [
  'pgvector'
  'pg_trgm'
  'hstore'
  'citext'
  'age'
]

@description('Enable public network access for PostgreSQL server (for dev/testing).')
param enablePublicAccess bool = false

module networking 'networking.bicep' = if (!enablePublicAccess) {
  name: 'networking'
  params: {
    location: location
    baseName: baseName
    environmentName: environmentName
    tags: tags
  }
}

module postgres 'postgres-flex.bicep' = {
  name: 'postgresFlexibleServer'
  params: {
    location: location
    serverName: serverName
    administratorLogin: administratorLogin
    administratorPassword: administratorPassword
    delegatedSubnetResourceId: ''
    privateDnsZoneResourceId: ''
    availabilityZone: availabilityZone
    enableHighAvailability: enableHighAvailability
    storageSizeGB: storageSizeGB
    backupRetentionDays: backupRetentionDays
    databaseName: databaseName
    extensions: extensions
  }
}

output serverFqdn string = postgres.outputs.serverFqdn
output databaseResourceId string = postgres.outputs.databaseResourceId
output delegatedSubnetId string = ''
output privateDnsZoneId string = ''
