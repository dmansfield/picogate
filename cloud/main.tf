# Terraform configuration to set up providers by version.
terraform {
  required_providers {
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
  }
}

# Configures the provider to use the resource block's specified project for quota checks.
provider "google-beta" {
  user_project_override = true
}

# Configures the provider to not use the resource block's specified project for quota checks.
# This provider should only be used during project creation and initializing services.
provider "google-beta" {
  alias = "no_user_project_override"
  user_project_override = false
}

# 1. Variables
variable "project_id" {
  description = "The unique ID for your new project (e.g., garage-pico-123)"
  type        = string
}

# NOTE: We do NOT attach a billing_account, ensuring this stays on the FREE (Spark) plan.
resource "google_project" "default" {
  provider   = google-beta.no_user_project_override

  name       = "Picogate Garage Door Opener"
  project_id = var.project_id

  # Required for the project to display in any list of Firebase projects.
  labels = {
    "firebase" = "enabled"
  }
}

# Enables required APIs.
resource "google_project_service" "default" {
  provider = google-beta.no_user_project_override
  project  = google_project.default.project_id
  for_each = toset([
    "cloudresourcemanager.googleapis.com",
    "firebase.googleapis.com",
    "firebasedatabase.googleapis.com",
  ])
  service = each.key

  # Don't disable the service if the resource block is removed by accident.
  disable_on_destroy = false
}

# Enables Firebase services for the new project created above.
resource "google_firebase_project" "default" {
  provider = google-beta
  project  = google_project.default.project_id

  # Waits for the required APIs to be enabled.
  depends_on = [
    google_project_service.default
  ]
}

# 6. Create the Realtime Database Instance
resource "google_firebase_database_instance" "default" {
  provider    = google-beta
  project     = google_firebase_project.default.project
  region      = "us-central1"
  instance_id = "${var.project_id}-default-rtdb" # Custom name for the DB
  type        = "DEFAULT_DATABASE"
  
  depends_on = [
    google_project_service.default
  ]
}

# 7. Output the Database URL (You need this for your Pico W code!)
output "database_url" {
  value = google_firebase_database_instance.default.database_url
}
