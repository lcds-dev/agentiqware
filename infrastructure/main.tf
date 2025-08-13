# terraform/main.tf - Infrastructure as Code
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "agentiqware-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  default = "agentiqware-prod"
}

variable "region" {
  default = "us-central1"
}

variable "environment" {
  default = "production"
}

# Firestore Database
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  
  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"
}

# Firestore Indexes
resource "google_firestore_index" "flows_user_created" {
  project    = var.project_id
  database   = google_firestore_database.database.name
  collection = "flows"
  
  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "executions_flow_status" {
  project    = var.project_id
  database   = google_firestore_database.database.name
  collection = "executions"
  
  fields {
    field_path = "flow_id"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "created_at"
    order      = "DESCENDING"
  }
}

# Cloud Storage Buckets
resource "google_storage_bucket" "user_files" {
  name          = "${var.project_id}-user-files"
  location      = var.region
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
  
  cors {
    origin          = ["https://agentiqware.com"]
    method          = ["GET", "POST", "PUT", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket" "flow_templates" {
  name          = "${var.project_id}-flow-templates"
  location      = var.region
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
}

# Cloud Scheduler Jobs
resource "google_cloud_scheduler_job" "cleanup_old_executions" {
  name             = "cleanup-old-executions"
  description      = "Clean up execution logs older than 30 days"
  schedule         = "0 2 * * *"
  time_zone        = "UTC"
  attempt_deadline = "320s"
  
  http_target {
    uri         = "https://us-central1-${var.project_id}.cloudfunctions.net/cleanup_executions"
    http_method = "POST"
    
    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}

# Service Accounts
resource "google_service_account" "app_engine" {
  account_id   = "app-engine-sa"
  display_name = "App Engine Service Account"
}

resource "google_service_account" "cloud_functions" {
  account_id   = "cloud-functions-sa"
  display_name = "Cloud Functions Service Account"
}

resource "google_service_account" "scheduler" {
  account_id   = "scheduler-sa"
  display_name = "Cloud Scheduler Service Account"
}

# IAM Bindings
resource "google_project_iam_member" "app_engine_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.app_engine.email}"
}

resource "google_project_iam_member" "app_engine_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.app_engine.email}"
}

resource "google_project_iam_member" "functions_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_functions.email}"
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "agentiqware-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "agentiqware-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
  
  private_ip_google_access = true
}

# VPC Connector for App Engine
resource "google_vpc_access_connector" "connector" {
  name          = "vpc-connector"
  region        = var.region
  ip_cidr_range = "10.1.0.0/28"
  network       = google_compute_network.vpc.name
  
  min_instances = 2
  max_instances = 10
}

# Cloud Armor Security Policy
resource "google_compute_security_policy" "policy" {
  name = "agentiqware-security-policy"
  
  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["9.9.9.0/24"]
      }
    }
    description = "Deny access to specific IP range"
  }
  
  rule {
    action   = "rate_based_ban"
    priority = "2000"
    
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
      
      ban_duration_sec = 600
    }
    
    description = "Rate limiting rule"
  }
  
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule"
  }
}

# Cloud CDN
resource "google_compute_backend_bucket" "static_content" {
  name        = "agentiqware-static-content"
  bucket_name = google_storage_bucket.static_assets.name
  enable_cdn  = true
  
  cdn_policy {
    cache_mode        = "CACHE_ALL_STATIC"
    client_ttl        = 3600
    default_ttl       = 3600
    max_ttl          = 86400
    negative_caching = true
    
    negative_caching_policy {
      code = 404
      ttl  = 120
    }
  }
}

resource "google_storage_bucket" "static_assets" {
  name          = "${var.project_id}-static-assets"
  location      = var.region
  force_destroy = false
  
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
}

# Monitoring and Alerting
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate Alert"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate exceeds 5%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_function\" AND metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" AND metric.labels.status!=\"ok\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.id]
}

resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification"
  type         = "email"
  
  labels = {
    email_address = "alerts@agentiqware.com"
  }
}

# Outputs
output "app_url" {
  value = "https://${var.project_id}.appspot.com"
}

output "api_url" {
  value = "https://api.agentiqware.com/v1"
}

output "firestore_database" {
  value = google_firestore_database.database.name
}
