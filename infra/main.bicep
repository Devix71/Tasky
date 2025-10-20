@description('The secret key for signing JWT tokens. MUST be a strong, randomly generated string.')
@secure()
param jwtSecretKey string

@description('The base name for all resources. Must be globally unique.')
param resourceBaseName string = 'taskrem${uniqueString(resourceGroup().id)}'

@description('The Azure region where the resources will be deployed.')
param location string = resourceGroup().location

@description('The administrator username for the SQL server.')
param sqlAdminLogin string = 'sqladmin'

@description('The administrator password for the SQL server. MUST be provided at deployment.')
@secure()
param sqlAdminPassword string

// --- VARIABLES ---

var containerRegistryName = 'cr${uniqueString(resourceGroup().id)}'
var sqlServerName = '${resourceBaseName}-sql'
var sqlDatabaseName = 'taskreminders'
var containerInstanceName = '${resourceBaseName}-aci'

// --- RESOURCES ---

// 1. Azure Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: containerRegistryName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// 2. Azure SQL Server
resource sqlServer 'Microsoft.Sql/servers@2023-02-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: sqlAdminPassword
    version: '12.0'
  }
}

// 2.1 Azure SQL Database
resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-02-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: 'S0'
    tier: 'Standard'
  }
}

// 2.2 Firewall rule to allow access from Azure services
resource sqlFirewallRule 'Microsoft.Sql/servers/firewallRules@2023-02-01-preview' = {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// 3. Azure Container Instance
resource containerInstance 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: containerInstanceName
  location: location
  properties: {
    containers: [
      {
        name: 'task-reminder-api'
        properties: {
          image: '${containerRegistry.name}.azurecr.io/task-reminder-api:latest'
          ports: [
            {
              port: 8000
              protocol: 'TCP'
            }
          ]
          resources: {
            requests: {
              cpu: 1
            memoryInGB: 2
            }
          }
          environmentVariables: [
            {
              name: 'DATABASE_URL'
              #disable-next-line use-secure-value-for-secure-inputs
              secureValue: 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:${sqlServer.name}.database.windows.net,1433;Database=${sqlDatabaseName};Uid=${sqlAdminLogin};Pwd=${sqlAdminPassword};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
            }
            {
               name: 'SECRET_KEY'
               secureValue: jwtSecretKey
            }
          ]
        }
      }
    ]
    osType: 'Linux'
    ipAddress: {
      type: 'Public'
      ports: [
        {
          port: 8000
          protocol: 'TCP'
        }
      ]
    }
    imageRegistryCredentials: [
      {
        server: containerRegistry.properties.loginServer
        username: containerRegistry.name
        password: containerRegistry.listCredentials().passwords[0].value
      }
    ]
  }
  dependsOn: [
    sqlFirewallRule
  ]
}

// --- OUTPUTS ---

@description('The public IP address of the container instance.')
output containerIpAddress string = containerInstance.properties.ipAddress.ip ?? 'IP not available'

@description('Login server for the Azure Container Registry.')
output acrLoginServer string = containerRegistry.properties.loginServer
