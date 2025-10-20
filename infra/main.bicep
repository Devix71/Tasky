// ===================================================================================
// PARAMETERS
// ===================================================================================
@description('The tag for the container image to deploy.')
param containerImageTag string = 'latest'

@description('The secret key for signing JWT tokens.')
@secure()
param jwtSecretKey string

@description('The administrator username for the SQL server.')
param sqlAdminLogin string = 'sqladmin'

@description('The administrator password for the SQL server.')
@secure()
param sqlAdminPassword string

@description('The base64 encoded data of the PFX certificate for the Application Gateway.')
@secure()
param appGatewayCertificateData string

@description('The password for the PFX certificate.')
@secure()
param appGatewayCertificatePassword string

@description('The base name for all resources. Must be globally unique.')
param resourceBaseName string = 'taskrem${uniqueString(resourceGroup().id)}'

@description('The Azure region where the resources will be deployed.')
param location string = resourceGroup().location


// ===================================================================================
// VARIABLES
// ===================================================================================
var containerRegistryName = 'cr${uniqueString(resourceGroup().id)}'
var sqlServerName = '${resourceBaseName}-sql'
var sqlDatabaseName = 'taskreminders'
var containerInstanceName = '${resourceBaseName}-aci'
var virtualNetworkName = '${resourceBaseName}-vnet'
var appGatewaySubnetName = 'AppGatewaySubnet'
var containerSubnetName = 'ContainerSubnet'
var publicIpName = '${resourceBaseName}-pip'
var appGatewayName = '${resourceBaseName}-agw'


// ===================================================================================
// RESOURCES
// ===================================================================================

// --- 1. Azure Container Registry ---
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: containerRegistryName
  location: location
  sku: { name: 'Basic' }
  properties: { adminUserEnabled: true }
}

// --- 2. Azure SQL Server and Database ---
resource sqlServer 'Microsoft.Sql/servers@2023-02-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: sqlAdminPassword
    version: '12.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-02-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: { name: 'S0', tier: 'Standard' }
}

resource sqlFirewallRule 'Microsoft.Sql/servers/firewallRules@2023-02-01-preview' = {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: { startIpAddress: '0.0.0.0', endIpAddress: '0.0.0.0' }
}


// --- 3. Networking Resources ---
resource virtualNetwork 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: virtualNetworkName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [ '10.0.0.0/16' ]
    }
  }
}

resource appGatewaySubnet 'Microsoft.Network/virtualNetworks/subnets@2023-05-01' = {
  parent: virtualNetwork
  name: appGatewaySubnetName
  properties: {
    addressPrefix: '10.0.1.0/24'
  }
}

resource containerSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-05-01' = {
  parent: virtualNetwork
  name: containerSubnetName
  properties: {
    addressPrefix: '10.0.2.0/24'
    delegations: [
      {
        name: 'aciDelegation'
        properties: {
          serviceName: 'Microsoft.ContainerInstance/containerGroups'
        }
      }
    ]
    serviceEndpoints: [
      {
        service: 'Microsoft.ContainerRegistry'
      }
    ]
  }
}

resource publicIp 'Microsoft.Network/publicIPAddresses@2023-05-01' = {
  name: publicIpName
  location: location
  sku: { name: 'Standard' }
  properties: {
    publicIPAllocationMethod: 'Static'
    dnsSettings: {
      domainNameLabel: resourceBaseName
    }
  }
}


// --- 4. Azure Container Instance (Private) ---
resource containerInstance 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: containerInstanceName
  location: location
  properties: {
    containers: [
      {
        name: 'task-reminder-api'
        properties: {
          image: '${containerRegistry.name}.azurecr.io/task-reminder-api:${containerImageTag}'
          ports: [ { port: 8000, protocol: 'TCP' } ]
          resources: { requests: { cpu: 1, memoryInGB: 2 } }
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
    subnetIds: [
      {
        id: containerSubnet.id
      }
    ]
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


// --- 5. Application Gateway ---
resource applicationGateway 'Microsoft.Network/applicationGateways@2023-05-01' = {
  name: appGatewayName
  location: location
  properties: {
    sku: { name: 'Standard_v2', tier: 'Standard_v2' }
    frontendIPConfigurations: [
      {
        name: 'appGatewayFrontendIP'
        properties: {
          publicIPAddress: { id: publicIp.id }
        }
      }
    ]
    frontendPorts: [
      {
        name: 'port_443'
        properties: { port: 443 }
      }
    ]
    backendAddressPools: [
      {
        name: 'aciBackendPool'
        properties: {
          backendAddresses: [
            {
              ipAddress: containerInstance.properties.ipAddress.ip
            }
          ]
        }
      }
    ]
    backendHttpSettingsCollection: [
      {
        name: 'aciHttpSettings'
        properties: {
          port: 8000
          protocol: 'Http'
          cookieBasedAffinity: 'Disabled'
          requestTimeout: 20
          probe: {
            id: resourceId('Microsoft.Network/applicationGateways/probes', appGatewayName, 'aciHealthProbe')
          }
        }
      }
    ]
    httpListeners: [
      {
        name: 'httpsListener'
        properties: {
          frontendIPConfiguration: { id: resourceId('Microsoft.Network/applicationGateways/frontendIPConfigurations', appGatewayName, 'appGatewayFrontendIP') }
          frontendPort: { id: resourceId('Microsoft.Network/applicationGateways/frontendPorts', appGatewayName, 'port_443') }
          protocol: 'Https'
          sslCertificate: { id: resourceId('Microsoft.Network/applicationGateways/sslCertificates', appGatewayName, 'selfSignedCert') }
        }
      }
    ]
    requestRoutingRules: [
      {
        name: 'routingRule'
        properties: {
          ruleType: 'Basic'
          httpListener: { id: resourceId('Microsoft.Network/applicationGateways/httpListeners', appGatewayName, 'httpsListener') }
          backendAddressPool: { id: resourceId('Microsoft.Network/applicationGateways/backendAddressPools', appGatewayName, 'aciBackendPool') }
          backendHttpSettings: { id: resourceId('Microsoft.Network/applicationGateways/backendHttpSettingsCollection', appGatewayName, 'aciHttpSettings') }
        }
      }
    ]
    probes: [
      {
        name: 'aciHealthProbe'
        properties: {
          protocol: 'Http'
          host: containerInstance.properties.ipAddress.ip
          path: '/docs'
          interval: 30
          timeout: 10
          unhealthyThreshold: 3
        }
      }
    ]
    sslCertificates: [
      {
        name: 'selfSignedCert'
        properties: {
          data: appGatewayCertificateData
          password: appGatewayCertificatePassword
        }
      }
    ]
  }
}


// ===================================================================================
// OUTPUTS
// ===================================================================================

@description('The public FQDN of the Application Gateway. This is your new HTTPS endpoint.')
output applicationGatewayFqdn string = publicIp.properties.dnsSettings.fqdn

@description('Login server for the Azure Container Registry.')
output acrLoginServer string = containerRegistry.properties.loginServer
