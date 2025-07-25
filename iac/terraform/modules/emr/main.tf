resource "aws_emrserverless_application" "this" {
  name          = var.application_name
  release_label = var.release_label
}

output "application_id" {
  value = aws_emrserverless_application.this.id
}
