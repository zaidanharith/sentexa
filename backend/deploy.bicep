@description('The location where resources will be deployed.')
param location string = resourceGroup().location

@description('Suffix to ensure globally unique names across resources.')
param nameSuffix string = uniqueString(resourceGroup().id)

@description('The name of your existing Azure Container Registry.')
param acrName string = 'sentexaregistry'

@description('The name of the Azure Container Apps environment.')
param environmentName string = 'cae-sentexa-${nameSuffix}'

@description('The name of the FastAPI backend Container App.')
param containerAppName string = 'sentexa-api'

@description('The container image repository name.')
param imageRepository string = 'sentexa-backend'

@description('The CPU cores allocated to the container.')
param cpuCore string = '1.0'

@description('The Memory allocated to the container.')
param memorySize string = '2.0Gi'

@description('The Hugging Face model identifier.')
param hfModel string = 'zaidanharith/sentexa-indobert'

@description('The allowed CORS origins comma-separated.')
param allowedOrigins string = 'https://sentexa.vercel.app,http://localhost:3000'

@description('The container image to deploy.')
param containerImage string = '${acrName}.azurecr.io/${imageRepository}:latest'

@secure()
param databaseUrl string = ''

@secure()
param secretKey string = ''

@secure()
param kaggleUsername string = ''

@secure()
param kaggleKey string = ''

@secure()
param hfToken string = ''

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'log-sentexa-${nameSuffix}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id

    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        transport: 'auto'
      }

      registries: [
        {
          server: '${acr.name}.azurecr.io'
          username: acr.name
          passwordSecretRef: 'registry-password'
        }
      ]

      secrets: [
        {
          name: 'registry-password'
          value: acr.listCredentials().passwords[0].value
        }
        {
          name: 'database-url'
          value: databaseUrl
        }
        {
          name: 'secret-key'
          value: secretKey
        }
        {
          name: 'kaggle-username'
          value: kaggleUsername
        }
        {
          name: 'kaggle-key'
          value: kaggleKey
        }
        {
          name: 'hf-token'
          value: hfToken
        }
      ]
    }

    template: {
      containers: [
        {
          name: 'backend'
          image: containerImage

          resources: {
            cpu: json(cpuCore)
            memory: memorySize
          }

          env: [
            {
              name: 'ENVIRONMENT'
              value: 'production'
            }
            {
              name: 'PORT'
              value: '8000'
            }
            {
              name: 'HOST'
              value: '0.0.0.0'
            }
            {
              name: 'ALLOWED_ORIGINS'
              value: allowedOrigins
            }
            {
              name: 'DATABASE_URL'
              secretRef: 'database-url'
            }
            {
              name: 'SECRET_KEY'
              secretRef: 'secret-key'
            }
            {
              name: 'KAGGLE_USERNAME'
              secretRef: 'kaggle-username'
            }
            {
              name: 'KAGGLE_KEY'
              secretRef: 'kaggle-key'
            }
            {
              name: 'HF_TOKEN'
              secretRef: 'hf-token'
            }
            {
              name: 'HF_MODEL'
              value: hfModel
            }
          ]

          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/api/health'
                port: 8000
              }
              initialDelaySeconds: 30
              periodSeconds: 15
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/api/ready'
                port: 8000
              }
              initialDelaySeconds: 60
              periodSeconds: 15
            }
          ]
        }
      ]

      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-rule'
            custom: {
              type: 'http'
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output acrLoginServer string = '${acr.name}.azurecr.io'
output acrAdminUsername string = acr.name
output fqdn string = containerApp.properties.configuration.ingress.fqdn
