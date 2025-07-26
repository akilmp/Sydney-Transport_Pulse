variable "env_name" {
  description = "Name of the MWAA environment"
  type        = string
}

variable "dag_s3_path" {
  description = "S3 path for DAGs"
  type        = string
}

variable "execution_role_arn" {
  description = "IAM role ARN used by MWAA"
  type        = string
}

variable "source_bucket_arn" {
  description = "ARN of the S3 bucket with DAGs"
  type        = string
}

variable "network_subnet_ids" {
  description = "Subnet IDs for MWAA"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security groups for MWAA"
  type        = list(string)
}
