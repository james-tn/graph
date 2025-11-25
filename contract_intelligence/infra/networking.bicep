@description('Azure region for networking resources')
param location string

@description('Base name applied to networking resources')
param baseName string

@description('Environment suffix for resource names')
param environmentName string

@description('Tags propagated to networking resources')
param tags object = {}

@description('Address space for the virtual network')
param addressPrefix string = '10.20.0.0/16'

@description('Subnet CIDR for the PostgreSQL delegated subnet')
param postgresSubnetPrefix string = '10.20.1.0/24'

@description('Subnet CIDR for private endpoints (e.g., monitoring, future services)')
param privateEndpointSubnetPrefix string = '10.20.2.0/24'

var vnetName = '${baseName}-${environmentName}-vnet'
var postgresSubnetName = 'postgres-delegated'
var privateEndpointSubnetName = 'private-endpoints'
var dnsZoneName = 'privatelink.postgres.database.azure.com'
var dnsLinkName = '${vnetName}-postgres-link'

resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: vnetName
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      {
        name: postgresSubnetName
        properties: {
          addressPrefix: postgresSubnetPrefix
          privateEndpointNetworkPolicies: 'Disabled'
          privateLinkServiceNetworkPolicies: 'Disabled'
          delegations: [
            {
              name: 'flexibleservers'
              properties: {
                serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
              }
            }
          ]
        }
      }
      {
        name: privateEndpointSubnetName
        properties: {
          addressPrefix: privateEndpointSubnetPrefix
          privateEndpointNetworkPolicies: 'Disabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
    ]
  }
}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2018-09-01' = {
  name: dnsZoneName
  location: 'global'
  tags: tags
}

resource privateDnsZoneLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2018-09-01' = {
  parent: privateDnsZone
  name: dnsLinkName
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnet.id
    }
  }
}

output vnetId string = vnet.id
output delegatedSubnetId string = vnet.properties.subnets[0].id
output privateEndpointSubnetId string = vnet.properties.subnets[1].id
output privateDnsZoneId string = privateDnsZone.id
