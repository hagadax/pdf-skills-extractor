// Creates an Azure App Service Plan for hosting applications

@description('The name of the App Service Plan')
param name string

@description('The location into which the resources should be deployed')
param location string

@description('The App Service Plan SKU')
param sku object = {
  name: 'B1'
}

@description('Indicates whether the App Service Plan should be reserved (Linux)')
param reserved bool = true

@description('Tags to apply to the resource')
param tags object = {}

resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  properties: {
    reserved: reserved
  }
}

output id string = appServicePlan.id
output name string = appServicePlan.name
