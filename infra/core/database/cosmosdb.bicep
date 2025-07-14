// Creates an Azure Cosmos DB account for persistent data storage

@description('The name of the Cosmos DB account')
param name string

@description('The location into which the resources should be deployed')
param location string

@description('The principal ID of the managed identity to grant access')
param managedIdentityPrincipalId string

@description('Tags to apply to the resource')
param tags object = {}

resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: name
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    databaseAccountOfferType: 'Standard'
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-04-15' = {
  parent: cosmosDbAccount
  name: 'skillsdb'
  properties: {
    resource: {
      id: 'skillsdb'
    }
  }
}

resource container 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-04-15' = {
  parent: database
  name: 'skills'
  properties: {
    resource: {
      id: 'skills'
      partitionKey: {
        paths: ['/type']
        kind: 'Hash'
      }
    }
  }
}

// Grant the managed identity Cosmos DB Data Contributor access
resource cosmosRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(cosmosDbAccount.id, managedIdentityPrincipalId, 'Cosmos DB Built-in Data Contributor')
  scope: cosmosDbAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '00000000-0000-0000-0000-000000000002') // Cosmos DB Built-in Data Contributor
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

output id string = cosmosDbAccount.id
output name string = cosmosDbAccount.name
output endpoint string = cosmosDbAccount.properties.documentEndpoint
output connectionString string = cosmosDbAccount.listConnectionStrings().connectionStrings[0].connectionString
