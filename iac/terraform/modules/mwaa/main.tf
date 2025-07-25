resource "aws_mwaa_environment" "this" {
  name               = var.env_name
  dag_s3_path        = var.dag_s3_path
  execution_role_arn = var.execution_role_arn

  network_configuration {
    security_group_ids = var.security_group_ids
    subnet_ids         = var.network_subnet_ids
  }
}

output "arn" {
  value = aws_mwaa_environment.this.arn
}
