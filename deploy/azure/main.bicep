// Azure Container Apps (ACA) Serverless Blueprint: AI Video Producer Studio
param location string = 'eastus'
param environmentName string = 'cineai-studio-env'
param appName string = 'cineai-studio-api'
param containerImage string = 'mcr.microsoft.com/azuredocs/aci-helloworld:latest'
param storageAccountName string = 'cineaistudiostorage'

// 1. Air-Gapped Storage Account for User Containers (user-{user_id})
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_ZRS'
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}

// 2. Azure Container Apps Managed Environment
resource environment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  properties: {
    zoneRedundant: true
  }
}

// 3. Stateless Auto-Scaling FastAPI API Container (Scales 1 to 200 Replicas)
resource apiApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: appName
  location: location
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
      }
    }
    template: {
      containers: [
        {
          name: 'api'
          image: containerImage
          resources: {
            cpu: json('1.0')
            memory: '2.0Gi'
          }
          env: [
            { name: 'APP_ENV', value: 'production' }
            { name: 'STORAGE_BACKEND', value: 'azure' }
            { name: 'AZURE_STORAGE_ACCOUNT', value: storageAccount.name }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 200
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '100'
              }
            }
          }
        ]
      }
    }
  }
}

// 4. KEDA Event-Driven Render Worker (Scales 0 to 500 CPU Replicas, $0 Idle)
resource workerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appName}-worker'
  location: location
  properties: {
    managedEnvironmentId: environment.id
    template: {
      containers: [
        {
          name: 'ffmpeg-worker'
          image: containerImage
          resources: {
            cpu: json('2.0')
            memory: '4.0Gi'
          }
          env: [
            { name: 'STORAGE_BACKEND', value: 'azure' }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 500
        rules: [
          {
            name: 'queue-scaling'
            custom: {
              type: 'azure-servicebus'
              metadata: {
                queueName: 'render-tasks'
                messageCount: '5'
              }
            }
          }
        ]
      }
    }
  }
}
