// Creates an Azure App Service for hosting web applications

@description('The name of the App Service')
param name string

@description('The location into which the resources should be deployed')
param location string

@description('The resource ID of the App Service Plan')
param appServicePlanId string

@description('The runtime name (e.g., python, node)')
param runtimeName string

@description('The runtime version (e.g., 3.11, 18)')
param runtimeVersion string

@description('Application settings for the App Service')
param appSettings object = {}

@description('The name of the Key Vault for storing secrets')
param keyVaultName string = ''

@description('The principal ID of the managed identity')
param managedIdentity string = ''

@description('Tags to apply to the resource')
param tags object = {}

var linuxFxVersion = '${runtimeName}|${runtimeVersion}'

resource appService 'Microsoft.Web/sites@2024-04-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlanId
    reserved: true
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: linuxFxVersion
      alwaysOn: true
      appSettings: [for key in items(appSettings): {
        name: key.key
        value: key.value
      }]
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
      }
    }
  }
}

output id string = appService.id
output name string = appService.name
output uri string = 'https://${appService.properties.defaultHostName}'
output identityPrincipalId string = managedIdentity
