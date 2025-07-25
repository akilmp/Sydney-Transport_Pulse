variable "application_name" {
  description = "Name of the EMR Serverless application"
  type        = string
}

variable "release_label" {
  description = "EMR release label"
  type        = string
  default     = "emr-6.10.0"
}
