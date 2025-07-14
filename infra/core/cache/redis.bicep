// Creates an Azure Cache for Redis for fast in-memory data storage

@description('The name of the Redis Cache')
param name string

@description('The location into which the resources should be deployed')
param location string

@description('The principal ID of the managed identity to grant access')
param managedIdentityPrincipalId string

@description('Tags to apply to the resource')
param tags object = {}

resource redisCache 'Microsoft.Cache/redis@2023-08-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 0
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    redisConfiguration: {
      'maxmemory-policy': 'allkeys-lru'
    }
  }
}

// Grant the managed identity Redis Cache Contributor access
resource redisRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(redisCache.id, managedIdentityPrincipalId, 'Redis Cache Contributor')
  scope: redisCache
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'e0f68234-74aa-48ed-b826-c38b57376e17') // Redis Cache Contributor
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

output id string = redisCache.id
output name string = redisCache.name
output hostName string = redisCache.properties.hostName
output port number = redisCache.properties.port
output sslPort number = redisCache.properties.sslPort
output connectionString string = '${redisCache.properties.hostName}:${redisCache.properties.sslPort},password=${redisCache.listKeys().primaryKey},ssl=True,abortConnect=False'
