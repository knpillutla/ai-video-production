# Cloudflare Multi-Cloud Health Check & Automatic Load Balancer Failover
# Automates 15-second Anycast DNS failover between Azure ACA and GCP Cloud Run

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

variable "cloudflare_zone_id" {
  type        = string
  description = "Cloudflare DNS Zone ID"
  default     = "023e105f4ecef8ad9ca31a8372d0c353"
}

variable "domain_name" {
  type        = string
  description = "Production API Domain"
  default     = "studio.cineai.io"
}

# 1. Health Monitor: Pings /health every 15s with 5s timeout
resource "cloudflare_load_balancer_monitor" "api_health" {
  account_id     = var.cloudflare_zone_id
  type           = "http"
  method         = "GET"
  path           = "/health"
  port           = 443
  timeout        = 5
  interval       = 15
  retries        = 2
  expected_codes = "200"
  follow_redirects = false
  description    = "Stateless API Health Monitor across Clouds"
}

# 2. Azure Container Apps Origin Pool (Primary)
resource "cloudflare_load_balancer_pool" "azure_pool" {
  account_id = var.cloudflare_zone_id
  name       = "azure-primary-pool"
  origins {
    name    = "azure-aca"
    address = "cineai-studio-api.eastus.azurecontainer.io"
    enabled = true
    weight  = 1.0
  }
  monitor     = cloudflare_load_balancer_monitor.api_health.id
  description = "Azure Container Apps Primary Cluster"
}

# 3. Google Cloud Run Origin Pool (Secondary / Failover)
resource "cloudflare_load_balancer_pool" "gcp_pool" {
  account_id = var.cloudflare_zone_id
  name       = "gcp-failover-pool"
  origins {
    name    = "gcp-cloud-run"
    address = "cineai-studio-api-us-central1.run.app"
    enabled = true
    weight  = 1.0
  }
  monitor     = cloudflare_load_balancer_monitor.api_health.id
  description = "Google Cloud Run Failover Cluster"
}

# 4. Global Anycast Load Balancer with Automatic Failover
resource "cloudflare_load_balancer" "global_lb" {
  zone_id          = var.cloudflare_zone_id
  name             = var.domain_name
  fallback_pool_id = cloudflare_load_balancer_pool.gcp_pool.id
  default_pool_ids = [
    cloudflare_load_balancer_pool.azure_pool.id,
    cloudflare_load_balancer_pool.gcp_pool.id
  ]
  proxied          = true
  steering_policy  = "off" # Strict active-passive failover
  session_affinity = "none"
  description      = "Active-Passive Zero-Downtime Cross-Cloud Failover"
}
