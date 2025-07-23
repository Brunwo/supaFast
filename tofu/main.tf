# main.tf

terraform {
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

# --- API Enablement ---
# Automatically enable the necessary APIs for the project.
resource "google_project_service" "cloudfunctions_api" {
  service = "cloudfunctions.googleapis.com"
}

resource "google_project_service" "cloudbuild_api" {
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "run_api" {
  service = "run.googleapis.com"
}

resource "google_project_service" "iam_api" {
  service = "iam.googleapis.com"
}

# --- Source Code Packaging ---
# Zip the gcp_function directory for deployment.
data "archive_file" "source" {
  type        = "zip"
  source_dir  = "../gcp_function"
  output_path = "/tmp/gcp_function_source.zip"
}

# --- Cloud Storage for Source Code ---
# A unique bucket to store the zipped source code.
resource "google_storage_bucket" "source_bucket" {
  name          = "${var.project_id}-function-source"
  location      = var.region
  force_destroy = true # Set to false for production environments
}

# Upload the zipped source code to the bucket.
resource "google_storage_bucket_object" "source_archive" {
  name   = "source.zip"
  bucket = google_storage_bucket.source_bucket.name
  source = data.archive_file.source.output_path
}

# --- Google Cloud Function ---
# The Gen 2 Cloud Function resource.
resource "google_cloudfunctions2_function" "protected_endpoint" {
  name     = "protected-endpoint-tf"
  location = var.region

  # Ensure APIs are enabled before creating the function
  depends_on = [
    google_project_service.cloudfunctions_api,
    google_project_service.cloudbuild_api,
    google_project_service.run_api
  ]

  build_config {
    runtime     = "python311"
    entry_point = "protected_endpoint"
    source {
      storage_source {
        bucket = google_storage_bucket.source_bucket.name
        object = google_storage_bucket_object.source_archive.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    min_instance_count = 0
    available_memory   = "256Mi"
    timeout_seconds    = 60
    environment_variables = {
      supa_jwt_secret = var.supa_jwt_secret
    }
    ingress_settings               = "ALLOW_ALL"
    all_traffic_on_latest_revision = true
  }
}

# --- IAM to allow public access ---
# Allow unauthenticated HTTP requests to trigger the function.
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloudfunctions2_function.protected_endpoint.location
  service  = google_cloudfunctions2_function.protected_endpoint.name
  role     = "roles/run.invoker"
  member   = "allUsers"

  # Ensure the function is created before setting IAM
  depends_on = [google_cloudfunctions2_function.protected_endpoint]
}
