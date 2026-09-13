# Google Cloud Run Serverless Blueprint: AI Video Producer Studio

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type    = string
  default = "cineai-studio-prod"
}

variable "region" {
  type    = string
  default = "us-central1"
}

# 1. Cloud Storage Multi-Tenant Air-Gapped Root Bucket
resource "google_storage_bucket" "studio_storage" {
  name          = "cineai-studio-vault-prod"
  location      = "US"
  force_destroy = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# 2. Google Cloud Run Stateless API Service (Autoscales 1 to 200 Replicas)
resource "google_cloud_run_v2_service" "studio_api" {
  name     = "cineai-studio-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 200
    }

    containers {
      image = "gcr.io/${var.project_id}/studio-api:v2.0.0"

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      env {
        name  = "APP_ENV"
        value = "production"
      }
      env {
        name  = "STORAGE_BACKEND"
        value = "gcs"
      }
      env {
        name  = "GCS_BUCKET_NAME"
        value = google_storage_bucket.studio_storage.name
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        period_seconds   = 10
        failure_threshold = 3
      }
    }
  }
}

# 3. Public IAM Ingress Policy
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.studio_api.location
  service  = google_cloud_run_v2_service.studio_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
