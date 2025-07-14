// Main infrastructure file for PDF Skills Extractor
// This template creates an App Service Plan and App Service with supporting resources

targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// Optional parameters for environment variables
@secure()
@description('Secret key for Flask application')
param secretKey string = ''

@description('Upload folder path')
param uploadFolder string = 'uploads'

@description('Maximum content length in bytes')
param maxContentLength string = '16777216'

// Generate a unique token for resource naming
var resourceToken = toLower(uniqueString(subscription().id, resourceGroup().id, environmentName))
var tags = {
  'azd-env-name': environmentName
}

// Core infrastructure modules
module appServicePlan 'core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  params: {
    name: 'plan-${resourceToken}'
    location: location
    tags: tags
    sku: {
      name: 'B1'
    }
    reserved: true  // Linux App Service Plan
  }
}

module appService 'core/host/appservice.bicep' = {
  name: 'appservice'
  params: {
    name: 'app-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'web' })
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.11'
    appSettings: {
      SECRET_KEY: secretKey
      UPLOAD_FOLDER: uploadFolder
      MAX_CONTENT_LENGTH: maxContentLength
      SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
      WEBSITE_HTTPLOGGING_RETENTION_DAYS: '1'
      APPINSIGHTS_INSTRUMENTATIONKEY: applicationInsights.outputs.instrumentationKey
      APPLICATIONINSIGHTS_CONNECTION_STRING: applicationInsights.outputs.connectionString
      ApplicationInsightsAgent_EXTENSION_VERSION: '~3'
      AZURE_STORAGE_CONNECTION_STRING: storageAccount.outputs.connectionString
      AZURE_STORAGE_CONTAINER_NAME: 'uploads'
    }
    keyVaultName: keyVault.outputs.name
    managedIdentity: managedIdentity.outputs.managedIdentityId
  }
}

module managedIdentity 'core/security/managedidentity.bicep' = {
  name: 'managedidentity'
  params: {
    name: 'mi-${resourceToken}'
    location: location
    tags: tags
  }
}

module keyVault 'core/security/keyvault.bicep' = {
  name: 'keyvault'
  params: {
    name: 'kv-${resourceToken}'
    location: location
    tags: tags
    managedIdentityPrincipalId: managedIdentity.outputs.managedIdentityPrincipalId
  }
}

module applicationInsights 'core/monitor/applicationinsights.bicep' = {
  name: 'applicationinsights'
  params: {
    name: 'appi-${resourceToken}'
    location: location
    tags: tags
  }
}

module storageAccount 'core/storage/storageaccount.bicep' = {
  name: 'storageaccount'
  params: {
    name: 'st${resourceToken}'
    location: location
    tags: tags
    managedIdentityPrincipalId: managedIdentity.outputs.managedIdentityPrincipalId
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.uri
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name
output AZURE_STORAGE_CONNECTION_STRING string = storageAccount.outputs.connectionString
output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = managedIdentity.outputs.managedIdentityPrincipalId
output SERVICE_WEB_NAME string = appService.outputs.name
output SERVICE_WEB_URI string = appService.outputs.uri
output RESOURCE_GROUP_ID string = resourceGroup().id
