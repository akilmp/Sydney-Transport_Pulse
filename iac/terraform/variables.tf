variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-2"
}

variable "data_lake_bucket" {
  description = "S3 bucket for the data lake"
  type        = string
}

variable "msk_cluster_name" {
  description = "MSK cluster name"
  type        = string
}

variable "kafka_version" {
  description = "Kafka version"
  type        = string
  default     = "3.4.0"
}

variable "broker_instance_type" {
  description = "MSK broker instance type"
  type        = string
  default     = "kafka.m5.large"
}

variable "number_of_broker_nodes" {
  description = "Number of MSK brokers"
  type        = number
  default     = 2
}

variable "subnet_ids" {
  description = "Subnet IDs used for networking"
  type        = list(string)
  default     = []
}

variable "security_group_ids" {
  description = "Security groups for networking"
  type        = list(string)
  default     = []
}

variable "emr_application_name" {
  description = "Name of the EMR Serverless application"
  type        = string
}

variable "mwaa_env_name" {
  description = "MWAA environment name"
  type        = string
}

variable "mwaa_dag_s3_path" {
  description = "S3 path to MWAA DAGs"
  type        = string
}

variable "mwaa_execution_role_arn" {
  description = "IAM role ARN used by MWAA"
  type        = string
}
