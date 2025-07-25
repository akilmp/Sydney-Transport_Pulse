resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
}

output "bucket_name" {
  value = aws_s3_bucket.this.bucket
}
