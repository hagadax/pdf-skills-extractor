// Creates a Log Analytics workspace for monitoring and logging

@description('The name of the Log Analytics workspace')
param name string

@description('The location into which the resources should be deployed')
param location string

@description('Tags to apply to the resource')
param tags object = {}

@description('The retention period in days')
param retentionInDays int = 30

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    retentionInDays: retentionInDays
    sku: {
      name: 'PerGB2018'
    }
  }
}

output id string = logAnalyticsWorkspace.id
output name string = logAnalyticsWorkspace.name
output customerId string = logAnalyticsWorkspace.properties.customerId
