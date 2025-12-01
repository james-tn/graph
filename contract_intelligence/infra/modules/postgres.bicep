// PostgreSQL Flexible Server with conditional deployment
param location string
param baseName string
param tags object = {}
param useExistingPostgres bool
param existingPostgresHost string = ''
param existingPostgresDatabase string = ''
param existingPostgresUser string = ''
@secure()
param existingPostgresPassword string = ''
@secure()
param postgresAdminPassword string = ''
param databaseName string = 'cipgraph'
param principalId string
param principalType string = 'ServicePrincipal'

var defaultAdminUsername = 'pgadmin'

// Create new PostgreSQL server (conditional)
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = if (!useExistingPostgres) {
  name: '${baseName}-pgflex'
  location: location
  tags: tags
  sku: {
    name: 'Standard_D2ds_v4'
    tier: 'GeneralPurpose'
  }
  properties: {
    administratorLogin: defaultAdminUsername
    administratorLoginPassword: postgresAdminPassword
    version: '15'
    storage: {
      storageSizeGB: 256
      autoGrow: 'Enabled'
    }
    backup: {
      backupRetentionDays: 14
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
  }
}

// Enable required extensions on new server
resource postgresExtensions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2023-03-01-preview' = if (!useExistingPostgres) {
  parent: postgresServer
  name: 'azure.extensions'
  properties: {
    value: 'vector,pg_trgm,hstore,citext,age'
    source: 'user-override'
  }
}

// Firewall rule to allow Azure services (required for Container Apps)
resource firewallRule 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = if (!useExistingPostgres) {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Create database on new server
resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = if (!useExistingPostgres) {
  parent: postgresServer
  name: databaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Outputs
output host string = useExistingPostgres ? existingPostgresHost : postgresServer.properties.fullyQualifiedDomainName
output databaseName string = useExistingPostgres ? existingPostgresDatabase : databaseName
output username string = useExistingPostgres ? existingPostgresUser : defaultAdminUsername
@secure()
output password string = useExistingPostgres ? existingPostgresPassword : postgresAdminPassword
output serverName string = useExistingPostgres ? split(existingPostgresHost, '.')[0] : postgresServer.name
