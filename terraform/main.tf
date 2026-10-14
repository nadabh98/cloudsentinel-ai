terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

variable "project_id" {
  type    = string
  default = "cloudsentinel-ai-511522"
}

variable "region" {
  type    = string
  default = "europe-west9"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "artifacts" {
  name          = "${var.project_id}-artifacts"
  location      = var.region
  force_destroy = true
}

resource "google_bigquery_dataset" "cloudsentinel" {
  dataset_id                 = "cloudsentinel"
  location                   = var.region
  delete_contents_on_destroy = true
}

resource "google_bigquery_table" "predictions" {
  dataset_id          = google_bigquery_dataset.cloudsentinel.dataset_id
  table_id            = "predictions"
  deletion_protection = false

  schema = jsonencode([
    { name = "ts",            type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "cpu",           type = "FLOAT",     mode = "NULLABLE" },
    { name = "memory",        type = "FLOAT",     mode = "NULLABLE" },
    { name = "latency_ms",    type = "FLOAT",     mode = "NULLABLE" },
    { name = "http_errors",   type = "FLOAT",     mode = "NULLABLE" },
    { name = "is_anomaly",    type = "BOOLEAN",   mode = "NULLABLE" },
    { name = "anomaly_score", type = "FLOAT",     mode = "NULLABLE" }
  ])
}

resource "google_pubsub_topic" "metrics_stream" {
  name = "metrics-stream"
}
