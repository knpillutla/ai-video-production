# Azure Container Apps (ACA) Serverless Terraform Blueprint: AI Video Producer Studio
# Terraform-only infrastructure for Azure multi-tenant studio deployment

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "location" {
  type    = string
  default = "eastus"
}

variable "resource_group_name" {
  type    = string
  default = "rg-cineai-studio-prod"
}

variable "environment_name" {
  type    = string
  default = "cineai-studio-env"
}

variable "app_name" {
  type    = string
  default = "cineai-studio-api"
}

# 1. Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# 2. Air-Gapped Storage Account for User Containers (user-{user_id})
resource "azurerm_storage_account" "storage" {
  name                     = "cineaistudiostorage"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  min_tls_version          = "TLS1_2"
  allow_nested_items_to_be_public = false
}

# 3. Azure Container Apps Managed Environment
resource "azurerm_container_app_environment" "env" {
  name                = var.environment_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# 4. Stateless Auto-Scaling FastAPI API Container (Scales 1 to 200 Replicas)
resource "azurerm_container_app" "api" {
  name                         = var.app_name
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    min_replicas = 1
    max_replicas = 200

    container {
      name   = "api"
      image  = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
      cpu    = 1.0
      memory = "2.0Gi"

      env {
        name  = "APP_ENV"
        value = "production"
      }
      env {
        name  = "STORAGE_BACKEND"
        value = "azure"
      }
      env {
        name  = "AZURE_STORAGE_ACCOUNT"
        value = azurerm_storage_account.storage.name
      }
    }

    http_scale_rule {
      name                = "http-scaling"
      concurrent_requests = "100"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

# 5. KEDA Event-Driven Render Worker (Scales 0 to 500 CPU Replicas, $0 Idle)
resource "azurerm_container_app" "worker" {
  name                         = "${var.app_name}-worker"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    min_replicas = 0 # Scale-to-zero when queue is empty ($0 idle cost)
    max_replicas = 500

    container {
      name   = "ffmpeg-worker"
      image  = "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
      cpu    = 2.0
      memory = "4.0Gi"

      env {
        name  = "STORAGE_BACKEND"
        value = "azure"
      }
    }

    custom_scale_rule {
      name             = "queue-scaling"
      custom_rule_type = "azure-servicebus"
      metadata = {
        queueName    = "render-tasks"
        messageCount = "5"
      }
    }
  }
}
