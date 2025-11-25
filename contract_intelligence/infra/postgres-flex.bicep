@description('Azure region for all resources. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('Globally unique PostgreSQL Flexible Server name (lowercase, 3-63 characters).')
param serverName string

@description('Administrator login name. Avoid the reserved value "azure_superuser".')
param administratorLogin string = 'pgadmin'

@secure()
@description('Administrator password. Store in Azure Key Vault and pass securely via your deployment pipeline.')
param administratorPassword string

@description('PostgreSQL major version supported by Azure Flexible Server (e.g., 15 or 16).')
param postgresVersion string = '16'

@description('SKU name, such as Standard_D4ds_v5 or Standard_D8ds_v5.')
param skuName string = 'Standard_D4ds_v5'

@allowed([
  'Burstable'
  'GeneralPurpose'
  'MemoryOptimized'
])
@description('Compute tier matching the selected SKU.')
param skuTier string = 'GeneralPurpose'

@description('Delegated subnet resource ID used for private access to the flexible server.')
param delegatedSubnetResourceId string = ''

@description('Private DNS zone resource ID linked to the delegated subnet.')
param privateDnsZoneResourceId string = ''

@description('Primary availability zone (1, 2, or 3). Leave empty to deploy without a pinned zone.')
param availabilityZone string = ''

@description('Enable Zone Redundant High Availability when true; otherwise the server deploys without HA.')
param enableHighAvailability bool = false

@description('Storage size in GB (between 32 and 32768).')
param storageSizeGB int = 128

@description('Backup retention in days (7-35).')
param backupRetentionDays int = 7

@description('Logical database name provisioned after the server is created.')
param databaseName string = 'cipgraph'

@description('List of PostgreSQL extensions to enable. Verify availability for your Azure region/SKU.')
param extensions array = [
  'vector'
  'pg_trgm'
  'hstore'
  'citext'
  'age'
]

resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: serverName
  location: location
  sku: {
    name: skuName
    tier: skuTier
  }
  tags: {
    project: 'contract-intelligence'
    component: 'deep-insight-layer'
  }
  properties: {
    version: postgresVersion
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    backup: {
      backupRetentionDays: backupRetentionDays
      geoRedundantBackup: 'Disabled'
    }
    network: empty(delegatedSubnetResourceId) ? {} : {
      delegatedSubnetResourceId: delegatedSubnetResourceId
      privateDnsZoneArmResourceId: privateDnsZoneResourceId
    }
    storage: {
      storageSizeGB: storageSizeGB
    }
    highAvailability: {
      mode: 'Disabled'
    }
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Enabled'
    }
    createMode: 'Create'
    dataEncryption: {
      type: 'SystemManaged'
    }
  }
}

resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresServer
  name: databaseName
  properties: {}
}

output serverFqdn string = postgresServer.properties.fullyQualifiedDomainName
output databaseResourceId string = postgresDatabase.id
